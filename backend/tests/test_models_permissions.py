import uuid
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.loader import MigrationLoader
from django.test import Client
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.accounts.permissions import HasCompanyAccess
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company
from config.admin import site
from tests.conftest import PASSWORD

User = get_user_model()
pytestmark = pytest.mark.django_db


def test_user_exists_in_first_migration_and_no_auth_user_table():
    loader = MigrationLoader(connection)
    state = loader.project_state(("accounts", "0001_initial"))
    assert state.apps.get_model("accounts", "User")._meta.db_table == "accounts_user"
    tables = connection.introspection.table_names()
    assert "accounts_user" in tables and "auth_user" not in tables
    assert ("accounts", "0001_initial") in loader.applied_migrations


def test_superuser_manager_and_admin_policy(company, user):
    superuser = User.objects.create_superuser("root@example.test", PASSWORD)
    assert superuser.role == User.Role.SUPERADMIN
    assert superuser.is_staff and superuser.is_superuser and superuser.company_id is None
    assert site.has_permission(SimpleNamespace(user=superuser))
    user.is_staff = True
    user.save()
    assert not site.has_permission(SimpleNamespace(user=user))
    user.company = company
    user.role = User.Role.COMPANY_ADMIN
    user.save()
    assert not site.has_permission(SimpleNamespace(user=user))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"is_staff": False},
        {"is_superuser": False},
        {"role": "OPERATOR"},
    ],
)
def test_superuser_rejects_inconsistent_flags(kwargs):
    with pytest.raises(ValueError):
        User.objects.create_superuser("root@example.test", PASSWORD, **kwargs)


def test_admin_creation_and_assignment_forms(company, user):
    from config.admin import CreateUserForm

    form = CreateUserForm(
        data={
            "email": "nuevo-admin@example.test",
            "password1": PASSWORD,
            "password2": PASSWORD,
            "role": "COMPANY_ADMIN",
            "company": str(company.pk),
            "is_active": True,
        }
    )
    assert form.is_valid(), form.errors
    account = form.save()
    assert account.role == User.Role.COMPANY_ADMIN and account.company == company
    assert account.check_password(PASSWORD) and not account.is_superuser


def test_database_rejects_privilege_escalation_bypassing_model_clean(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.filter(pk=user.pk).update(role="SUPERADMIN", is_superuser=True)


def test_database_rejects_case_insensitive_duplicate_bypassing_clean(user):
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.bulk_create([User(email=user.email.upper(), password="!inutilizable")])


def test_company_admin_requires_assignment():
    with pytest.raises(ValidationError):
        User.objects.create_user("admin@example.test", PASSWORD, role="COMPANY_ADMIN")


def test_private_permission_uses_current_company_and_not_staff(user, company):
    permission = HasCompanyAccess()
    request = SimpleNamespace(user=user)
    assert not permission.has_permission(request, None)
    user.company = company
    user.save()
    assert permission.has_permission(request, None)
    assert permission.has_object_permission(request, None, SimpleNamespace(company_id=company.pk))
    other = Company.objects.create(name="Empresa ajena")
    assert not permission.has_object_permission(request, None, SimpleNamespace(company_id=other.pk))
    company.status = Company.Status.INACTIVE
    company.save()
    user.refresh_from_db()
    assert not permission.has_permission(request, None)


def test_unassigned_user_denied_on_private_policy_in_test_only_view(user):
    class PrivatePolicyProbe(APIView):
        permission_classes = [HasCompanyAccess]

        def get(self, request):
            raise AssertionError("No debe llegar a datos privados")

    request = APIRequestFactory().get("/prueba-interna-no-publicada/")
    from rest_framework.test import force_authenticate

    force_authenticate(request, user=user)
    assert PrivatePolicyProbe.as_view()(request).status_code == 403


def test_superadmin_can_open_admin_without_default_user(user):
    superuser = User.objects.create_superuser("root@example.test", PASSWORD)
    client = Client()
    client.force_login(superuser)
    assert client.get("/admin/").status_code == 200
    client.force_login(user)
    assert client.get("/admin/").status_code == 302


@pytest.fixture
def box_setup(company, user):
    user.company = company
    user.save()
    category = Category.objects.create(
        company=company, name="Refrigerados", is_fragile=True, is_perishable=True
    )
    product = Product.objects.create(
        company=company, category=category, sku="prod-01", name="Producto de prueba"
    )
    branch = Branch.objects.create(company=company, name="Central")
    return {
        "company": company,
        "product": product,
        "branch": branch,
        "created_by": user,
        "quantity": 2,
    }


def test_box_independent_identifiers_and_flags(box_setup):
    first = Box.objects.create(**box_setup)
    second = Box.objects.create(**box_setup)
    assert first.internal_id.startswith("CJ-") and len(first.internal_id) == 35
    assert first.internal_id != second.internal_id
    assert first.qr_code != second.qr_code and first.qr_code != first.pk
    assert first.product.sku == "PROD-01"
    assert first.product.category.is_fragile and first.product.category.is_perishable


def test_cross_company_references_and_tenant_changes_rejected(box_setup):
    other = Company.objects.create(name="Empresa ajena")
    foreign_branch = Branch.objects.create(company=other, name="Otra sede")
    with pytest.raises(ValidationError):
        Box.objects.create(**{**box_setup, "branch": foreign_branch})
    with pytest.raises(ValidationError):
        Product.objects.create(
            company=other, category=box_setup["product"].category, sku="OTRO", name="Inválido"
        )
    product = box_setup["product"]
    product.company = other
    with pytest.raises(ValidationError):
        product.save()


@pytest.mark.parametrize("field,value", [("quantity", 0), ("quantity", -1), ("weight_kg", 0)])
def test_box_invalid_quantity_and_weight(box_setup, field, value):
    with pytest.raises(ValidationError):
        Box.objects.create(**{**box_setup, field: value})


def test_database_quantity_constraint_and_protected_references(box_setup):
    from django.db.models.deletion import ProtectedError

    box = Box.objects.create(**box_setup)
    with pytest.raises(IntegrityError), transaction.atomic():
        Box.objects.filter(pk=box.pk).update(quantity=0)
    with pytest.raises(ProtectedError):
        box.product.delete()


def test_missing_related_objects_raise_validation_error(box_setup):
    invalid = {**box_setup}
    invalid.pop("product")
    with pytest.raises(ValidationError):
        Box.objects.create(**invalid, product_id=uuid.uuid4())
    with pytest.raises(ValidationError):
        Product.objects.create(
            company=box_setup["company"], category_id=uuid.uuid4(), sku="NO-EXISTE", name="Inválido"
        )
