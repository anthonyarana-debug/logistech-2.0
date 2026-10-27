"""Valores ficticios únicamente para pytest; las pruebas de integración usan PostgreSQL."""

import os

os.environ.setdefault("SECRET_KEY", "clave-ficticia-de-pruebas-" * 4)
os.environ.setdefault("ALLOWED_HOSTS", "testserver,localhost,127.0.0.1,backend")
os.environ.setdefault("POSTGRES_DB", "logistech")
os.environ.setdefault("POSTGRES_USER", "logistech")
os.environ.setdefault("POSTGRES_PASSWORD", "solo-pruebas-no-es-un-secreto-real")
os.environ.setdefault("DB_HOST", "127.0.0.1")

from .base import *  # noqa: E402,F403

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1", "backend"]
DEBUG = False
