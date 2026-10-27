"""Fixtures limitadas F5, solo en el proyecto Compose de validación local."""

import argparse
import json
import os
import re
import secrets
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402
from rest_framework_simplejwt.tokens import AccessToken  # noqa: E402

from apps.accounts.models import User  # noqa: E402
from apps.boxes.models import Box  # noqa: E402
from apps.catalog.models import Category, Product  # noqa: E402
from apps.organizations.models import Branch, Company  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--namespace", required=True)
parser.add_argument("--users", type=int, default=2)
parser.add_argument("--output")
parser.add_argument("--retire", action="store_true")
args = parser.parse_args()
if os.environ.get("F5_VALIDATION") != "local-only" or settings.SETTINGS_MODULE.endswith(
    "production"
):
    raise SystemExit("Se requiere el entorno local F5 aislado; producción no admitida.")
if not re.fullmatch(r"f5load-[a-z0-9-]{3,40}", args.namespace) or not 1 <= args.users <= 100:
    raise SystemExit("Namespace f5load- explícito y entre 1 y 100 usuarios.")
suffix = f".{args.namespace}@example.test"
if args.retire:
    count = User.objects.filter(email__endswith=suffix).update(is_active=False)
    if args.output:
        target = Path(args.output)
        if target.parent != Path("/tmp") or target.name != f"{args.namespace}.json":
            raise SystemExit("Ruta de manifiesto fuera del directorio temporal autorizado.")
        target.unlink(missing_ok=True)
    print(json.dumps({"usuarios_desactivados": count, "namespace": args.namespace}))
    raise SystemExit(0)
if (
    not args.output
    or Path(args.output).exists()
    or User.objects.filter(email__endswith=suffix).exists()
):
    raise SystemExit("Se requiere archivo/namespace nuevo. No se sustituyen datos.")
manifest = {"namespace": args.namespace, "users": []}
with transaction.atomic():
    companies = []
    for number in range(2):
        company = Company.objects.create(name=f"DEMO · {args.namespace} · Empresa {number + 1}")
        category = Category.objects.create(company=company, name="Carga controlada F5")
        branch = Branch.objects.create(company=company, name="Sucursal de prueba F5")
        product = Product.objects.create(
            company=company, category=category, name="Producto de carga F5", sku="F5-001"
        )
        companies.append((company, product, branch))
    for index in range(args.users):
        company, product, branch = companies[index % 2]
        password = secrets.token_urlsafe(24) if index == 0 else None
        user = User.objects.create_user(
            email=f"u{index}{suffix}", password=password, role=User.Role.OPERATOR, company=company
        )
        manifest["users"].append(
            {
                "email": user.email,
                "password": password,
                "access": str(AccessToken.for_user(user)),
                "product": str(product.pk),
                "branch": str(branch.pk),
            }
        )
        if index < 2:
            box = Box.objects.create(
                company=company, product=product, branch=branch, quantity=1, created_by=user
            )
            manifest["users"][-1]["lookup"] = box.internal_id
    for index, account in enumerate(manifest["users"]):
        account["lookup"] = manifest["users"][index % min(2, args.users)]["lookup"]
    descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream)
print(
    json.dumps(
        {
            "namespace": args.namespace,
            "usuarios": args.users,
            "empresas": 2,
            "cajas_iniciales": min(2, args.users),
            "max_cajas_nuevas": args.users,
            "archivo_privado": args.output,
        }
    )
)
