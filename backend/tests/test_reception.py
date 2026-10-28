"""Receipt boundary, tenant privacy, history, atomicity and PostgreSQL locking."""

import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, connection, connections, transaction
from psycopg.errors import DeadlockDetected, SerializationFailure
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.boxes.models import Box, BoxEvent, Receipt
from tests.test_crud import scope as crud_scope

pytestmark = pytest.mark.django_db
scope = crud_scope


def client_for(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")
    return client


def payload(scope, **extra):
    return {
        "box": str(scope.boxa.pk),
        "branch": str(scope.ba.pk),
        "result": "RECEIVED",
        "reason": "",
        **extra,
    }


def post(client, scope, key=None, **extra):
    return client.post(
        "/api/v1/receipts/",
        payload(scope, **extra),
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(key or uuid.uuid4()),
    )


def test_receipt_replay_conflicts_and_history(scope):
    client = client_for(scope.operator)
    key = uuid.uuid4()
    created = post(client, scope, key)
    assert created.status_code == 201, created.data
    assert created["Cache-Control"] == "no-store"
    assert created.json()["actor"] == str(scope.operator.pk)
    assert created.json()["company"] == str(scope.a.pk)
    assert "idempotency_key" not in created.data
    repeated = post(client, scope, key)
    assert repeated.status_code == 200 and repeated.data == created.data
    assert repeated["Idempotent-Replayed"] == "true"
    assert post(client, scope, key, result="REJECTED", reason="DAMAGED").status_code == 409
    assert post(client, scope).status_code == 409
    scope.boxa.refresh_from_db()
    assert scope.boxa.status == "RECEIVED"
    assert Receipt.objects.count() == BoxEvent.objects.count() == 1
    event = BoxEvent.objects.get()
    assert event.event_type == "RECEIPT_RECORDED" and event.data["source"] == "RECEIPT_API"


@pytest.mark.parametrize(
    "extra",
    [
        {"actor": "spoof"},
        {"company": "spoof"},
        {"reason": "OTHER"},
        {"result": "REJECTED"},
        {"result": "REGISTERED"},
        {"reason": "free text"},
    ],
)
def test_strict_request(scope, extra):
    assert post(client_for(scope.operator), scope, **extra).status_code == 400
    assert not Receipt.objects.exists()


@pytest.mark.parametrize("body", [[], ["box"], "text", 42, None])
def test_non_object_json_rejected(scope, body):
    response = client_for(scope.operator).post(
        "/api/v1/receipts/",
        body,
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
    )
    assert response.status_code == 400
    assert response["Cache-Control"] == "no-store"
    assert not Receipt.objects.exists()


def test_malformed_json_and_post_filters_rejected(scope):
    client = client_for(scope.operator)
    malformed = client.post(
        "/api/v1/receipts/",
        '{"box":',
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
    )
    assert malformed.status_code == 400
    filtered = client.post(
        "/api/v1/receipts/?box=bad",
        payload(scope),
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
    )
    assert filtered.status_code == 400
    assert filtered["Cache-Control"] == malformed["Cache-Control"] == "no-store"


def test_uuid_key_required_and_rejected_reason(scope):
    client = client_for(scope.operator)
    for key in (None, "bad", ""):
        headers = {} if key is None else {"HTTP_IDEMPOTENCY_KEY": key}
        response = client.post("/api/v1/receipts/", payload(scope), format="json", **headers)
        assert response.status_code == 400 and response["Cache-Control"] == "no-store"
    response = post(client, scope, result="REJECTED", reason="DAMAGED")
    assert response.status_code == 201 and response.data["reason"] == "DAMAGED"


@pytest.mark.parametrize("role", ["operator", "admin", "root"])
def test_permitted_receivers(scope, role):
    assert post(client_for(getattr(scope, role)), scope).status_code == 201


def test_scope_branch_and_inactive_denials(scope):
    assert post(client_for(scope.other), scope).status_code == 404
    assert post(client_for(scope.unassigned), scope).status_code == 403
    assert post(client_for(scope.operator), scope, branch=str(scope.bb.pk)).status_code == 409
    scope.pa.status = "INACTIVE"
    scope.pa.save()
    assert post(client_for(scope.operator), scope).status_code == 409
    assert not Receipt.objects.exists()


def test_inactive_company_denied(scope):
    scope.a.status = "INACTIVE"
    scope.a.save()
    assert post(client_for(scope.operator), scope).status_code == 403
    assert post(client_for(scope.root), scope).status_code == 409


def test_inactive_actor_and_branch_denied(scope):
    client = client_for(scope.operator)
    scope.operator.is_active = False
    scope.operator.save()
    assert post(client, scope).status_code == 401
    scope.ba.status = "INACTIVE"
    scope.ba.save()
    assert post(client_for(scope.admin), scope).status_code == 409
    assert not Receipt.objects.exists()


def test_readonly_scoped_collections_and_strict_filters(scope):
    client = client_for(scope.operator)
    receipt = post(client, scope).data
    for resource in ("receipts", "box-events"):
        url = f"/api/v1/{resource}/"
        assert client_for(scope.other).get(url).data == []
        assert len(client.get(url).data) == 1
        assert client.get(url, {"company": str(scope.b.pk)}).status_code == 403
        for query in (
            {"unknown": "x"},
            {"box": "bad"},
            {"company": [str(scope.a.pk), str(scope.b.pk)]},
        ):
            assert client.get(url, query).status_code == 400
        row = client.get(url).data[0]
        detail = f"{url}{row['id']}/"
        assert client.get(detail).status_code == 200
        assert client_for(scope.other).get(detail).status_code == 404
        for method in (client.patch, client.put, client.delete):
            assert method(detail, {}, format="json").status_code == 405
    assert client.get("/api/v1/receipts/", {"result": "INVALID"}).status_code == 400
    assert client.get("/api/v1/box-events/", {"event_type": "INVALID"}).status_code == 400
    assert client.get(f"/api/v1/receipts/{receipt['id']}/?box={scope.boxa.pk}").status_code == 400
    assert client.post("/api/v1/box-events/", {}, format="json").status_code == 405


def test_box_crud_history_survives_deletion(scope):
    client = client_for(scope.admin)
    created = client.post(
        "/api/v1/boxes/",
        {"product": str(scope.pa.pk), "branch": str(scope.ba.pk), "quantity": 2},
        format="json",
    )
    assert created.status_code == 201
    box_id = created.data["id"]
    url = f"/api/v1/boxes/{box_id}/"
    assert client.patch(url, {"quantity": 4}, format="json").status_code == 200
    assert client.delete(url).status_code == 204
    events = list(
        BoxEvent.objects.filter(box=box_id)
        .order_by("created_at")
        .values_list("event_type", flat=True)
    )
    assert events == ["BOX_CREATED", "BOX_UPDATED", "BOX_DELETED"]
    assert not Box.objects.filter(pk=box_id).exists()


@pytest.mark.parametrize("result", ["RECEIVED", "REJECTED"])
def test_legacy_status_routes_through_receipt(scope, result):
    response = client_for(scope.operator).patch(
        f"/api/v1/boxes/{scope.boxa.pk}/", {"status": result}, format="json"
    )
    assert response.status_code == 200, response.data
    receipt = Receipt.objects.get()
    assert receipt.source == "BOX_STATUS_UPDATE"
    assert receipt.reason == ("OTHER" if result == "REJECTED" else "")
    assert BoxEvent.objects.count() == 1


def test_legacy_terminal_box_has_no_invented_history(scope):
    scope.boxa.status = "RECEIVED"
    scope.boxa.save()
    client = client_for(scope.operator)
    response = client.patch(
        f"/api/v1/boxes/{scope.boxa.pk}/", {"status": "RECEIVED"}, format="json"
    )
    assert response.status_code == 200
    assert not Receipt.objects.exists() and not BoxEvent.objects.exists()
    assert post(client, scope).status_code == 409


def test_receipt_failure_rolls_back_status_and_history(scope):
    with patch("apps.boxes.reception.record_event", side_effect=RuntimeError("event write failed")):
        response = post(client_for(scope.operator), scope)
    assert response.status_code == 500
    assert response.json() == {"detalle": "Internal service error."}
    assert response["Cache-Control"] == "no-store"
    assert "event write failed" not in response.content.decode()
    scope.boxa.refresh_from_db()
    assert scope.boxa.status == "REGISTERED"
    assert not Receipt.objects.exists() and not BoxEvent.objects.exists()


@pytest.mark.parametrize("legacy", [False, True])
@pytest.mark.parametrize("cause_type", [DeadlockDetected, SerializationFailure, None])
def test_transaction_conflicts_are_safe_and_atomic(scope, legacy, cause_type):
    failure = OperationalError("private database message")
    if cause_type:
        failure.__cause__ = cause_type("private SQL and transaction detail")
    client = client_for(scope.operator)
    with patch("apps.boxes.reception.record_event", side_effect=failure):
        if legacy:
            response = client.patch(
                f"/api/v1/boxes/{scope.boxa.pk}/", {"status": "RECEIVED"}, format="json"
            )
        else:
            response = post(client, scope)
    assert response.status_code == (409 if cause_type else 500)
    assert response["Cache-Control"] == "no-store"
    text = response.content.decode()
    assert "private" not in text and "SQL" not in text
    if cause_type:
        assert "same idempotency key" in text
    else:
        assert response.json() == {"detalle": "Internal service error."}
    scope.boxa.refresh_from_db()
    assert scope.boxa.status == "REGISTERED"
    assert not Receipt.objects.exists() and not BoxEvent.objects.exists()


def test_history_model_queryset_and_sql_are_immutable(scope):
    post(client_for(scope.operator), scope)
    for model in (Receipt, BoxEvent):
        row = model.objects.get()
        with pytest.raises(ValidationError):
            row.save()
        with pytest.raises(ValidationError):
            row.delete()
        with pytest.raises(ValidationError):
            model.objects.all().delete()
        with pytest.raises(ValidationError):
            model.objects.all().update(internal_id="tampered")
        if connection.vendor == "postgresql":
            for statement in (
                f"UPDATE {model._meta.db_table} SET internal_id = 'tampered'",
                f"DELETE FROM {model._meta.db_table}",
            ):
                with (
                    pytest.raises(IntegrityError),
                    transaction.atomic(),
                    connection.cursor() as cursor,
                ):
                    cursor.execute(statement)
    # Historical actors can be reassigned after receipt without rewriting history.
    scope.operator.company = scope.b
    scope.operator.save()
    assert Receipt.objects.get().company_id == scope.a.pk


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("same_key", [False, True])
def test_concurrent_different_actors_finalize_once(scope, same_key):
    if connection.vendor != "postgresql":
        pytest.skip("Requires real PostgreSQL row locks")
    barrier = Barrier(2)
    shared_key = uuid.uuid4()

    def worker(user_id):
        connections.close_all()
        try:
            user = User.objects.get(pk=user_id)
            barrier.wait(timeout=10)
            return post(
                client_for(user), scope, shared_key if same_key else uuid.uuid4()
            ).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(worker, [scope.operator.pk, scope.admin.pk]))
    assert sorted(results) == [201, 409]
    assert Receipt.objects.count() == 1
    assert BoxEvent.objects.filter(event_type="RECEIPT_RECORDED").count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_same_actor_idempotent_replay(scope):
    if connection.vendor != "postgresql":
        pytest.skip("Requires real PostgreSQL row locks")
    barrier = Barrier(2)
    key = uuid.uuid4()

    def worker(_):
        connections.close_all()
        try:
            barrier.wait(timeout=10)
            return post(client_for(scope.operator), scope, key).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(worker, range(2)))
    assert sorted(results) == [200, 201]
    assert Receipt.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_same_actor_key_different_boxes_conflicts(scope):
    if connection.vendor != "postgresql":
        pytest.skip("Requires real PostgreSQL row locks")
    second = Box.objects.create(
        company=scope.a,
        product=scope.pa,
        branch=scope.ba,
        created_by=scope.operator,
        quantity=2,
    )
    barrier = Barrier(2)
    key = uuid.uuid4()

    def worker(box_id):
        connections.close_all()
        try:
            barrier.wait(timeout=10)
            return post(client_for(scope.operator), scope, key, box=str(box_id)).status_code
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(worker, [scope.boxa.pk, second.pk]))
    assert sorted(results) == [201, 409]
    assert Receipt.objects.count() == 1
    assert BoxEvent.objects.count() == 1
    assert Box.objects.filter(company=scope.a, status="REGISTERED").count() == 1
