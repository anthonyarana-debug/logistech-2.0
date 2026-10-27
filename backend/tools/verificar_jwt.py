"""Smoke JWT aislado; no conecta a DB ni ejecuta migraciones."""

from django.conf import settings

settings.configure(
    SECRET_KEY="clave-ficticia-compatibilidad-" * 4,
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
    USE_TZ=True,
)

import django  # noqa: E402

django.setup()

from rest_framework_simplejwt.backends import TokenBackend  # noqa: E402
from rest_framework_simplejwt.exceptions import TokenBackendError  # noqa: E402

backend = TokenBackend(algorithm="HS256", signing_key="clave-ficticia-prueba-" * 4)
token = backend.encode({"sub": "compatibilidad", "exp": 4102444800})
assert backend.decode(token)["sub"] == "compatibilidad"

for rejected in [
    backend.encode({"sub": "compatibilidad", "exp": 1}),
    TokenBackend(algorithm="HS256", signing_key="otra-clave-ficticia-" * 4).encode(
        {"sub": "compatibilidad", "exp": 4102444800}
    ),
]:
    try:
        backend.decode(rejected)
    except TokenBackendError:
        pass
    else:
        raise AssertionError("Se aceptó un token expirado o firmado con otra clave")
print("JWT: firma, verificación y rechazo de expiración/firma ajena correctos; sin DB.")
