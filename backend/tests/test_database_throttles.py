from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from io import StringIO
from threading import Barrier, Event
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.db import OperationalError, close_old_connections, connection, transaction
from django.test import override_settings
from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from apps.accounts.throttles import LoginIdentityThrottle, LoginIPThrottle
from apps.core.messages import message
from apps.core.models import ThrottleWindow

pytestmark = [pytest.mark.integration, pytest.mark.django_db(transaction=True)]


def request(ip="192.0.2.123", **headers):
    return Request(
        APIRequestFactory().post(
            "/", {"email": "private@example.invalid"}, format="json", REMOTE_ADDR=ip, **headers
        ),
        parsers=[JSONParser()],
    )


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_quota_is_atomic_across_independent_connections():
    assert connection.vendor == "postgresql"
    barrier = Barrier(12)

    def consume(_):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return LoginIPThrottle().allow_request(request(), None)
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(consume, range(12)))
    assert sum(results) == 5
    window = ThrottleWindow.objects.get()
    assert len(window.history) == 5
    assert len(window.key) == 64
    assert "192.0.2.123" not in window.key


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_sliding_window_keeps_exact_expiry_and_wait():
    for stamp in (100, 101, 102, 103, 104):
        throttle = LoginIPThrottle()
        throttle.timer = lambda: stamp
        assert throttle.allow_request(request(), None)
    blocked = LoginIPThrottle()
    blocked.timer = lambda: 159
    assert not blocked.allow_request(request(), None)
    assert blocked.wait() == 1
    retry = LoginIPThrottle()
    retry.timer = lambda: 160
    assert retry.allow_request(request(), None)
    assert ThrottleWindow.objects.get().history == [160, 104, 103, 102, 101]


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_quota_never_falls_back_to_allow_on_database_failure():
    with patch("django.db.models.query.QuerySet.get_or_create", side_effect=OperationalError):
        with pytest.raises(OperationalError):
            LoginIPThrottle().allow_request(request(), None)


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_failure_returns_existing_generic_api_error(client):
    with patch(
        "django.db.models.query.QuerySet.get_or_create",
        side_effect=OperationalError("sensitive-details"),
    ):
        response = client.get("/api/v1/auth/csrf/")
    assert response.status_code == 500
    assert response.json() == {"detalle": message("internal_service_error")}


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_limit_preserves_api_429_and_retry_after(client):
    for _ in range(60):
        assert client.get("/api/v1/auth/csrf/").status_code == 200
    response = client.get("/api/v1/auth/csrf/")
    assert response.status_code == 429
    assert response.json() == {"detalle": message("too_many_requests_please_try_again_later")}
    assert 1 <= int(response["Retry-After"]) <= 60


@override_settings(USE_DATABASE_THROTTLE=True)
def test_database_identity_window_uses_full_fifteen_minutes():
    for _ in range(10):
        throttle = LoginIdentityThrottle()
        throttle.timer = lambda: 100
        assert throttle.allow_request(request(), None)
    denied = LoginIdentityThrottle()
    denied.timer = lambda: 999
    assert not denied.allow_request(request(), None)
    assert denied.wait() == 1
    retry = LoginIdentityThrottle()
    retry.timer = lambda: 1000
    assert retry.allow_request(request(), None)
    assert "private" not in ThrottleWindow.objects.get().key


def test_single_trusted_proxy_uses_overwritten_forwarded_address():
    throttle = LoginIPThrottle()
    with override_settings(REST_FRAMEWORK={"NUM_PROXIES": 1}):
        assert throttle.get_ident(request(HTTP_X_FORWARDED_FOR="198.51.100.7")) == "198.51.100.7"
        assert (
            throttle.get_ident(request(HTTP_X_FORWARDED_FOR="forged, 198.51.100.7"))
            == "198.51.100.7"
        )
    with override_settings(REST_FRAMEWORK={"NUM_PROXIES": 0}):
        assert throttle.get_ident(request(HTTP_X_FORWARDED_FOR="forged")) == "192.0.2.123"


def test_cleanup_deletes_only_expired_windows(user):
    now = timezone.now()
    ThrottleWindow.objects.create(key="expired", expires_at=now - timedelta(seconds=1))
    ThrottleWindow.objects.create(key="active", expires_at=now + timedelta(hours=1))
    call_command("cleanup_throttles", stdout=StringIO())
    assert list(ThrottleWindow.objects.values_list("key", flat=True)) == ["active"]
    user.refresh_from_db()


def test_cleanup_skips_window_locked_by_concurrent_quota_refresh():
    expired = timezone.now() - timedelta(seconds=1)
    ThrottleWindow.objects.create(key="refreshing", expires_at=expired)
    ThrottleWindow.objects.create(key="expired", expires_at=expired)
    locked, release = Event(), Event()

    def refresh():
        close_old_connections()
        try:
            with transaction.atomic():
                window = ThrottleWindow.objects.select_for_update().get(key="refreshing")
                locked.set()
                assert release.wait(timeout=10)
                window.expires_at = timezone.now() + timedelta(minutes=1)
                window.save(update_fields=["expires_at"])
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(refresh)
        try:
            assert locked.wait(timeout=10)
            call_command("cleanup_throttles", stdout=StringIO())
            assert list(ThrottleWindow.objects.values_list("key", flat=True)) == ["refreshing"]
        finally:
            release.set()
        future.result(timeout=10)
    call_command("cleanup_throttles", stdout=StringIO())
    assert ThrottleWindow.objects.filter(key="refreshing").exists()
