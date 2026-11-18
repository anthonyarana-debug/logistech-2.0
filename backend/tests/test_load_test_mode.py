from io import StringIO

import pytest
from django.core.checks import run_checks
from django.core.management import call_command

from apps.accounts.models import User
from tests.conftest import PASSWORD, csrf

pytestmark = pytest.mark.django_db


def test_rate_limits_apply_by_default(client):
    csrf(client)
    for _ in range(3):
        assert client.post("/api/v1/auth/register/", {}, format="json").status_code == 400
    assert client.post("/api/v1/auth/register/", {}, format="json").status_code == 429


@pytest.mark.parametrize("database_throttle", [False, True])
def test_load_test_mode_disables_rate_limits(client, settings, database_throttle):
    settings.LOAD_TEST_MODE = True
    settings.USE_DATABASE_THROTTLE = database_throttle
    csrf(client)
    for n in range(8):
        response = client.post(
            "/api/v1/auth/register/",
            {"email": f"k6-t{n}@example.test", "password": PASSWORD},
            format="json",
        )
        assert response.status_code == 201
    assert User.objects.filter(email__startswith="k6-t").count() == 8


def test_load_test_mode_raises_deploy_warning(settings):
    settings.LOAD_TEST_MODE = True
    ids = {message.id for message in run_checks(include_deployment_checks=True)}
    assert "logistech.W010" in ids
    settings.LOAD_TEST_MODE = False
    ids = {message.id for message in run_checks(include_deployment_checks=True)}
    assert "logistech.W010" not in ids


def test_load_test_users_counts_and_deletes_only_test_accounts(company):
    for n in range(3):
        User.objects.create_user(f"k6-run1-{n}@example.test", PASSWORD)
    User.objects.create_user("k6-run1-real@empresa.pe", PASSWORD)
    User.objects.create_user("real@example.test", PASSWORD)
    User.objects.create_user(
        "k6-run1-admin@example.test", PASSWORD, role=User.Role.COMPANY_ADMIN, company=company
    )

    out = StringIO()
    call_command("load_test_users", "--prefix", "k6-run1-", stdout=out)
    assert "Users with prefix 'k6-run1-': 3" in out.getvalue()
    assert User.objects.count() == 6

    call_command("load_test_users", "--prefix", "k6-run1-", "--delete", stdout=StringIO())
    assert User.objects.count() == 3
    assert not User.objects.filter(email__startswith="k6-run1-", email__endswith="@example.test",
                                   role=User.Role.OPERATOR).exists()


def test_load_test_users_rejects_unsafe_prefix():
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("load_test_users", "--prefix", "", "--delete")
