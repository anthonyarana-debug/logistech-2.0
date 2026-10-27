"""Consulta PostgreSQL y confirma que F1 no introdujo tablas de autenticación."""

import json
import os
from importlib.metadata import version

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import connection  # noqa: E402

assert connection.vendor == "postgresql"
with connection.cursor() as cursor:
    cursor.execute("SELECT version()")
    database_version = cursor.fetchone()[0]
tables = connection.introspection.table_names()
assert not any(t.startswith(("auth_", "accounts_", "django_admin")) for t in tables)
print(
    json.dumps(
        {
            "postgresql": database_version,
            "tablas": tables,
            "autenticacion_migrada": False,
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
