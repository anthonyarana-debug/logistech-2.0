import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.organizations.models import Company

PASSWORD = "PruebaLocal!4820_segura"


@pytest.fixture(autouse=True)
def clean_throttles():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client():
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture
def user(db):
    return User.objects.create_user("operador@example.test", PASSWORD)


@pytest.fixture
def company(db):
    return Company.objects.create(name="Empresa de prueba")


def csrf(client):
    response = client.get("/api/v1/auth/csrf/")
    assert response.status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=response.json()["csrfToken"])


def login(client, user):
    csrf(client)
    return client.post(
        "/api/v1/auth/login/", {"email": user.email, "password": PASSWORD}, format="json"
    )
