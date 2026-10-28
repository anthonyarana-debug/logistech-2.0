from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

import pytest
from django.conf import settings
from django.contrib.auth.hashers import identify_hasher
from django.db import connections
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.accounts.models import User
from tests.conftest import PASSWORD, csrf, login

pytestmark = pytest.mark.django_db


def test_registration_hash_and_unassigned_operator(client):
    csrf(client)
    response = client.post(
        "/api/v1/auth/register/",
        {
            "email": "NUEVO@Example.test",
            "password": PASSWORD,
        },
        format="json",
    )
    assert response.status_code == 201
    user = User.objects.get(email="nuevo@example.test")
    assert user.role == User.Role.OPERATOR and user.company_id is None
    assert not user.is_staff and not user.is_superuser
    assert user.password != PASSWORD and user.check_password(PASSWORD)
    assert identify_hasher(user.password).algorithm == "pbkdf2_sha256"
    assert "password" not in response.json() and "access" not in response.json()
    assert response.json()["assignment_pending"] is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("role", "SUPERADMIN"),
        ("role", "COMPANY_ADMIN"),
        ("company", "ajena"),
        ("company_id", "ajena"),
        ("is_staff", True),
        ("is_superuser", True),
        ("is_active", False),
        ("groups", []),
        ("user_permissions", []),
    ],
)
def test_registration_rejects_privileged_fields(client, field, value):
    csrf(client)
    response = client.post(
        "/api/v1/auth/register/",
        {
            "email": "nuevo@example.test",
            "password": PASSWORD,
            field: value,
        },
        format="json",
    )
    assert response.status_code == 400
    assert not User.objects.exists()


@pytest.mark.parametrize(
    "data",
    [
        {"email": "invalido", "password": PASSWORD},
        {"email": "nuevo@example.test", "password": "123"},
        {"email": "nuevo@example.test"},
        [],
    ],
)
def test_registration_validation(client, data):
    csrf(client)
    assert client.post("/api/v1/auth/register/", data, format="json").status_code == 400


def test_duplicate_email_case_insensitive(client, user):
    csrf(client)
    response = client.post(
        "/api/v1/auth/register/",
        {
            "email": user.email.upper(),
            "password": PASSWORD,
        },
        format="json",
    )
    assert response.status_code == 400
    assert User.objects.count() == 1


def test_login_cookie_and_me(client, user):
    csrf(client)
    response = client.post(
        "/api/v1/auth/login/",
        {
            "email": user.email.upper(),
            "password": PASSWORD,
        },
        format="json",
    )
    assert response.status_code == 200
    assert "refresh" not in response.json()
    cookie = response.cookies[settings.AUTH_REFRESH_COOKIE]
    assert cookie["httponly"] and cookie["samesite"] == "Lax"
    assert cookie["path"] == "/api/v1/auth/" and cookie["max-age"] == 86400
    assert response["Cache-Control"] == "no-store"
    me = client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    assert me.status_code == 200 and me.json()["id"] == str(user.pk)
    assert me.json()["company"] is None
    assert not {"password", "is_staff", "is_superuser"} & set(me.json())


def test_invalid_login_and_inactive_account_have_same_error(client, user):
    csrf(client)
    results = []
    for email, password in [(user.email, "incorrecta"), ("ausente@example.test", PASSWORD)]:
        response = client.post(
            "/api/v1/auth/login/", {"email": email, "password": password}, format="json"
        )
        results.append((response.status_code, response.json()))
    user.is_active = False
    user.save()
    response = client.post(
        "/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json"
    )
    results.append((response.status_code, response.json()))
    assert all(result == results[0] for result in results)
    assert results[0][0] == 401


@pytest.mark.parametrize("token_kind", ["missing", "invalid", "expired", "refresh"])
def test_me_rejects_invalid_access(client, user, token_kind):
    access = AccessToken.for_user(user)
    access.set_exp(lifetime=timedelta(seconds=-1))
    token = {
        "missing": "",
        "invalid": "alterado",
        "expired": str(access),
        "refresh": str(RefreshToken.for_user(user)),
    }[token_kind]
    response = client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 401


def test_refresh_rotation_replay_and_logout(client, user):
    initial = login(client, user)
    old_cookie = initial.cookies[settings.AUTH_REFRESH_COOKIE].value
    rotated = client.post("/api/v1/auth/refresh/", {}, format="json")
    assert rotated.status_code == 200
    new_cookie = rotated.cookies[settings.AUTH_REFRESH_COOKIE].value
    assert new_cookie != old_cookie
    client.cookies[settings.AUTH_REFRESH_COOKIE] = old_cookie
    assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 401
    client.cookies[settings.AUTH_REFRESH_COOKIE] = new_cookie
    logout = client.post("/api/v1/auth/logout/", {}, format="json")
    assert logout.status_code == 204 and not logout.content
    assert logout.cookies[settings.AUTH_REFRESH_COOKIE]["max-age"] == 0
    client.cookies[settings.AUTH_REFRESH_COOKIE] = new_cookie
    assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 401
    assert client.post("/api/v1/auth/logout/", {}, format="json").status_code == 204


def test_deactivation_rejects_existing_access_and_refresh(client, user):
    response = login(client, user)
    user.is_active = False
    user.save()
    assert (
        client.get(
            "/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}"
        ).status_code
        == 401
    )
    assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 401


@pytest.mark.parametrize("endpoint", ["register", "login", "refresh", "logout"])
def test_cookie_mutations_require_csrf(client, endpoint):
    response = client.post(f"/api/v1/auth/{endpoint}/", {}, format="json")
    assert response.status_code == 403
    assert response.json() == {"detalle": "CSRF verification failed."}


def test_foreign_origin_rejected_even_with_csrf(client, user):
    csrf(client)
    response = client.post(
        "/api/v1/auth/login/",
        {
            "email": user.email,
            "password": PASSWORD,
        },
        format="json",
        HTTP_ORIGIN="https://ajeno.example",
    )
    assert response.status_code == 403


def test_refresh_missing_corrupt_and_expired(client, user):
    csrf(client)
    for value in ["", "invalido"]:
        client.cookies[settings.AUTH_REFRESH_COOKIE] = value
        assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 401
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(lifetime=timedelta(seconds=-1))
    client.cookies[settings.AUTH_REFRESH_COOKIE] = str(refresh)
    assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 401


def test_cookie_secure_when_production_policy_enabled(client, user):
    with override_settings(AUTH_COOKIE_SECURE=True):
        response = login(client, user)
    assert response.cookies[settings.AUTH_REFRESH_COOKIE]["secure"]


def test_me_observes_current_assignment_not_token_claim(client, user, company):
    response = login(client, user)
    user.company = company
    user.save()
    me = client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    assert me.json()["company"]["id"] == str(company.pk)
    assert me.json()["assignment_pending"] is False


@pytest.mark.django_db(transaction=True)
def test_concurrent_refresh_only_one_consumes_cookie(user):
    starter = APIClient(enforce_csrf_checks=True)
    initial = login(starter, user)
    cookie = initial.cookies[settings.AUTH_REFRESH_COOKIE].value
    barrier = Barrier(2)

    def rotate(_):
        try:
            browser = APIClient(enforce_csrf_checks=True)
            csrf(browser)
            browser.cookies[settings.AUTH_REFRESH_COOKIE] = cookie
            barrier.wait(timeout=10)
            return browser.post("/api/v1/auth/refresh/", {}, format="json").status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        codes = list(executor.map(rotate, range(2)))
    assert sorted(codes) == [200, 401]
