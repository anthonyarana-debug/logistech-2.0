import uuid

import pytest

from apps.catalog.models import Product
from tests.test_crud import auth
from tests.test_crud import scope as scope_fixture

scope = scope_fixture

pytestmark = pytest.mark.django_db


def test_references_scope_and_labels(client, scope):
    auth(client, scope.operator)
    response = client.get("/api/v1/references/")
    assert response.status_code == 200
    assert response.json()["companies"] == [{"id": str(scope.a.pk), "name": scope.a.name}]
    assert response.json()["products"][0]["category_name"] == scope.ca.name
    assert {b["id"] for b in response.json()["branches"]} == {str(scope.ba.pk)}
    assert response["Cache-Control"] == "no-store"
    assert client.get("/api/v1/references/", {"company": str(scope.b.pk)}).status_code == 403


def test_references_superadmin_requires_context_for_products(client, scope):
    auth(client, scope.root)
    response = client.get("/api/v1/references/").json()
    assert len(response["companies"]) == 2 and response["products"] == []
    assert client.get("/api/v1/references/", {"company": str(scope.b.pk)}).json()["products"][0][
        "id"
    ] == str(scope.pb.pk)
    assert client.get("/api/v1/references/", {"company": str(uuid.uuid4())}).status_code == 400


def test_references_excludes_inactive_and_inconsistent(client, scope):
    auth(client, scope.admin)
    Product.objects.filter(pk=scope.pa.pk).update(status="INACTIVE")
    assert client.get("/api/v1/references/").json()["products"] == []
    Product.objects.filter(pk=scope.pa.pk).update(status="ACTIVE", category=scope.cb)
    assert client.get("/api/v1/references/").json()["products"] == []
    scope.ba.status = "INACTIVE"
    scope.ba.save()
    assert client.get("/api/v1/references/").json()["branches"] == []
    scope.a.status = "INACTIVE"
    scope.a.save()
    assert client.get("/api/v1/references/").status_code == 403


def test_references_auth_methods_and_filter_validation(client, scope):
    assert client.get("/api/v1/references/").status_code == 401
    auth(client, scope.unassigned)
    assert client.get("/api/v1/references/").status_code == 403
    auth(client, scope.admin)
    assert client.post("/api/v1/references/", {}).status_code == 405
    for query in ["company=invalid", "company__id=1", "company=a&company=b"]:
        assert client.get("/api/v1/references/?" + query).status_code == 400
