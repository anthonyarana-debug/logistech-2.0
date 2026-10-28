"""Forward migration preserves pre-F6 business rows in a disposable PostgreSQL test DB."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_upgrade_preserves_f5_rows_and_nullable_user_branch():
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    old = [
        ("accounts", "0001_initial"),
        ("catalog", "0001_initial"),
        ("boxes", "0001_initial"),
        ("organizations", "0001_initial"),
    ]
    try:
        executor.migrate(old)
        apps = executor.loader.project_state(old).apps
        company = apps.get_model("organizations", "Company").objects.create(name="Upgrade test")
        branch = apps.get_model("organizations", "Branch").objects.create(
            company=company, name="HQ"
        )
        category = apps.get_model("catalog", "Category").objects.create(
            company=company, name="Goods"
        )
        product = apps.get_model("catalog", "Product").objects.create(
            company=company, category=category, name="Product", sku="UPGRADE"
        )
        user = apps.get_model("accounts", "User").objects.create(
            email="upgrade@example.test", password="!", role="OPERATOR", company=company
        )
        box = apps.get_model("boxes", "Box").objects.create(
            company=company, branch=branch, product=product, created_by=user, quantity=7
        )
        original = (box.internal_id, box.qr_code, box.created_by_id, box.company_id, box.quantity)
        MigrationExecutor(connection).migrate(latest)
        current = MigrationExecutor(connection).loader.project_state(latest).apps
        upgraded = current.get_model("boxes", "Box").objects.get(pk=box.pk)
        assert original == (
            upgraded.internal_id,
            upgraded.qr_code,
            upgraded.created_by_id,
            upgraded.company_id,
            upgraded.quantity,
        )
        assert current.get_model("accounts", "User").objects.get(pk=user.pk).branch_id is None
        assert (
            current.get_model("catalog", "Product").objects.get(pk=product.pk).category_id
            == category.pk
        )
    finally:
        MigrationExecutor(connection).migrate(latest)
