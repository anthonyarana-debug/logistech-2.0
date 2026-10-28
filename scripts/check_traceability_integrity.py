"""Read-only integrity snapshot; pipe into Python inside the isolated backend."""

import json
import os
from datetime import datetime, timezone
from importlib.metadata import version

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django  # noqa: E402

django.setup()

from django.db import connection  # noqa: E402
from django.db.models import Count, F  # noqa: E402

from apps.boxes.models import Box, BoxEvent, Receipt  # noqa: E402

discrepancies = {
    "receipt_company": Receipt.objects.exclude(box__company_id=F("company_id")).count(),
    "receipt_branch": Receipt.objects.exclude(branch__company_id=F("company_id")).count(),
    "receipt_status": Receipt.objects.exclude(box__status=F("result")).count(),
    "event_branch": BoxEvent.objects.exclude(branch__company_id=F("company_id")).count(),
}
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT tgname FROM pg_trigger WHERE NOT tgisinternal AND "
        "tgname IN ('boxes_receipt_immutable','boxes_event_immutable')"
    )
    triggers = sorted(row[0] for row in cursor.fetchall())
    constraints = {
        table: sorted(
            name
            for name, detail in connection.introspection.get_constraints(cursor, table).items()
            if detail.get("unique") or detail.get("check")
        )
        for table in ("boxes_receipt", "boxes_boxevent")
    }
report = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "scope": "Read-only isolated demo PostgreSQL; historical actors may be reassigned",
    "vendor": connection.vendor,
    "versions": {name: version(name) for name in ("qrcode", "zxing-cpp", "Django")},
    "counts": {
        "boxes": Box.objects.count(),
        "receipts": Receipt.objects.count(),
        "events": BoxEvent.objects.count(),
    },
    "events_by_type": list(BoxEvent.objects.values("event_type").annotate(count=Count("id"))),
    "legacy_terminal_boxes_without_receipt": Box.objects.exclude(status="REGISTERED")
    .filter(receipt__isnull=True)
    .count(),
    "discrepancies": discrepancies,
    "triggers": triggers,
    "constraints": constraints,
}
print(json.dumps(report, indent=2))
raise SystemExit(int(any(discrepancies.values()) or len(triggers) != 2))
