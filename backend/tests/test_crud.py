import json
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, connections, transaction
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company

pytestmark = pytest.mark.django_db


@pytest.fixture
def scope():
    # Passwords inutilizables en fixtures JWT; las pruebas de login mantienen PBKDF2 real.
    a = Company.objects.create(name="Empresa A")
    b = Company.objects.create(name="Empresa B")
    admin = User.objects.create_user("admin-a@example.test", role="COMPANY_ADMIN", company=a)
    operator = User.objects.create_user("operador-a@example.test", company=a)
    other = User.objects.create_user("operador-b@example.test", company=b)
    root = User.objects.create_superuser("root-crud@example.test")
    unassigned = User.objects.create_user("sin-asignacion@example.test")
    ca = Category.objects.create(company=a, name="Categoría A", is_fragile=True)
    cb = Category.objects.create(company=b, name="Secreto B", is_perishable=True)
    pa = Product.objects.create(company=a, category=ca, sku="SKU-A", name="Producto A")
    pb = Product.objects.create(company=b, category=cb, sku="SKU-B", name="Secreto B")
    ba = Branch.objects.create(company=a, name="Sede A")
    bb = Branch.objects.create(company=b, name="Sede B")
    boxa = Box.objects.create(company=a, product=pa, branch=ba, created_by=operator, quantity=3)
    boxb = Box.objects.create(company=b, product=pb, branch=bb, created_by=other, quantity=7)
    return SimpleNamespace(**locals())


def auth(client, user):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")


def body(s, **extra):
    return {"product": str(s.pa.pk), "branch": str(s.ba.pk), "quantity": 4, **extra}


def detail(kind, record):
    return f"/api/v1/{kind}/{record.pk}/"


@pytest.mark.parametrize("kind", ["categories", "boxes"])
def test_collections_require_login_and_assigned_company(client, scope, kind):
    url = f"/api/v1/{kind}/"
    assert client.get(url).status_code == 401
    auth(client, scope.unassigned)
    for method in (client.get, client.post):
        assert method(url, {}, format="json").status_code == 403
    auth(client, scope.operator)
    result = client.get(url)
    assert result.status_code == 200 and len(result.json()) == 1
    assert result.json()[0]["company"] == str(scope.a.pk)
    assert result["Cache-Control"] == "no-store"
    auth(client, scope.root)
    assert len(client.get(url).json()) == 2


@pytest.mark.parametrize("role", ["admin", "root"])
def test_category_crud_admin_and_superadmin(client, scope, role):
    auth(client, getattr(scope, role))
    data = {
        "name": " Nueva ",
        "description": "Descripción",
        "is_fragile": True,
        "is_perishable": True,
    }
    if role == "root":
        data["company"] = str(scope.a.pk)
    created = client.post("/api/v1/categories/", data, format="json")
    assert created.status_code == 201, created.json()
    category = Category.objects.get(pk=created.json()["id"])
    assert category.name == "Nueva" and category.company == scope.a
    assert category.is_fragile and category.is_perishable
    url = detail("categories", category)
    assert client.get(url).status_code == 200
    assert client.put(url, {"name": "Renombrada"}, format="json").status_code == 200
    assert client.patch(url, {"description": "Editada"}, format="json").status_code == 200
    deleted = client.delete(url)
    assert deleted.status_code == 204 and not deleted.content
    assert client.get(url).status_code == 404


def test_operator_cannot_administer_categories(client, scope):
    auth(client, scope.operator)
    assert (
        client.post("/api/v1/categories/", {"name": "Prohibida"}, format="json").status_code == 403
    )
    for method in (client.put, client.patch, client.delete):
        assert method(detail("categories", scope.ca), {}, format="json").status_code == 403


@pytest.mark.parametrize("role", ["admin", "operator", "root"])
def test_box_create_read_put_patch_and_server_identifiers(client, scope, role):
    actor = getattr(scope, role)
    auth(client, actor)
    data = body(scope, weight_kg="1.250", priority="HIGH")
    if role == "root":
        data["company"] = str(scope.a.pk)
    created = client.post("/api/v1/boxes/", data, format="json")
    assert created.status_code == 201, created.json()
    box = Box.objects.get(pk=created.json()["id"])
    assert box.created_by == actor and box.company == scope.a
    assert created.json()["product_name"] == scope.pa.name
    assert created.json()["branch_name"] == scope.ba.name
    assert box.internal_id.startswith("CJ-") and len(box.internal_id) == 35
    assert box.qr_code != box.pk
    url = detail("boxes", box)
    assert client.get(url).status_code == 200
    assert client.put(url, body(scope, quantity=8), format="json").status_code == 200
    assert (
        client.patch(url, {"weight_kg": None, "priority": "LOW"}, format="json").status_code == 200
    )
    box.refresh_from_db()
    assert box.quantity == 8 and box.weight_kg is None and box.created_by == actor


@pytest.mark.parametrize("kind", ["categories", "boxes"])
@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_other_company_detail_is_404(client, scope, kind, method):
    auth(client, scope.admin)
    record = scope.cb if kind == "categories" else scope.boxb
    response = getattr(client, method)(detail(kind, record), {}, format="json")
    assert response.status_code == 404
    record.refresh_from_db()
    assert record.company == scope.b


@pytest.mark.parametrize("key", ["product", "branch"])
def test_foreign_or_missing_box_reference_same_safe_error(client, scope, key):
    auth(client, scope.operator)
    foreign = scope.pb if key == "product" else scope.bb
    for value in [str(foreign.pk), str(uuid.uuid4())]:
        response = client.post("/api/v1/boxes/", body(scope, **{key: value}), format="json")
        assert response.status_code == 400
    response = client.patch(detail("boxes", scope.boxa), {key: str(foreign.pk)}, format="json")
    assert response.status_code == 400
    assert Box.objects.filter(company=scope.a).count() == 1
    scope.boxa.refresh_from_db()
    assert scope.boxa.product == scope.pa and scope.boxa.branch == scope.ba


@pytest.mark.parametrize(
    "field,value",
    [
        ("company", "foreign"),
        ("created_by", "foreign"),
        ("internal_id", "CJ-MANIPULADO"),
        ("qr_code", "foreign"),
        ("id", "foreign"),
        ("created_at", "2020-01-01"),
        ("category", "foreign"),
        ("product__company", "foreign"),
        ("product_name", "Manipulado"),
    ],
)
def test_box_rejects_mass_assignment_even_on_own_resource(client, scope, field, value):
    auth(client, scope.admin)
    data = {field: str(scope.b.pk) if value == "foreign" else value}
    assert client.post("/api/v1/boxes/", body(scope, **data), format="json").status_code == 400
    assert client.patch(detail("boxes", scope.boxa), data, format="json").status_code == 400


def test_company_readonly_for_admin_even_when_equal_and_for_super_update(client, scope):
    auth(client, scope.admin)
    assert (
        client.post(
            "/api/v1/categories/", {"name": "Nueva", "company": str(scope.a.pk)}, format="json"
        ).status_code
        == 400
    )
    auth(client, scope.root)
    assert client.post("/api/v1/categories/", {"name": "Nueva"}, format="json").status_code == 400
    assert (
        client.patch(
            detail("boxes", scope.boxa), {"company": str(scope.b.pk)}, format="json"
        ).status_code
        == 400
    )
    assert (
        client.patch(
            detail("categories", scope.ca), {"company": str(scope.b.pk)}, format="json"
        ).status_code
        == 400
    )


def test_superadmin_explicit_scope_and_reference_integrity(client, scope):
    auth(client, scope.root)
    assert client.post("/api/v1/boxes/", body(scope), format="json").status_code == 400
    invalid = body(scope, company=str(scope.b.pk))
    assert client.post("/api/v1/boxes/", invalid, format="json").status_code == 400
    valid = body(scope, company=str(scope.b.pk), product=str(scope.pb.pk), branch=str(scope.bb.pk))
    response = client.post("/api/v1/boxes/", valid, format="json")
    assert response.status_code == 201 and response.json()["company"] == str(scope.b.pk)
    assert response.json()["created_by"] == str(scope.root.pk)


@pytest.mark.parametrize(
    "key,value",
    [
        ("quantity", 0),
        ("quantity", -1),
        ("quantity", 1.5),
        ("quantity", True),
        ("weight_kg", "0"),
        ("weight_kg", "-1"),
        ("weight_kg", "NaN"),
        ("weight_kg", "1.0001"),
        ("status", "INVALID"),
        ("status", "RECEIVED"),
        ("priority", "URGENT"),
    ],
)
def test_box_validation(client, scope, key, value):
    auth(client, scope.operator)
    assert (
        client.post("/api/v1/boxes/", body(scope, **{key: value}), format="json").status_code == 400
    )


@pytest.mark.parametrize(
    "data", [{"name": " "}, {"name": "x" * 121}, {"name": "A", "company_id": "ajena"}, []]
)
def test_category_validation(client, scope, data):
    auth(client, scope.admin)
    assert client.post("/api/v1/categories/", data, format="json").status_code == 400


def test_category_uniqueness_scope_and_protected_delete(client, scope):
    auth(client, scope.admin)
    response = client.post("/api/v1/categories/", {"name": scope.ca.name.upper()}, format="json")
    assert response.status_code == 409
    # El mismo nombre en otra empresa es válido y no revela su categoría.
    assert (
        client.post("/api/v1/categories/", {"name": scope.cb.name}, format="json").status_code
        == 201
    )
    assert client.delete(detail("categories", scope.ca)).status_code == 409
    assert Category.objects.filter(pk=scope.ca.pk).exists()


def test_box_delete_permissions_and_terminal_state(client, scope):
    auth(client, scope.operator)
    assert client.delete(detail("boxes", scope.boxa)).status_code == 403
    auth(client, scope.admin)
    deleted = client.delete(detail("boxes", scope.boxa))
    assert deleted.status_code == 204 and not deleted.content
    auth(client, scope.root)
    assert (
        client.patch(detail("boxes", scope.boxb), {"status": "RECEIVED"}, format="json").status_code
        == 200
    )
    assert client.delete(detail("boxes", scope.boxb)).status_code == 409


@pytest.mark.parametrize("terminal", ["RECEIVED", "REJECTED"])
def test_box_initial_state_transitions_and_terminal_immutability(client, scope, terminal):
    auth(client, scope.operator)
    url = detail("boxes", scope.boxa)
    assert client.patch(url, {"status": terminal}, format="json").status_code == 200
    assert client.patch(url, {"status": "REGISTERED"}, format="json").status_code == 409
    assert client.patch(url, {"quantity": 99}, format="json").status_code == 409
    scope.boxa.refresh_from_db()
    assert scope.boxa.quantity == 3 and scope.boxa.status == terminal


def test_lookup_by_internal_id_qr_and_related_filters_remains_scoped(client, scope):
    auth(client, scope.operator)
    for key, own, foreign in [
        ("internal_id", scope.boxa.internal_id, scope.boxb.internal_id),
        ("qr_code", scope.boxa.qr_code, scope.boxb.qr_code),
        ("product", scope.pa.pk, scope.pb.pk),
        ("branch", scope.ba.pk, scope.bb.pk),
        ("category", scope.ca.pk, scope.cb.pk),
    ]:
        assert len(client.get("/api/v1/boxes/", {key: str(own)}).json()) == 1
        response = client.get("/api/v1/boxes/", {key: str(foreign)})
        assert response.status_code == 200 and response.json() == []
    assert client.get("/api/v1/boxes/", {"search": "Secreto B"}).json() == []
    assert client.get("/api/v1/categories/", {"search": "Secreto B"}).json() == []
    assert len(client.get("/api/v1/categories/", {"is_fragile": "true"}).json()) == 1


@pytest.mark.parametrize(
    "query",
    [
        "company__id=ajena",
        "product__company_id=ajena",
        "unknown=1",
        "status=NO_EXISTE",
        "company=incorrecto",
        "qr_code=incorrecto",
        "internal_id=incorrecto",
        "product=1",
        "status=REGISTERED&status=RECEIVED",
        "search=",
        "ordering=company",
    ],
)
def test_unknown_malformed_and_duplicate_filters_rejected(client, scope, query):
    auth(client, scope.operator)
    assert client.get(f"/api/v1/boxes/?{query}").status_code == 400


def test_company_filter_never_expands_scope(client, scope):
    auth(client, scope.admin)
    for kind in ("categories", "boxes"):
        assert client.get(f"/api/v1/{kind}/", {"company": str(scope.b.pk)}).status_code == 403
        assert len(client.get(f"/api/v1/{kind}/", {"company": str(scope.a.pk)}).json()) == 1
    auth(client, scope.root)
    assert len(client.get("/api/v1/boxes/", {"company": str(scope.b.pk)}).json()) == 1


def test_inactive_company_and_references_denied(client, scope):
    scope.pa.status = "INACTIVE"
    scope.pa.save()
    auth(client, scope.operator)
    assert client.post("/api/v1/boxes/", body(scope), format="json").status_code == 400
    scope.a.status = "INACTIVE"
    scope.a.save()
    assert client.get("/api/v1/boxes/").status_code == 403
    auth(client, scope.root)
    assert client.get(detail("boxes", scope.boxa)).status_code == 200
    assert (
        client.patch(detail("boxes", scope.boxa), {"quantity": 2}, format="json").status_code == 409
    )


def test_current_assignment_scopes_reads_and_preserves_historical_creator(client, scope):
    auth(client, scope.operator)
    old_token = client._credentials.copy()
    scope.operator.company = scope.b
    scope.operator.save()
    client.credentials(**old_token)
    assert client.get(detail("boxes", scope.boxa)).status_code == 404
    assert len(client.get("/api/v1/boxes/").json()) == 1
    auth(client, scope.admin)
    assert (
        client.patch(detail("boxes", scope.boxa), {"quantity": 8}, format="json").status_code == 200
    )
    scope.boxa.refresh_from_db()
    assert scope.boxa.created_by == scope.operator and scope.boxa.company == scope.a


def test_external_inconsistent_reference_not_exposed_or_linked(client, scope):
    # Simula corrupción externa que omite clean; la API no sirve sus datos cruzados.
    Product.objects.filter(pk=scope.pa.pk).update(category=scope.cb)
    auth(client, scope.operator)
    assert client.get(detail("boxes", scope.boxa)).status_code == 404
    assert client.get("/api/v1/boxes/").json() == []
    assert client.post("/api/v1/boxes/", body(scope), format="json").status_code == 400


def test_identifier_collision_retried_and_exhaustion_safe(client, scope):
    auth(client, scope.operator)
    collision = uuid.UUID(scope.boxa.internal_id[3:])
    with patch("apps.boxes.models.uuid.uuid4", side_effect=[collision, uuid.uuid4()]):
        response = client.post("/api/v1/boxes/", body(scope), format="json")
    assert response.status_code == 201 and response.json()["internal_id"] != scope.boxa.internal_id
    with patch("apps.boxes.models.uuid.uuid4", return_value=collision):
        response = client.post("/api/v1/boxes/", body(scope), format="json")
    assert response.status_code == 409


@pytest.mark.parametrize("field,value", [("status", "INVENTADO"), ("priority", "INVENTADO")])
def test_postgresql_enforces_state_enumerations(scope, field, value):
    with pytest.raises(IntegrityError), transaction.atomic():
        Box.objects.filter(pk=scope.boxa.pk).update(**{field: value})


def test_private_rate_limit_is_per_user_and_recovers(client, scope):
    auth(client, scope.operator)
    with patch("rest_framework.throttling.SimpleRateThrottle.timer", return_value=1000):
        for _ in range(120):
            assert client.get("/api/v1/boxes/").status_code == 200
        limited = client.get("/api/v1/categories/")
        assert limited.status_code == 429 and int(limited["Retry-After"]) > 0
        auth(client, scope.admin)
        assert client.get("/api/v1/categories/").status_code == 200
    auth(client, scope.operator)
    with patch("rest_framework.throttling.SimpleRateThrottle.timer", return_value=1061):
        assert client.get("/api/v1/boxes/").status_code == 200


def test_private_errors_are_safe_json_even_with_debug(client, scope):
    auth(client, scope.operator)
    with (
        override_settings(DEBUG=True),
        patch(
            "apps.boxes.views.BoxViewSet.get_queryset", side_effect=RuntimeError("dato-reservado")
        ),
    ):
        response = client.get("/api/v1/boxes/")
    assert response.status_code == 500
    assert response.json() == {"detalle": "Internal service error."}
    assert b"dato-reservado" not in response.content
    assert client.get("/api/v1/boxes/uuid-invalido/").status_code == 404


@pytest.mark.parametrize("role", ["admin", "root"])
def test_registered_box_delete_allowed_for_admin_roles(client, scope, role):
    auth(client, getattr(scope, role))
    response = client.delete(detail("boxes", scope.boxa))
    assert response.status_code == 204 and not Box.objects.filter(pk=scope.boxa.pk).exists()


@pytest.mark.parametrize("method", ["get", "put", "patch", "delete"])
def test_unassigned_cannot_access_known_private_uuid(client, scope, method):
    auth(client, scope.unassigned)
    response = getattr(client, method)(detail("boxes", scope.boxa), {}, format="json")
    assert response.status_code == 403


def test_creator_is_immutable_at_model_boundary(scope):
    scope.boxa.created_by = scope.admin
    with pytest.raises(ModelValidationError):
        scope.boxa.save()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("kind", ["categories", "boxes"])
def test_concurrent_conflicting_writes_are_serialized(scope, kind):
    barrier = Barrier(2)
    actors = (scope.admin, scope.root)
    tokens = [str(AccessToken.for_user(actor)) for actor in actors]

    def write(index):
        try:
            browser = APIClient(enforce_csrf_checks=True)
            browser.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens[index]}")
            barrier.wait(timeout=10)
            if kind == "categories":
                data = {"name": "Duplicada concurrente"}
                if index:
                    data["company"] = str(scope.a.pk)
                return browser.post("/api/v1/categories/", data, format="json").status_code
            return browser.patch(
                detail("boxes", scope.boxa),
                {"status": "RECEIVED" if index else "REJECTED"},
                format="json",
            ).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        codes = list(executor.map(write, range(2)))
    assert sorted(codes) == ([201, 409] if kind == "categories" else [200, 409])


@pytest.mark.django_db(transaction=True)
def test_crud_over_real_http_in_isolated_postgresql(live_server, scope):
    records = []

    def http(method, route, expected, actor=None, data=None):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if actor:
            headers["Authorization"] = f"Bearer {AccessToken.for_user(actor)}"
        request = Request(
            live_server.url + route,
            method=method,
            data=json.dumps(data).encode() if data is not None else None,
            headers=headers,
        )
        try:
            response = urlopen(request, timeout=8)
        except HTTPError as error:
            response = error
        with response:
            content = response.read()
            result = json.loads(content) if content else None
            code = response.code
        records.append({"metodo": method, "ruta": route, "http": code, "esperado": expected})
        assert code == expected
        return result

    http("GET", "/api/v1/boxes/", 401)
    category = http("POST", "/api/v1/categories/", 201, scope.admin, {"name": "Prueba HTTP"})
    category_url = f"/api/v1/categories/{category['id']}/"
    http("GET", category_url, 200, scope.operator)
    http("PUT", category_url, 200, scope.admin, {"name": "Actualizada HTTP"})
    http("PATCH", category_url, 200, scope.admin, {"is_fragile": True})
    http("DELETE", category_url, 204, scope.admin)
    box = http("POST", "/api/v1/boxes/", 201, scope.operator, body(scope))
    box_url = f"/api/v1/boxes/{box['id']}/"
    http("GET", box_url, 200, scope.admin)
    http("PUT", box_url, 200, scope.operator, body(scope, quantity=8))
    http("PATCH", box_url, 200, scope.operator, {"priority": "HIGH"})
    http("DELETE", box_url, 403, scope.operator)
    http("GET", detail("boxes", scope.boxb), 404, scope.admin)
    http("POST", "/api/v1/boxes/", 400, scope.operator, body(scope, product=str(scope.pb.pk)))
    http("DELETE", box_url, 204, scope.admin)
    http("GET", box_url, 404, scope.admin)
    artifact = Path(tempfile.gettempdir()) / "logistech-f3-http.json"
    artifact.write_text(
        json.dumps(
            {
                "entorno": "Servidor HTTP efímero en contenedor, PostgreSQL test_ separado",
                "resultados": records,
                "datos_permanentes_creados": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
