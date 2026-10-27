"""Introspección de esquema e integridad F5, sin datos personales o secretos."""

import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.db import connection  # noqa: E402
from django.db.models import F  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from apps.boxes.models import Box  # noqa: E402
from apps.catalog.models import Category, Product  # noqa: E402
from apps.organizations.models import Branch, Company  # noqa: E402

assert connection.vendor == "postgresql"
models = [Company, User, Branch, Category, Product, Box]
result = {"vendor": connection.vendor, "esquema": {}, "inconsistencias": {}}
with connection.cursor() as cursor:
    for model in models:
        constraints = connection.introspection.get_constraints(cursor, model._meta.db_table)
        result["esquema"][model.__name__.upper()] = {
            "tabla": model._meta.db_table,
            "columnas": [f.column for f in model._meta.local_fields],
            "restricciones": {
                name: {
                    key: value
                    for key, value in item.items()
                    if key in ("columns", "primary_key", "unique", "foreign_key", "check")
                }
                for name, item in constraints.items()
            },
        }
    cursor.execute("SELECT conname FROM pg_constraint WHERE NOT convalidated")
    result["constraints_no_validados"] = [row[0] for row in cursor.fetchall()]
    cursor.execute("SHOW max_connections")
    result["postgres_max_connections"] = cursor.fetchone()[0]
result["inconsistencias"] = {
    "producto_categoria": Product.objects.exclude(company_id=F("category__company_id")).count(),
    "caja_producto": Box.objects.exclude(company_id=F("product__company_id")).count(),
    "caja_sucursal": Box.objects.exclude(company_id=F("branch__company_id")).count(),
    "cantidad_no_positiva": Box.objects.filter(quantity__lte=0).count(),
}
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(
    bool(result["constraints_no_validados"]) or any(result["inconsistencias"].values())
)
