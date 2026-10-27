"""Consulta PostgreSQL y verifica el Custom User de Fase 2, sin volcar datos."""

import json
import os
from importlib.metadata import version

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import connection  # noqa: E402
from django.db.migrations.loader import MigrationLoader  # noqa: E402

assert connection.vendor == "postgresql"
with connection.cursor() as cursor:
    cursor.execute("SELECT version()")
    database_version = cursor.fetchone()[0]
tables = connection.introspection.table_names()
assert "accounts_user" in tables and "auth_user" not in tables
loader = MigrationLoader(connection)
assert ("accounts", "0001_initial") in loader.applied_migrations
assert loader.project_state(("accounts", "0001_initial")).apps.get_model("accounts", "User")
print(
    json.dumps(
        {
            "postgresql": database_version,
            "tablas": tables,
            "autenticacion_migrada": True,
            "custom_user_en_0001": True,
            "auth_user_ausente": True,
            "migraciones_aplicadas": sorted(
                f"{app}.{name}" for app, name in loader.applied_migrations
            ),
            "versiones": {
                name: version(name)
                for name in [
                    "Django",
                    "djangorestframework",
                    "djangorestframework-simplejwt",
                    "psycopg",
                    "PyJWT",
                ]
            },
        },
        ensure_ascii=False,
    )
)
