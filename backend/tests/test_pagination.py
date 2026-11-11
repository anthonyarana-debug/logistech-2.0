import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import Category
from apps.organizations.models import Company

URL = "/api/v1/categories/"


@pytest.fixture
def collection(db):
    own = Company.objects.create(name="Pagination tenant")
    other = Company.objects.create(name="Other tenant")
    actor = User.objects.create_user(email="pagination@example.test", company=own)
    rows = [Category.objects.create(company=own, name=f"Demo {i}") for i in range(5)]
    Category.objects.create(company=other, name="Demo outside tenant")
    client = APIClient()
    client.force_authenticate(actor)
    return client, rows, other


def test_pagination_preserves_legacy_and_scopes_before_counting(collection):
    client, rows, other = collection
    assert len(client.get(URL).json()) == 5
    first = client.get(URL, {"page_size": 2, "search": "Demo"}).json()
    assert first["count"] == 5
    assert first["previous"] is None
    assert [row["id"] for row in first["results"]] == [str(row.pk) for row in rows[:2]]
    second = client.get(first["next"]).json()
    assert [row["id"] for row in second["results"]] == [str(row.pk) for row in rows[2:4]]
    assert second["previous"]
    newest = client.get(URL, {"page_size": 1, "order": "newest"}).json()
    assert newest["results"][0]["id"] == str(rows[-1].pk)
    assert client.get(URL, {"page": 1, "company": str(other.pk)}).status_code == 403


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("page=1&page=2", 400),
        ("page_size=101", 400),
        ("page_size=0", 400),
        ("page=abc", 400),
        ("page=0", 400),
        ("page=999", 404),
        ("order=random&page=1", 400),
    ],
)
def test_invalid_pagination(collection, query, expected):
    client, _, _ = collection
    assert client.get(f"{URL}?{query}").status_code == expected


def test_empty_filtered_page(collection):
    client, rows, _ = collection
    result = client.get(URL, {"page": 1, "search": "no matching records"}).json()
    assert result == {"count": 0, "next": None, "previous": None, "results": []}
    assert client.get(f"{URL}{rows[0].pk}/?page=1").status_code == 400
