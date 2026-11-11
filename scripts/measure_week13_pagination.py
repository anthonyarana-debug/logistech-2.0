"""Measure list-query count from the synthetic Week 13 application container."""

import json

from apps.accounts.models import User
from apps.catalog.views import CategoryViewSet
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIRequestFactory, force_authenticate

user = User.objects.get(email="admin.week13@example.test")
view = CategoryViewSet.as_view({"get": "list"})
factory = APIRequestFactory()


def fetch(size):
    request = factory.get(
        "/api/v1/categories/", {"page_size": size}, secure=True, HTTP_HOST="localhost"
    )
    force_authenticate(request, user=user)
    response = view(request)
    response.render()
    if response.status_code != 200:
        raise RuntimeError(f"List request returned {response.status_code}.")
    return response.data


fetch(1)
stats = []
for size in (1, 25):
    with CaptureQueriesContext(connection) as context:
        result = fetch(size)
    stats.append(
        {"page_size": size, "rows": len(result["results"]), "queries": len(context)}
    )
print(json.dumps(stats, indent=2))
