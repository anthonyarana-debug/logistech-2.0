"""F6 real PostgreSQL tests: scopes, administrative writes and privilege boundaries."""

import uuid
from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company

pytestmark = pytest.mark.django_db


@pytest.fixture
def ops():
    a, b = [Company.objects.create(name=name) for name in ("Operations A", "Private B")]
    root = User.objects.create_superuser("ops-root@example.test")
    admin = User.objects.create_user("ops-admin@example.test", role="COMPANY_ADMIN", company=a)
    operator = User.objects.create_user("ops-operator@example.test", company=a)
    other = User.objects.create_user("ops-other@example.test", company=b)
    pending = User.objects.create_user("ops-pending@example.test")
    ca, cb = [Category.objects.create(company=c, name="Goods") for c in (a, b)]
    ba, bb = [Branch.objects.create(company=c, name="Warehouse") for c in (a, b)]
    pa, pb = [
        Product.objects.create(company=c, category=k, sku="SKU", name="Goods")
        for c, k in ((a, ca), (b, cb))
    ]
    return SimpleNamespace(**locals())


def authenticate(client, user):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")


@pytest.mark.parametrize("resource", ["companies", "branches", "products", "users", "overview"])
def test_operations_require_authentication(client, resource):
    assert client.get(f"/api/v1/{resource}/").status_code == 401


@pytest.mark.parametrize("resource", ["companies", "branches", "products", "users", "overview"])
def test_pending_operator_has_no_private_operations(client, ops, resource):
    authenticate(client, ops.pending)
    assert client.get(f"/api/v1/{resource}/").status_code == 403


def test_company_lifecycle_superadmin_only(client, ops):
    authenticate(client, ops.admin)
    assert client.get("/api/v1/companies/").status_code == 403
    authenticate(client, ops.root)
    r = client.post("/api/v1/companies/", {"name": " New business "}, format="json")
    assert r.status_code == 201, r.data
    url = f"/api/v1/companies/{r.data['id']}/"
    assert r.data["name"] == "New business"
    assert client.patch(url, {"status": "INACTIVE"}, format="json").status_code == 200
    assert client.patch(url, {"status": "ACTIVE"}, format="json").status_code == 200
    assert client.delete(url).status_code == 204
    assert client.delete(f"/api/v1/companies/{ops.a.pk}/").status_code == 409


@pytest.mark.parametrize(
    "resource,foreign", [("branches", "bb"), ("products", "pb"), ("users", "other")]
)
def test_company_scope_cannot_be_bypassed(client, ops, resource, foreign):
    authenticate(client, ops.admin)
    r = client.get(f"/api/v1/{resource}/")
    assert r.status_code == 200
    assert all(x["company"] == str(ops.a.pk) for x in r.json())
    assert r["Cache-Control"] == "no-store"
    url = f"/api/v1/{resource}/{getattr(ops, foreign).pk}/"
    assert client.get(url).status_code == 404
    assert client.patch(url, {"name": "intrusion"}, format="json").status_code == 404
    assert client.get(f"/api/v1/{resource}/?company={ops.b.pk}").status_code == 403
    assert client.get(f"/api/v1/{resource}/?company__name=Private").status_code == 400


@pytest.mark.parametrize("resource", ["branches", "products"])
def test_operator_reads_but_cannot_administer(client, ops, resource):
    authenticate(client, ops.operator)
    assert client.get(f"/api/v1/{resource}/").status_code == 200
    assert client.post(f"/api/v1/{resource}/", {}, format="json").status_code == 403
    record = ops.ba if resource == "branches" else ops.pa
    for method in (client.patch, client.delete):
        assert method(f"/api/v1/{resource}/{record.pk}/", {}, format="json").status_code == 403
    assert client.get("/api/v1/users/").status_code == 403


def test_branch_and_product_crud_integrity(client, ops):
    authenticate(client, ops.admin)
    r = client.post("/api/v1/branches/", {"name": "New branch", "address": "Street"}, format="json")
    assert r.status_code == 201, r.data
    branch = r.data["id"]
    assert (
        client.post("/api/v1/branches/", {"name": "new BRANCH"}, format="json").status_code == 409
    )
    assert (
        client.patch(
            f"/api/v1/branches/{branch}/", {"company": str(ops.b.pk)}, format="json"
        ).status_code
        == 400
    )
    p = client.post(
        "/api/v1/products/",
        {"name": "New goods", "sku": " new ", "category": str(ops.ca.pk)},
        format="json",
    )
    assert p.status_code == 201, p.data
    assert p.data["sku"] == "NEW"
    assert (
        client.post(
            "/api/v1/products/",
            {"name": "Duplicate", "sku": "new", "category": str(ops.ca.pk)},
            format="json",
        ).status_code
        == 409
    )
    assert (
        client.patch(
            f"/api/v1/products/{p.data['id']}/", {"category": str(ops.cb.pk)}, format="json"
        ).status_code
        == 400
    )
    assert client.delete(f"/api/v1/products/{p.data['id']}/").status_code == 204
    assert client.delete(f"/api/v1/branches/{branch}/").status_code == 204
    Box.objects.create(
        company=ops.a, product=ops.pa, branch=ops.ba, created_by=ops.operator, quantity=1
    )
    assert client.delete(f"/api/v1/products/{ops.pa.pk}/").status_code == 409
    assert client.delete(f"/api/v1/branches/{ops.ba.pk}/").status_code == 409


@pytest.mark.parametrize(
    "resource,payload", [("branches", {"name": "x"}), ("products", {"name": "x", "sku": "X"})]
)
def test_global_creation_requires_explicit_company(client, ops, resource, payload):
    authenticate(client, ops.root)
    if resource == "products":
        payload = {**payload, "category": str(ops.ca.pk)}
    assert client.post(f"/api/v1/{resource}/", payload, format="json").status_code == 400
    bad = {**payload, "company": str(ops.b.pk)}
    if resource == "products":
        assert client.post(f"/api/v1/{resource}/", bad, format="json").status_code == 400
    good = {**payload, "company": str(ops.a.pk)}
    assert client.post(f"/api/v1/{resource}/", good, format="json").status_code == 201


def test_company_admin_can_manage_only_own_operators(client, ops):
    authenticate(client, ops.admin)
    r = client.post(
        "/api/v1/users/",
        {
            "email": "new-operator@example.test",
            "password": "Operational-Test!8294",
            "branch": str(ops.ba.pk),
        },
        format="json",
    )
    assert r.status_code == 201, r.data
    user = User.objects.get(pk=r.data["id"])
    assert user.company == ops.a and user.role == "OPERATOR" and user.branch == ops.ba
    assert user.check_password("Operational-Test!8294") and not user.is_staff
    assert (
        not {"password", "groups", "user_permissions", "is_superuser", "is_staff"} & r.data.keys()
    )
    assert (
        client.patch(f"/api/v1/users/{user.pk}/", {"is_active": False}, format="json").status_code
        == 200
    )
    assert client.delete(f"/api/v1/users/{user.pk}/").status_code == 405
    assert (
        client.patch(
            f"/api/v1/users/{ops.admin.pk}/", {"is_active": False}, format="json"
        ).status_code
        == 403
    )
    assert (
        client.patch(
            f"/api/v1/users/{user.pk}/", {"branch": str(ops.bb.pk)}, format="json"
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("role", "COMPANY_ADMIN"),
        ("company", None),
        ("is_staff", True),
        ("is_superuser", True),
        ("groups", []),
        ("user_permissions", []),
    ],
)
def test_admin_cannot_escalate_fields(client, ops, field, value):
    authenticate(client, ops.admin)
    assert (
        client.patch(f"/api/v1/users/{ops.operator.pk}/", {field: value}, format="json").status_code
        == 400
    )


def test_global_user_assignment_and_root_protection(client, ops):
    authenticate(client, ops.root)
    url = f"/api/v1/users/{ops.pending.pk}/"
    r = client.patch(
        url,
        {"company": str(ops.a.pk), "role": "COMPANY_ADMIN", "branch": str(ops.ba.pk)},
        format="json",
    )
    assert r.status_code == 200, r.data
    assert client.patch(url, {"role": "SUPERADMIN"}, format="json").status_code == 400
    assert client.patch(url, {"company": str(ops.b.pk)}, format="json").status_code == 400
    assert (
        client.patch(url, {"company": str(ops.b.pk), "branch": None}, format="json").status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/v1/users/{ops.root.pk}/", {"is_active": False}, format="json"
        ).status_code
        == 403
    )


def test_live_role_assignment_and_deactivation_revoke_access(client, ops):
    authenticate(client, ops.pending)
    assert client.get("/api/v1/branches/").status_code == 403
    ops.pending.company = ops.a
    ops.pending.save()
    assert client.get("/api/v1/branches/").status_code == 200
    ops.pending.is_active = False
    ops.pending.save()
    assert client.get("/api/v1/branches/").status_code == 401


@pytest.mark.parametrize("role", ["root", "admin", "operator"])
def test_overview_counts_are_real_and_scoped(client, ops, role):
    authenticate(client, getattr(ops, role))
    r = client.get("/api/v1/overview/")
    assert r.status_code == 200, r.data
    assert r.data["counts"]["products"] == (2 if role == "root" else 1)
    assert ("users" in r.data["counts"]) == (role != "operator")
    assert client.get("/api/v1/overview/?company=invalid").status_code == 400
    if role != "root":
        assert client.get(f"/api/v1/overview/?company={ops.b.pk}").status_code == 403


def test_user_branch_model_rejects_cross_company(client, ops):
    ops.operator.branch = ops.bb
    with pytest.raises(ModelValidationError):
        ops.operator.save()


@pytest.mark.parametrize("model_name", ["company", "branch", "product"])
def test_status_constraint_is_enforced_by_postgresql(ops, model_name):
    from django.db import IntegrityError, transaction

    record = {"company": ops.a, "branch": ops.ba, "product": ops.pa}[model_name]
    with pytest.raises(IntegrityError), transaction.atomic():
        type(record).objects.filter(pk=record.pk).update(status="INVALID")


def test_defensive_reads_exclude_corrupt_references(client, ops):
    # Raw writes bypass model.clean; an API response must still not reveal another tenant.
    Product.objects.filter(pk=ops.pa.pk).update(category=ops.cb)
    authenticate(client, ops.admin)
    assert client.get("/api/v1/products/").json() == []


def test_global_can_disable_account_in_inactive_company(client, ops):
    ops.a.status = "INACTIVE"
    ops.a.save()
    authenticate(client, ops.root)
    assert (
        client.patch(
            f"/api/v1/users/{ops.operator.pk}/", {"is_active": False}, format="json"
        ).status_code
        == 200
    )


def test_password_reset_is_not_an_unrevoked_session_backdoor(client, ops):
    authenticate(client, ops.root)
    assert (
        client.patch(
            f"/api/v1/users/{ops.operator.pk}/", {"password": "A-New-Password!4829"}, format="json"
        ).status_code
        == 400
    )


def test_deactivate_user_with_unchanged_inactive_branch(client, ops):
    ops.operator.branch = ops.ba
    ops.operator.save()
    ops.ba.status = "INACTIVE"
    ops.ba.save()
    authenticate(client, ops.root)
    result = client.patch(
        f"/api/v1/users/{ops.operator.pk}/",
        {
            "branch": str(ops.ba.pk),
            "is_active": False,
        },
        format="json",
    )
    assert result.status_code == 200, result.data
    # Another user still cannot acquire that inactive branch.
    assert (
        client.patch(
            f"/api/v1/users/{ops.pending.pk}/",
            {
                "company": str(ops.a.pk),
                "branch": str(ops.ba.pk),
            },
            format="json",
        ).status_code
        == 400
    )


def test_http_deactivation_invalidates_preexisting_access(client, ops):
    from rest_framework.test import APIClient

    operator_client = APIClient()
    authenticate(operator_client, ops.operator)
    assert operator_client.get("/api/v1/branches/").status_code == 200
    authenticate(client, ops.admin)
    assert (
        client.patch(
            f"/api/v1/users/{ops.operator.pk}/",
            {
                "is_active": False,
            },
            format="json",
        ).status_code
        == 200
    )
    assert operator_client.get("/api/v1/branches/").status_code == 401


def test_branch_assignment_protects_deletion_and_creator_history(client, ops):
    ops.operator.branch = ops.ba
    ops.operator.save()
    box = Box.objects.create(
        company=ops.a, product=ops.pa, branch=ops.ba, created_by=ops.operator, quantity=7
    )
    authenticate(client, ops.root)
    assert client.delete(f"/api/v1/branches/{ops.ba.pk}/").status_code == 409
    assert (
        client.patch(
            f"/api/v1/users/{ops.operator.pk}/",
            {
                "company": str(ops.b.pk),
                "branch": str(ops.bb.pk),
            },
            format="json",
        ).status_code
        == 200
    )
    box.refresh_from_db()
    assert box.company == ops.a and box.created_by == ops.operator and box.quantity == 7


def test_admin_cannot_claim_pending_user_or_modify_another_admin(client, ops):
    second = User.objects.create_user(
        "second-admin@example.test", role="COMPANY_ADMIN", company=ops.a
    )
    authenticate(client, ops.admin)
    assert (
        client.patch(
            f"/api/v1/users/{ops.pending.pk}/",
            {
                "company": str(ops.a.pk),
            },
            format="json",
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/users/{second.pk}/",
            {
                "is_active": False,
            },
            format="json",
        ).status_code
        == 403
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"role": "SUPERADMIN"},
        {"is_superuser": True},
        {"is_staff": True},
        {"groups": []},
        {"user_permissions": []},
        {"role": "COMPANY_ADMIN", "company": None},
    ],
)
def test_global_creation_cannot_grant_hidden_privileges(client, ops, payload):
    authenticate(client, ops.root)
    assert (
        client.post(
            "/api/v1/users/",
            {
                "email": "privilege-probe@example.test",
                "password": "Operational-Test!8294",
                **payload,
            },
            format="json",
        ).status_code
        == 400
    )
    assert not User.objects.filter(email="privilege-probe@example.test").exists()


@pytest.mark.parametrize("resource", ["companies", "branches", "products", "users"])
def test_malformed_and_unknown_fields_are_safe(client, ops, resource):
    authenticate(client, ops.root)
    assert client.post(f"/api/v1/{resource}/", [], format="json").status_code == 400
    assert (
        client.post(f"/api/v1/{resource}/", {"unexpected": "x"}, format="json").status_code == 400
    )
    assert client.get(f"/api/v1/{resource}/?search=x&search=y").status_code == 400
    assert client.get(f"/api/v1/{resource}/?status=INVALID").status_code == 400
    assert client.get(f"/api/v1/{resource}/{uuid.uuid4()}/").status_code == 404
