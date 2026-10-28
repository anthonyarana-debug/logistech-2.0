"""Password similarity errors use presentation labels without weakening validation."""

import pytest
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.accounts.password_errors import password_error_details
from tests.conftest import csrf


def test_password_error_rendering_preserves_template_code_and_input():
    verbose_name = User._meta.get_field("email").verbose_name
    template = "The password is too similar to the %(verbose_name)s."
    similar = ValidationError(
        template, code="password_too_similar", params={"verbose_name": verbose_name}
    )
    custom = ValidationError(
        "Unchanged input: %(value)s",
        code="custom_validator",
        params={"value": "correo electrónico"},
    )
    combined = ValidationError([similar, custom])
    details = password_error_details(combined, User(email="example@example.test"))
    assert details[0] == "The password is too similar to the email address."
    assert details[0].code == "password_too_similar"
    assert details[1] == "Unchanged input: correo electrónico"
    assert details[1].code == "custom_validator"
    assert similar.message == template
    assert similar.params == {"verbose_name": verbose_name}


@pytest.mark.django_db
@pytest.mark.parametrize("administrative", [False, True])
def test_similarity_rejected_in_english_for_registration_and_administration(client, administrative):
    email = "similarpasswordidentifier@example.test"
    body = {"email": email, "password": "similarpasswordidentifier"}
    if administrative:
        root = User.objects.create_superuser("password-label-root@example.test")
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(root)}")
        url = "/api/v1/users/"
    else:
        csrf(client)
        url = "/api/v1/auth/register/"
    response = client.post(url, body, format="json")
    assert response.status_code == 400, response.json()
    assert response["Cache-Control"] == "no-store"
    errors = response.json()["errores"]["password"]
    assert "The password is too similar to the email address." in errors
    assert "correo" not in response.content.decode()
    assert not User.objects.filter(email=email).exists()
