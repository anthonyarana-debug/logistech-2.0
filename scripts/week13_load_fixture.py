"""Seed the isolated k6 database and issue one short-lived access token per VU."""

import json
import os

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch
from django.db import connection, transaction
from rest_framework_simplejwt.tokens import AccessToken

if not os.environ.get("HOSTNAME") or os.environ.get("POSTGRES_DB") != "logistech":
    raise RuntimeError("Run this inside the dedicated load project.")
vus = int(os.environ["QA_VUS"])
rows = int(os.environ["QA_ROWS"])
if not 1 <= vus <= 20 or not 0 <= rows <= 20000:
    raise ValueError("Fixture exceeds the local budget.")

with transaction.atomic():
    admin = User.objects.get(email="admin.week13-load@example.test")
    company = admin.company
    Category.objects.bulk_create(
        [Category(company=company, name=f"Week 13 sample {i:05}") for i in range(rows)],
        batch_size=500,
    )
    users = [admin]
    for i in range(1, vus):
        users.append(
            User.objects.create_user(
                email=f"vu-{i}.week13-load@example.test",
                company=company,
                role=admin.role,
            )
        )

query = Category.objects.filter(company=company).order_by("created_at", "id")
with connection.cursor() as cursor:
    cursor.execute("ANALYZE catalog_category")
plans = {}
for label, offset in (("first", 0), ("deep", max(rows - 25, 0))):
    plans[label] = json.loads(
        query[offset : offset + 25].explain(analyze=True, buffers=True, format="JSON")
    )
print(
    json.dumps(
        {
            "access": [str(AccessToken.for_user(user)) for user in users],
            "product": str(Product.objects.filter(company=company).first().pk),
            "branch": str(Branch.objects.filter(company=company).first().pk),
            "category_count": query.count(),
            "plans": plans,
        }
    )
)
