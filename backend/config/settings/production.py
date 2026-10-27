"""Base de seguridad para producción; no representa un despliegue validado."""

import os
from copy import deepcopy
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import DATABASES, DEBUG, SECRET_KEY, env_bool

if DEBUG:
    raise ImproperlyConfigured("DEBUG debe ser false en producción.")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("SECRET_KEY de producción requiere al menos 50 caracteres.")

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
AUTH_COOKIE_SECURE = True
# TLS PostgreSQL con comprobación de identidad; el CA real se monta fuera de Git.
DATABASES = deepcopy(DATABASES)
DATABASES["default"]["OPTIONS"]["sslmode"] = "verify-full"
if os.environ.get("DB_SSLROOTCERT"):
    DATABASES["default"]["OPTIONS"]["sslrootcert"] = os.environ["DB_SSLROOTCERT"]
CSRF_TRUSTED_ORIGINS = [
    item.strip() for item in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if item.strip()
]
for origin in CSRF_TRUSTED_ORIGINS:
    parsed = urlsplit(origin)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.path
        or parsed.query
        or parsed.fragment
        or parsed.username
        or "*" in origin
    ):
        raise ImproperlyConfigured("CSRF_TRUSTED_ORIGINS requiere orígenes HTTPS explícitos.")
# Activar solo con backend privado y proxy que elimine/sustituya la cabecera entrante.
if env_bool("TRUSTED_TLS_PROXY"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
