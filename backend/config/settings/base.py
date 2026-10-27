"""Configuración común; no habilitar auth/admin antes de accounts.0001_initial."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parents[2]


def required(name):
    value = os.environ.get(name, "").strip()
    if not value or value.startswith("REEMPLAZAR_"):
        raise ImproperlyConfigured(f"Configura la variable {name} en el entorno.")
    return value


def env_bool(name, default="false"):
    value = os.environ.get(name, default).lower()
    if value not in {"true", "false"}:
        raise ImproperlyConfigured(f"{name} debe ser true o false.")
    return value == "true"


SECRET_KEY = required("SECRET_KEY")
DEBUG = env_bool("DEBUG")
ALLOWED_HOSTS = [host.strip() for host in required("ALLOWED_HOSTS").split(",") if host.strip()]
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS debe enumerar hosts explícitos.")

# Sin auth, admin, sessions o contenttypes en F1. Nunca migrar auth.User.
INSTALLED_APPS = ["rest_framework", "apps.core.apps.CoreConfig"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": required("POSTGRES_DB"),
        "USER": required("POSTGRES_USER"),
        "PASSWORD": required("POSTGRES_PASSWORD"),
        "HOST": required("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 0,
        "OPTIONS": {"connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "3"))},
    }
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
}
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
}
