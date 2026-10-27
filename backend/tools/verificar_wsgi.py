"""Comprueba Gunicorn en loopback dentro de contenedor efímero; no publica puertos."""

import json
import os
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


opener = build_opener(NoRedirect)
environment = {
    **os.environ,
    "DJANGO_SETTINGS_MODULE": "config.settings.production",
    "TRUSTED_TLS_PROXY": "true",
}
process = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "gunicorn",
        "config.wsgi:application",
        "--bind",
        "127.0.0.1:8011",
        "--workers",
        "2",
        "--threads",
        "2",
    ],
    env=environment,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


def request(path, tls=False):
    headers = {"X-Forwarded-Proto": "https"} if tls else {}
    try:
        response = opener.open(Request(f"http://127.0.0.1:8011{path}", headers=headers), timeout=4)
    except HTTPError as error:
        response = error
    with response:
        return response.code


try:
    for attempt in range(40):
        try:
            redirect = request("/api/v1/health/live/")
            break
        except URLError:
            time.sleep(0.25)
    else:
        raise RuntimeError("Gunicorn no inició dentro del plazo local.")
    live = request("/api/v1/health/live/", tls=True)
    readiness = request("/api/v1/health/", tls=True)
    assert redirect == 301 and live == 200
    # PostgreSQL local no tiene TLS/CA de cloud: fallo cerrado esperado con verify-full.
    assert readiness == 503
    print(
        json.dumps(
            {
                "gunicorn_http_redirect": redirect,
                "liveness_proxy_local": live,
                "readiness_sin_tls_postgresql": readiness,
                "limite": (
                    "No verifica TLS real, proxy externo ni conexión cloud. Solo loopback efímero."
                ),
            }
        )
    )
finally:
    process.terminate()
    process.wait(timeout=15)
