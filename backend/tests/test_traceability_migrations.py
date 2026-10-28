"""A block-1 upgrade must not invent provenance for legacy terminal boxes."""

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


@pytest.mark.django_db(transaction=True)
def test_block_two_upgrade_preserves_legacy_status_without_fabricated_history():
    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    old = [
        ("boxes", "0002_box_box_status_allowed_box_box_priority_allowed"),
        ("accounts", "0002_user_branch_user_user_branch_requires_company"),
        ("catalog", "0002_product_product_status_allowed"),
        ("organizations", "0002_branch_branch_status_allowed_and_more"),
    ]
    try:
        executor.migrate(old)
        apps = executor.loader.project_state(old).apps
        company = apps.get_model("organizations", "Company").objects.create(name="B1 upgrade")
        branch = apps.get_model("organizations", "Branch").objects.create(
            company=company, name="Legacy branch"
        )
        category = apps.get_model("catalog", "Category").objects.create(company=company, name="Old")
        product = apps.get_model("catalog", "Product").objects.create(
            company=company, category=category, sku="UPGRADE-B2", name="Legacy goods"
        )
        actor = apps.get_model("accounts", "User").objects.create(
            email="legacy-b2@example.test", password="!", company=company, role="OPERATOR"
        )
        before = {}
        for status in ["REGISTERED", "RECEIVED", "REJECTED"]:
            box = apps.get_model("boxes", "Box").objects.create(
                company=company,
                branch=branch,
                product=product,
                created_by=actor,
                quantity=7,
                status=status,
            )
            before[box.pk] = (box.internal_id, box.qr_code, box.status, box.created_by_id)
        MigrationExecutor(connection).migrate(latest)
        current = MigrationExecutor(connection).loader.project_state(latest).apps
        assert current.get_model("boxes", "Receipt").objects.count() == 0
        assert current.get_model("boxes", "BoxEvent").objects.count() == 0
        for box in current.get_model("boxes", "Box").objects.all():
            assert (box.internal_id, box.qr_code, box.status, box.created_by_id) == before[box.pk]
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tgname FROM pg_trigger WHERE NOT tgisinternal "
                "AND tgname IN ('boxes_receipt_immutable', 'boxes_event_immutable')"
            )
            assert {row[0] for row in cursor.fetchall()} == {
                "boxes_receipt_immutable",
                "boxes_event_immutable",
            }
    finally:
        MigrationExecutor(connection).migrate(latest)
