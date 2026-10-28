import os
import subprocess
import sys

import pytest


def production_environment(**override):
    return {
        **os.environ,
        "CSRF_TRUSTED_ORIGINS": "https://app.example.invalid",
        "TRUSTED_TLS_PROXY": "false",
        **override,
    }


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
        env=production_environment(),
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
        {"CSRF_TRUSTED_ORIGINS": ""},
        {"CSRF_TRUSTED_ORIGINS": "https://user:password@app.example.invalid"},
        {"CSRF_TRUSTED_ORIGINS": "https://app.example.invalid:wrong"},
        {"CSRF_TRUSTED_ORIGINS": "https://app.example.invalid:99999"},
        {"CSRF_TRUSTED_ORIGINS": "https://[malformed"},
        {"ALLOWED_HOSTS": "*.example.invalid"},
        {"ALLOWED_HOSTS": "https://app.example.invalid"},
        {"ALLOWED_HOSTS": "app.example.invalid:443"},
        {"ALLOWED_HOSTS": ",,"},
        {"DEBUG": "true"},
        {"SECRET_KEY": "too-short"},
    ],
)
def test_production_rejects_unsafe_configuration(override):
    run = subprocess.run(
        [sys.executable, "-c", "from config.settings import production"],
        env=production_environment(**override),
        capture_output=True,
        timeout=15,
    )
    assert run.returncode != 0
    assert b"ImproperlyConfigured" in run.stderr


def test_production_proxy_and_shared_quota_policy():
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            "from config.settings import production as s; "
            "assert s.USE_DATABASE_THROTTLE; "
            "assert s.REST_FRAMEWORK['NUM_PROXIES'] == 1; "
            "assert s.SECURE_PROXY_SSL_HEADER == ('HTTP_X_FORWARDED_PROTO', 'https'); "
            "assert s.DATABASES['default']['OPTIONS']['sslrootcert'] == "
            "'/run/config/postgresql-ca.pem'",
        ],
        env=production_environment(
            TRUSTED_TLS_PROXY="true", DB_SSLROOTCERT="/run/config/postgresql-ca.pem"
        ),
        capture_output=True,
        timeout=15,
    )
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize("settings_module", ["production", "testing"])
def test_secret_files_are_loaded_without_literal_secrets(tmp_path, settings_module):
    secret_file = tmp_path / "secret"
    password_file = tmp_path / "password"
    secret_file.write_text("fictional-test-secret-" * 4, encoding="utf-8")
    password_file.write_text("fictional-password\n", encoding="utf-8")
    env = production_environment(
        SECRET_KEY_FILE=str(secret_file), POSTGRES_PASSWORD_FILE=str(password_file)
    )
    env.pop("SECRET_KEY", None)
    env.pop("POSTGRES_PASSWORD", None)
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            f"from config.settings import {settings_module} as s; "
            "assert s.SECRET_KEY == 'fictional-test-secret-' * 4; "
            "assert s.DATABASES['default']['PASSWORD'] == 'fictional-password'",
        ],
        env=env,
        capture_output=True,
        timeout=15,
    )
    assert run.returncode == 0, run.stderr


@pytest.mark.parametrize("name", ["SECRET_KEY", "POSTGRES_PASSWORD"])
def test_secret_files_reject_ambiguous_or_unreadable_values(name, tmp_path):
    secret = "fictional-do-not-log-secret-" * 3
    path = tmp_path / "missing-secret"
    env = production_environment(**{name: secret, f"{name}_FILE": str(path)})
    for ambiguous in (True, False):
        if not ambiguous:
            env.pop(name)
        run = subprocess.run(
            [sys.executable, "-c", "from config.settings import production"],
            env=env,
            capture_output=True,
            timeout=15,
        )
        assert run.returncode != 0
        assert b"ImproperlyConfigured" in run.stderr
        assert secret.encode() not in run.stderr
