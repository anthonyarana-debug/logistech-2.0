"""Base de seguridad para producción; no representa un despliegue validado."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import DEBUG, SECRET_KEY

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
# No confiar en cabeceras de proxy hasta configurar un proxy conocido.
