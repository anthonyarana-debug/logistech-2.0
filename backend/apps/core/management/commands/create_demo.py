"""Datos académicos identificables; nunca sustituye datos existentes."""

import json
import os
import re
import secrets
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.core.messages import message
from apps.organizations.models import Branch, Company


class Command(BaseCommand):
    help = message("demo_help")

    def add_arguments(self, parser):
        parser.add_argument("--namespace", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        namespace = options["namespace"]
        if not re.fullmatch(r"[a-z0-9-]{3,32}", namespace):
            raise CommandError(message("demo_namespace"))
        target = Path(options["output"])
        if (
            target.exists()
            or User.objects.filter(email__endswith=f".{namespace}@example.test").exists()
        ):
            raise CommandError(
                message("demo_exists")
            )
        credentials = {"namespace": namespace, "users": {}}
        created_file = False
        try:
            with transaction.atomic():
                companies = [
                    Company.objects.create(name=f"DEMO · {namespace} · {name}")
                    for name in ("Almacén Lima", "Almacén Arequipa")
                ]
                for role, company in (
                    ("root", None),
                    ("admin", companies[0]),
                    ("operator", companies[0]),
                    ("pending", None),
                ):
                    password = secrets.token_urlsafe(24)
                    email = f"{role}.{namespace}@example.test"
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        role=User.Role.SUPERADMIN
                        if role == "root"
                        else User.Role.COMPANY_ADMIN
                        if role == "admin"
                        else User.Role.OPERATOR,
                        company=company,
                        is_superuser=role == "root",
                        is_staff=role == "root",
                        first_name=f"Demo {role}",
                    )
                    credentials["users"][role] = {"email": email, "password": password}
                    if role == "admin":
                        creator = user
                credentials["companies"] = [str(c.id) for c in companies]
                for company in companies:
                    branches = [
                        Branch.objects.create(company=company, name=name)
                        for name in ("Centro de distribución", "Zona de despacho")
                    ]
                    for index, name in enumerate(("Instrumentos", "Suministros", "Alimentos")):
                        category = Category.objects.create(
                            company=company,
                            name=name,
                            description="Mercancía de demostración académica.",
                            is_fragile=index == 0,
                            is_perishable=index == 2,
                        )
                        product = Product.objects.create(
                            company=company,
                            category=category,
                            name=(
                                "Sensores de temperatura",
                                "Cintas de embalaje",
                                "Conservas selladas",
                            )[index],
                            sku=f"DEMO-{index + 1:03}",
                        )
                        owner = (
                            creator
                            if company == companies[0]
                            else User.objects.get(email=credentials["users"]["root"]["email"])
                        )
                        for n in range(2):
                            Box.objects.create(
                                company=company,
                                product=product,
                                branch=branches[n],
                                quantity=12 + index * 6,
                                weight_kg="4.500",
                                priority=("HIGH", "NORMAL", "LOW")[index],
                                status="REGISTERED"
                                if n == 0
                                else ("RECEIVED" if index != 2 else "REJECTED"),
                                created_by=owner,
                            )
                descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                created_file = True
                with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                    json.dump(credentials, stream, ensure_ascii=False, indent=2)
        except Exception:
            if created_file:
                target.unlink(missing_ok=True)
            raise
        self.stdout.write(self.style.SUCCESS(message("demo_created").format(target=target)))
