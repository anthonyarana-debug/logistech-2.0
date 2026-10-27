"""Smoke HTTP local: cuenta técnica efímera, desactivada al terminar; salida sin secretos."""

import json
import os
import secrets
import uuid
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from rest_framework_simplejwt.token_blacklist.models import (  # noqa: E402
    BlacklistedToken,
    OutstandingToken,
)

User = get_user_model()
email = f"verificacion-f2-{uuid.uuid4().hex}@example.test"
password = secrets.token_urlsafe(32)
jar = CookieJar()
opener = build_opener(HTTPCookieProcessor(jar))
base = "http://backend:8000/api/v1/auth/"
results = []
csrf_token = ""


def call(route, expected, body=None, access=None):
    headers = {"Accept": "application/json"}
    if body is not None:
        headers.update({"Content-Type": "application/json", "X-CSRFToken": csrf_token})
    if access:
        headers["Authorization"] = f"Bearer {access}"
    request = Request(
        base + route + "/",
        data=json.dumps(body).encode() if body is not None else None,
        headers=headers,
    )
    try:
        response = opener.open(request, timeout=8)
    except HTTPError as error:
        response = error
    with response:
        content = response.read()
        data = json.loads(content) if content else {}
        code = response.code
    results.append({"ruta": route, "http": code, "esperado": expected})
    if code != expected:
        raise RuntimeError(f"Estado HTTP inesperado en {route}: {code}")
    return data


try:
    call("me", 401)
    csrf_token = call("csrf", 200)["csrfToken"]
    registered = call(
        "register",
        201,
        {
            "email": email,
            "password": password,
            "first_name": "Prueba técnica F2",
        },
    )
    assert registered["role"] == "OPERATOR" and registered["company"] is None
    signed_in = call("login", 200, {"email": email, "password": password})
    assert "refresh" not in signed_in
    call("me", 200, access=signed_in["access"])
    call("refresh", 200, {})
    call("logout", 204, {})
    call("refresh", 401, {})
finally:
    account = User.objects.filter(email=email).first()
    if account:
        for token in OutstandingToken.objects.filter(user=account):
            BlacklistedToken.objects.get_or_create(token=token)
        account.is_active = False
        account.set_unusable_password()
        account.save()

print(
    json.dumps(
        {
            "entorno": "HTTP local real",
            "resultados": results,
            "cuenta_tecnica": "Desactivada, contraseña inutilizable y sin datos de negocio",
        },
        ensure_ascii=False,
    )
)
