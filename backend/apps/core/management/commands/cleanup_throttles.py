from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.core.models import ThrottleWindow


class Command(BaseCommand):
    help = "Delete only expired shared throttle windows. Business records are never touched."

    def handle(self, *args, **options):
        cutoff = timezone.now()
        with transaction.atomic():
            # Never wait on a quota being refreshed; retain locks until the
            # deletion and repeat the expiry predicate under those locks.
            keys = list(
                ThrottleWindow.objects.select_for_update(skip_locked=True)
                .filter(expires_at__lte=cutoff)
                .values_list("key", flat=True)
            )
            deleted, _ = ThrottleWindow.objects.filter(
                key__in=keys, expires_at__lte=cutoff
            ).delete()
        self.stdout.write(f"Deleted {deleted} expired throttle windows.")
