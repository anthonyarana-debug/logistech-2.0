from unittest.mock import patch

import pytest

from apps.accounts.throttles import LoginIdentityThrottle
from tests.conftest import csrf, login

pytestmark = pytest.mark.django_db


def test_login_ip_rate_and_window_recovery(client):
    csrf(client)
    with patch("rest_framework.throttling.SimpleRateThrottle.timer", return_value=1000):
        for n in range(5):
            assert (
                client.post(
                    "/api/v1/auth/login/",
                    {
                        "email": f"ausente{n}@example.test",
                        "password": "invalida",
                    },
                    format="json",
                ).status_code
                == 401
            )
        limited = client.post(
            "/api/v1/auth/login/",
            {
                "email": "ausente@example.test",
                "password": "invalida",
            },
            format="json",
            HTTP_X_FORWARDED_FOR="203.0.113.99",
        )
        assert limited.status_code == 429 and int(limited["Retry-After"]) > 0
    with patch("rest_framework.throttling.SimpleRateThrottle.timer", return_value=1061):
        assert (
            client.post(
                "/api/v1/auth/login/",
                {
                    "email": "ausente@example.test",
                    "password": "invalida",
                },
                format="json",
            ).status_code
            == 401
        )


def test_login_identity_rate_across_ips(client):
    csrf(client)
    for n in range(10):
        assert (
            client.post(
                "/api/v1/auth/login/",
                {
                    "email": "MISMO@example.test",
                    "password": "invalida",
                },
                format="json",
                REMOTE_ADDR=f"192.0.2.{n + 1}",
            ).status_code
            == 401
        )
    response = client.post(
        "/api/v1/auth/login/",
        {
            "email": "mismo@EXAMPLE.test",
            "password": "invalida",
        },
        format="json",
        REMOTE_ADDR="192.0.2.100",
    )
    assert response.status_code == 429
    assert LoginIdentityThrottle().duration == 900


def test_registration_rate(client):
    csrf(client)
    for n in range(3):
        assert client.post("/api/v1/auth/register/", {}, format="json").status_code == 400
    response = client.post("/api/v1/auth/register/", {}, format="json")
    assert response.status_code == 429 and "Retry-After" in response


def test_refresh_rate_with_real_rotation(client, user):
    assert login(client, user).status_code == 200
    for n in range(30):
        assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 200
    assert client.post("/api/v1/auth/refresh/", {}, format="json").status_code == 429


@pytest.mark.parametrize("data", [[], "texto", 5])
def test_invalid_login_body_is_400_not_500(client, data):
    csrf(client)
    assert client.post("/api/v1/auth/login/", data, format="json").status_code == 400


def test_admin_login_is_rate_limited(client):
    assert client.get("/admin/login/").status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
    for _ in range(5):
        assert (
            client.post(
                "/admin/login/",
                {
                    "username": "ausente@example.test",
                    "password": "incorrecta",
                },
            ).status_code
            == 200
        )
    response = client.post("/admin/login/", {})
    assert response.status_code == 429 and "Retry-After" in response
