"""Read-only production-role/TLS/restore manifest. Run inside the isolated backend."""

import hashlib
import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
import django

django.setup()
from apps.accounts.models import User
from apps.boxes.models import Box, BoxEvent, Receipt
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models import F

manifests = {}
for model in (Company, Branch, User, Category, Product, Box, Receipt, BoxEvent):
    rows = list(model.objects.order_by("pk").values())
    # Even password hashes remain in memory only; output is one aggregate digest.
    digest = hashlib.sha256(
        json.dumps(rows, sort_keys=True, cls=DjangoJSONEncoder).encode()
    ).hexdigest()
    manifests[model._meta.label] = {"count": len(rows), "sha256": digest}
with connection.cursor() as cursor:
    cursor.execute("SELECT ssl,version FROM pg_stat_ssl WHERE pid=pg_backend_pid()")
    tls, protocol = cursor.fetchone()
    cursor.execute(
        "SELECT rolsuper,rolcreatedb,rolcreaterole FROM pg_roles WHERE rolname=current_user"
    )
    privileged = list(cursor.fetchone())
    cursor.execute("SELECT has_schema_privilege(current_user,'public','CREATE')")
    schema_create = cursor.fetchone()[0]
    cursor.execute(
        "SELECT has_table_privilege(current_user,'boxes_boxevent','TRUNCATE')"
    )
    truncate = cursor.fetchone()[0]
    cursor.execute(
        "SELECT tgname,tgenabled FROM pg_trigger WHERE NOT tgisinternal AND "
        "tgname IN ('boxes_receipt_immutable','boxes_event_immutable') ORDER BY tgname"
    )
    triggers = dict(cursor.fetchall())
invalid = Receipt.objects.exclude(box__company_id=F("company_id")).count()
report = {
    "database": connection.settings_dict["NAME"],
    "tls": tls,
    "tls_protocol": protocol,
    "sslmode": connection.settings_dict["OPTIONS"]["sslmode"],
    "runtime_superuser_createdb_createrole": privileged,
    "runtime_schema_create": schema_create,
    "runtime_history_truncate": truncate,
    "history_triggers": triggers,
    "invalid_receipt_company": invalid,
    "business_manifest": manifests,
}
print(json.dumps(report, indent=2))
assert tls and report["sslmode"] == "verify-full"
assert not any(privileged) and not schema_create and not truncate
assert len(triggers) == 2 and all(v == "O" for v in triggers.values()) and not invalid
