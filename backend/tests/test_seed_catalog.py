from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.catalog.management.commands.seed_catalog import CATALOG
from apps.catalog.models import Category, Product

pytestmark = pytest.mark.django_db


def test_seed_catalog_creates_types_with_distinct_codes_and_is_idempotent(company):
    call_command("seed_catalog", "--company", company.name, stdout=StringIO())
    call_command("seed_catalog", "--company", str(company.pk), stdout=StringIO())
    assert Category.objects.filter(company=company).count() == len(CATALOG)
    assert Product.objects.filter(company=company).count() == 3 * len(CATALOG)
    fragile = Category.objects.get(company=company, name="Cerámica y vidrio")
    assert fragile.is_fragile and not fragile.is_perishable
    assert Category.objects.get(company=company, name="Alimentos perecibles").is_perishable
    for product in Product.objects.filter(company=company).select_related("category"):
        prefix = next(p for n, p, *_ in CATALOG if n == product.category.name)
        assert product.sku.startswith(prefix + "-")


def test_seed_catalog_keeps_existing_category(company):
    Category.objects.create(company=company, name="muebles", description="Propia")
    call_command("seed_catalog", "--company", company.name, stdout=StringIO())
    assert Category.objects.get(company=company, name__iexact="muebles").description == "Propia"


def test_seed_catalog_requires_existing_company(db):
    with pytest.raises(CommandError):
        call_command("seed_catalog", "--company", "No existe")
