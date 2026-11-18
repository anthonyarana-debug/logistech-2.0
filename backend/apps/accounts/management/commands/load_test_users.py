"""Cuenta o elimina los usuarios creados por las pruebas de carga k6.

Solo toca cuentas OPERATOR sin empresa cuyo correo empieza por el prefijo de
prueba y termina en @example.test, de modo que no puede afectar usuarios reales.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max, Min
from django.db.models.functions import TruncSecond

from apps.accounts.models import User

DOMAIN = "@example.test"


class Command(BaseCommand):
    help = "Count (default) or delete users created by the k6 cloud load test."

    def add_arguments(self, parser):
        parser.add_argument("--prefix", default="k6-", help="Email prefix used by the test run.")
        parser.add_argument("--delete", action="store_true", help="Delete the matching users.")

    def handle(self, *args, prefix, delete, **options):
        if not prefix.startswith("k6-"):
            raise CommandError("The prefix must start with 'k6-'.")
        users = User.objects.filter(
            email__startswith=prefix,
            email__endswith=DOMAIN,
            role=User.Role.OPERATOR,
            company__isnull=True,
            is_superuser=False,
        )
        stats = users.aggregate(total=Count("pk"), first=Min("created_at"), last=Max("created_at"))
        self.stdout.write(f"Users with prefix {prefix!r}: {stats['total']}")
        if stats["total"]:
            span = (stats["last"] - stats["first"]).total_seconds()
            self.stdout.write(
                f"First: {stats['first']:%Y-%m-%d %H:%M:%S}  "
                f"Last: {stats['last']:%Y-%m-%d %H:%M:%S}  Span: {span:.1f} s"
            )
            peak = (
                users.annotate(second=TruncSecond("created_at"))
                .values("second")
                .annotate(n=Count("pk"))
                .order_by("-n")
                .first()
            )
            self.stdout.write(f"Peak: {peak['n']} users/s")
        if delete:
            deleted, _ = users.delete()
            self.stdout.write(f"Deleted {deleted} test users.")
