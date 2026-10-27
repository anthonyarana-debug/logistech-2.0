import pytest
from django.db import connection
from django.test import Client


@pytest.mark.integration
@pytest.mark.django_db
def test_real_postgresql_and_readiness():
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        assert "PostgreSQL" in cursor.fetchone()[0]
    response = Client().get("/api/v1/health/")
    assert response.status_code == 200
