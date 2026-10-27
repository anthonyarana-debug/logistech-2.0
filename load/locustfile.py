"""Carga F5 limitada: solo loopback, tokens de fixtures, permisos y límites intactos."""

import csv
import itertools
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import gevent
from locust import HttpUser, between, events, task
from locust.exception import StopUser

manifest = json.loads(Path(os.environ["F5_MANIFEST"]).read_text(encoding="utf-8"))
sequence = itertools.count()
phase = "warmup"
codes = {"warmup": Counter(), "measurement": Counter()}
auth_events = Counter()
authenticated = 0
peak = 0
samples = []
timeline = []
measurement_start = None
warmup = float(os.environ.get("F5_WARMUP", "30"))
summary_path = Path(os.environ["F5_SUMMARY"])


@events.test_start.add_listener
def begin(environment, **kwargs):
    target = urlsplit(environment.host)
    if (
        (target.scheme, target.hostname, target.port, target.path)
        != ("http", "127.0.0.1", 8001, "")
        or target.query
        or target.fragment
    ):
        raise RuntimeError("Carga permitida únicamente sobre http://127.0.0.1:8001")

    def measure():
        global phase, measurement_start
        environment.stats.reset_all()
        measurement_start = time.monotonic()
        phase = "measurement"

    def sample():
        while environment.runner.state not in ("stopped", "stopping", "cleanup"):
            if phase == "measurement":
                samples.append(authenticated)
                timeline.append(
                    [
                        time.monotonic() - measurement_start,
                        authenticated,
                        environment.stats.total.num_requests,
                        environment.stats.total.num_failures,
                    ]
                )
            gevent.sleep(1)

    gevent.spawn_later(warmup, measure)
    gevent.spawn(sample)


@events.request.add_listener
def classify(
    request_type, name, response_time, response_length, response=None, exception=None, **kwargs
):
    status = str(response.status_code) if response is not None else "network"
    codes[phase][status] += 1
    if name in ("login controlado", "logout controlado"):
        auth_events[f"{name}:HTTP {status}"] += 1


@events.test_stop.add_listener
def finish(environment, **kwargs):
    duration = time.monotonic() - measurement_start if measurement_start else 0
    total = environment.stats.total
    with summary_path.with_name(summary_path.stem.replace("_summary", "_final") + ".csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "name", "requests", "failures", "mean_ms", "p95_ms"])
        for item in [*environment.stats.entries.values(), total]:
            writer.writerow(
                [
                    item.method,
                    item.name,
                    item.num_requests,
                    item.num_failures,
                    item.avg_response_time,
                    item.get_response_time_percentile(0.95),
                ]
            )
    with summary_path.with_name(summary_path.stem.replace("_summary", "_timeline") + ".csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(["measurement_seconds", "authenticated_users", "requests", "failures"])
        writer.writerows(timeline)
    summary_path.write_text(
        json.dumps(
            {
                "fecha_utc": datetime.now(timezone.utc).isoformat(),
                "namespace": manifest["namespace"],
                "target": environment.host,
                "usuarios_configurados": environment.parsed_options.num_users,
                "usuarios_autenticados_pico": peak,
                "usuarios_medicion_min": min(samples) if samples else 0,
                "usuarios_medicion_max": max(samples) if samples else 0,
                "spawn_rate": environment.parsed_options.spawn_rate,
                "calentamiento_segundos": warmup,
                "medicion_segundos_reales": duration,
                "solicitudes": total.num_requests,
                "fallos": total.num_failures,
                "fallos_porcentaje": 100 * total.fail_ratio,
                "rps": total.num_requests / duration if duration else 0,
                "latencia_media_ms": total.avg_response_time,
                "p95_ms": total.get_response_time_percentile(0.95),
                "http_calentamiento": dict(codes["warmup"]),
                "http_medicion": dict(codes["measurement"]),
                "auth_http": dict(auth_events),
                "usuarios_autenticados_muestras_1s": samples,
                "autenticacion": (
                    "1 login HTTP por ejecución; demás usuarios JWT de fixtures, TTL sin cambio"
                ),
                "limite_escrituras": "1 POST y 1 PATCH de caja por usuario como máximo",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


class InventoryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        global authenticated, peak
        index = next(sequence)
        if index >= len(manifest["users"]):
            raise StopUser()
        self.account = manifest["users"][index]
        self.client.trust_env = False
        self.box_id = None
        self.patched = False
        self.attempted_create = False
        self.counted = False
        self.csrf = None
        token = self.account["access"]
        if self.account["password"]:
            result = self.call("GET", "/api/v1/auth/csrf/", "csrf", 200)
            if result is None:
                raise StopUser()
            self.csrf = result["csrfToken"]
            result = self.call(
                "POST",
                "/api/v1/auth/login/",
                "login controlado",
                200,
                json={"email": self.account["email"], "password": self.account["password"]},
                headers={"X-CSRFToken": self.csrf},
            )
            if result is None:
                raise StopUser()
            token = result["access"]
        self.client.headers["Authorization"] = f"Bearer {token}"
        if self.call("GET", "/api/v1/auth/me/", "identidad autorizada") is None:
            raise StopUser()
        authenticated += 1
        peak = max(peak, authenticated)
        self.counted = True

    def call(self, method, path, name, expected=200, **kwargs):
        with self.client.request(
            method, path, name=name, timeout=8, allow_redirects=False, catch_response=True, **kwargs
        ) as response:
            if response.status_code != expected:
                response.failure(f"HTTP {response.status_code}")
                return None
            response.success()
            if response.status_code == 204:
                return {}
            return response.json()

    @task(7)
    def boxes(self):
        self.call("GET", "/api/v1/boxes/", "cajas: lista")

    @task(3)
    def categories(self):
        self.call("GET", "/api/v1/categories/", "categorias: lista")

    @task(3)
    def search(self):
        self.call(
            "GET",
            "/api/v1/boxes/",
            "cajas: ID exacto",
            params={"internal_id": self.account["lookup"]},
        )

    @task(1)
    def bounded_write(self):
        if not self.attempted_create:
            self.attempted_create = True
            result = self.call(
                "POST",
                "/api/v1/boxes/",
                "cajas: crear",
                201,
                json={
                    "product": self.account["product"],
                    "branch": self.account["branch"],
                    "quantity": 1,
                },
            )
            if result:
                self.box_id = result["id"]
        elif self.box_id is not None and not self.patched:
            self.patched = True
            self.call(
                "PATCH", f"/api/v1/boxes/{self.box_id}/", "cajas: editar", json={"quantity": 2}
            )

    def on_stop(self):
        global authenticated
        if getattr(self, "counted", False):
            authenticated -= 1
        if getattr(self, "csrf", None):
            self.call(
                "POST",
                "/api/v1/auth/logout/",
                "logout controlado",
                204,
                json={},
                headers={"X-CSRFToken": self.csrf},
            )
