import os
import subprocess
import sys

import pytest


def test_production_cookie_and_database_policy():
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            "from config.settings import production as s; "
            "assert s.AUTH_COOKIE_SECURE and s.CSRF_COOKIE_SECURE and not s.DEBUG; "
            'assert s.DATABASES["default"]["OPTIONS"]["sslmode"] == "verify-full"; '
            'assert not hasattr(s, "SECURE_PROXY_SSL_HEADER")',
        ],
        env={**os.environ, "TRUSTED_TLS_PROXY": "false"},
        capture_output=True,
        timeout=15,
    )
    assert run.returncode == 0


@pytest.mark.parametrize(
    "override",
    [
        {"CSRF_TRUSTED_ORIGINS": "http://app.example.invalid"},
        {"CSRF_TRUSTED_ORIGINS": "https://*.example.invalid"},
        {"CSRF_TRUSTED_ORIGINS": "https://app.example.invalid/ruta"},
        {"TRUSTED_TLS_PROXY": "maybe"},
    ],
)
def test_production_rejects_unsafe_configuration(override):
    run = subprocess.run(
        [sys.executable, "-c", "from config.settings import production"],
        env={**os.environ, **override},
        capture_output=True,
        timeout=15,
    )
    assert run.returncode != 0
    assert b"ImproperlyConfigured" in run.stderr
