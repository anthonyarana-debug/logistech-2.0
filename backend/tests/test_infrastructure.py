import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from django.apps import apps
from django.conf import settings
from django.db import OperationalError
from django.test import Client, override_settings

from apps.core.checks import prevent_default_user_migration


def test_live_does_not_query_database():
    with patch("apps.core.views.connection.cursor") as cursor:
        response = Client().get("/api/v1/health/live/")
    assert response.status_code == 200
    cursor.assert_not_called()


def test_readiness_checks_database():
    with patch("apps.core.views.connection.cursor") as cursor:
        cursor.return_value.__enter__.return_value.fetchone.return_value = (1,)
        response = Client().get("/api/v1/health/")
    assert response.status_code == 200
    cursor.return_value.__enter__.return_value.execute.assert_called_once_with("SELECT 1")


def test_readiness_failure_does_not_leak_database_error():
    with patch("apps.core.views.connection.cursor", side_effect=OperationalError("dato-reservado")):
        response = Client().get("/api/v1/health/")
    assert response.status_code == 503
    assert b"dato-reservado" not in response.content


def test_unknown_api_route_is_json_404():
    response = Client().get("/api/v1/no-existe/")
    assert response.status_code == 404
    assert response.json() == {"detalle": "Recurso no encontrado."}


def test_custom_user_is_enabled_before_auth_migrations():
    assert apps.is_installed("django.contrib.auth")
    assert settings.AUTH_USER_MODEL == "accounts.User"
    assert apps.get_model(settings.AUTH_USER_MODEL)._meta.db_table == "accounts_user"
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_guard_rejects_default_user_if_auth_is_enabled():
    with patch("apps.core.checks.apps.is_installed", return_value=True):
        with override_settings(AUTH_USER_MODEL="auth.User"):
            errors = prevent_default_user_migration(None)
    assert [error.id for error in errors] == ["logistech.E001"]


def test_installed_jwt_backend_signs_and_verifies():
    # Smoke aislado de biblioteca, conservado desde F1.
    script = Path(__file__).resolve().parents[1] / "tools" / "verificar_jwt.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
