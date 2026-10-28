"""English presentation keeps legacy contracts, user data and model metadata intact."""

import pytest
from django.conf import settings
from django.test import Client

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category
from apps.core.admin_presentation import object_tree, presentation_options
from apps.core.messages import domain_message
from config.admin import site
from tests.conftest import PASSWORD, csrf

pytestmark = pytest.mark.django_db


def test_default_english_and_legacy_health_contract(client):
    assert settings.LANGUAGE_CODE == "en"
    response = client.get("/api/v1/health/", HTTP_ACCEPT_LANGUAGE="es-PE")
    assert response.status_code == 200
    assert response.json() == {"estado": "disponible", "base_de_datos": "disponible"}
    denied = client.get("/api/v1/boxes/", HTTP_ACCEPT_LANGUAGE="es")
    assert denied.status_code == 401
    assert denied.json() == {"detalle": "Invalid credentials or session."}


def test_framework_validation_is_english_without_changing_error_keys(client):
    csrf(client)
    response = client.post(
        "/api/v1/auth/login/", {"email": "invalid", "password": PASSWORD}, format="json"
    )
    assert response.status_code == 400
    assert response.json() == {"errores": {"email": ["Enter a valid email address."]}}


def test_spanish_business_data_is_not_translated(company):
    category = Category.objects.create(company=company, name="Mercancía frágil")
    category.refresh_from_db()
    assert category.name == "Mercancía frágil"
    assert domain_message(category.name) == category.name


def test_admin_options_are_copied_without_migration_metadata_changes():
    before = Box._meta.verbose_name
    localized = presentation_options(Box._meta)
    assert localized.verbose_name == "box"
    assert Box._meta.verbose_name == before == "caja"
    assert Box.Status.REGISTERED.value == "REGISTERED"
    assert object_tree(["Caja: categoría privada", ["Sucursal: sede española"]]) == [
        "Box: categoría privada",
        ["Branch: sede española"],
    ]


def test_admin_forms_and_pages_use_english(company):
    root = User.objects.create_superuser("language-root@example.test", PASSWORD)
    client = Client()
    client.force_login(root)
    response = client.get("/admin/")
    assert response.status_code == 200
    assert "Restricted administration" in response.content.decode()
    users = client.get("/admin/accounts/user/")
    assert "Superadmin" in users.content.decode()
    assert "Superadministrador" not in users.content.decode()
    response = client.get("/admin/boxes/box/add/")
    assert response.status_code == 200
    assert response.context_data["opts"].verbose_name == "box"
    form = response.context_data["adminform"].form
    assert form.fields["product"].label == "Product"
    html = response.content.decode()
    assert "Add another product" in html
    assert "Add another producto" not in html
    assert dict(form.fields["status"].choices)["REGISTERED"] == "Registered"
    response = client.post(
        "/admin/accounts/user/add/",
        {
            "email": "invalid-admin@example.test",
            "password1": PASSWORD,
            "password2": PASSWORD,
            "role": "COMPANY_ADMIN",
            "is_active": "on",
        },
    )
    assert response.status_code == 200
    assert "The administrator must have an assigned company." in response.content.decode()
    assert not User.objects.filter(email="invalid-admin@example.test").exists()
    assert site._registry[Box].model is Box
    response = client.post(
        "/admin/catalog/category/add/",
        {
            "company": str(company.pk),
            "name": "Categoría del usuario",
            "_save": "Save",
        },
        follow=True,
    )
    assert response.status_code == 200
    html = response.content.decode()
    assert "The category" in html
    assert "Categoría del usuario" in html
    assert "The categoría" not in html
    category = Category.objects.get(name="Categoría del usuario")
    history = client.get(f"/admin/catalog/category/{category.pk}/history/")
    assert history.status_code == 200
    assert history.context_data["opts"].verbose_name == "category"
    duplicate = client.post(
        "/admin/accounts/user/add/",
        {
            "email": root.email,
            "password1": PASSWORD,
            "password2": PASSWORD,
            "role": "OPERATOR",
            "is_active": "on",
        },
    )
    errors = str(duplicate.context_data["adminform"].form.errors)
    assert "usuario" not in errors and "correo electrónico" not in errors
    assert "already exists" in errors


def test_options_labels_and_enum_values_remain_compatible(client, user, company):
    from rest_framework_simplejwt.tokens import AccessToken

    user.company = company
    user.save()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
    response = client.options("/api/v1/boxes/")
    assert response.status_code == 200
    fields = response.json()["actions"]["POST"]
    assert fields["quantity"]["label"] == "Quantity"
    assert fields["status"]["choices"] == [
        {"value": "REGISTERED", "display_name": "Registered"},
        {"value": "RECEIVED", "display_name": "Received"},
        {"value": "REJECTED", "display_name": "Rejected"},
    ]


def test_admin_label_filter_keeps_untrusted_html_escaped():
    from apps.core.templatetags.english_presentation import english_label_tag

    assert "<script>" not in english_label_tag("<script>alert(1)</script>")
    assert "&lt;script&gt;" in english_label_tag("<script>alert(1)</script>")
