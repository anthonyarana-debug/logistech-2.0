"""Base de seguridad para producción; no representa un despliegue validado."""

import os
import re
from copy import deepcopy
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import ALLOWED_HOSTS, DATABASES, DEBUG, REST_FRAMEWORK, SECRET_KEY, env_bool

if DEBUG:
    raise ImproperlyConfigured("DEBUG must be false in production.")
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Production SECRET_KEY requires at least 50 characters.")
if not ALLOWED_HOSTS or any(
    not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", host) or ".." in host
    for host in ALLOWED_HOSTS
):
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS requires explicit hostnames without ports or schemes."
    )

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
DATABASES["default"]["OPTIONS"]["sslrootcert"] = os.environ.get(
    "DB_SSLROOTCERT", "/run/config/postgresql-ca.pem"
)
USE_DATABASE_THROTTLE = True
CSRF_TRUSTED_ORIGINS = [
    item.strip() for item in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if item.strip()
]
if not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured("CSRF_TRUSTED_ORIGINS requires explicit HTTPS origins.")
for origin in CSRF_TRUSTED_ORIGINS:
    try:
        parsed = urlsplit(origin)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname
            and re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", parsed.hostname)
            and ".." not in parsed.hostname
            and (parsed.port is None or 1 <= parsed.port <= 65535)
            and not parsed.netloc.endswith(":")
            and not (parsed.path or parsed.query or parsed.fragment)
            and parsed.username is None
            and origin == f"https://{parsed.netloc}"
            and not any(character.isspace() for character in origin)
        )
    except ValueError:
        valid = False
    if not valid:
        raise ImproperlyConfigured("CSRF_TRUSTED_ORIGINS requires explicit HTTPS origins.")
# Activar solo con backend privado y proxy que elimine/sustituya la cabecera entrante.
if env_bool("TRUSTED_TLS_PROXY"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    REST_FRAMEWORK = deepcopy(REST_FRAMEWORK)
    REST_FRAMEWORK["NUM_PROXIES"] = 1
