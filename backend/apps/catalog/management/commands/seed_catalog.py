"""Carga categorías por tipo de producto y productos de ejemplo para una empresa.

Cada tipo tiene su propio prefijo de SKU (ELEC-, MUEB-, FRAG-...), de modo que los
electrodomésticos, muebles y productos frágiles nunca comparten el mismo código.
Es idempotente: si se ejecuta dos veces no duplica nada ni modifica datos existentes.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalog.models import Category, Product
from apps.organizations.models import Company

# (categoría, prefijo SKU, frágil, perecedera, descripción, productos)
CATALOG = [
    ("Electrodomésticos", "ELEC", False, False, "Línea blanca y equipos para el hogar.",
     ["Refrigeradora 300 L", "Lavadora 12 kg", "Microondas 20 L"]),
    ("Muebles", "MUEB", False, False, "Muebles armados y en caja; carga voluminosa.",
     ["Ropero 3 puertas", "Escritorio de melamina", "Juego de comedor 4 sillas"]),
    ("Cerámica y vidrio", "FRAG", True, False, "Productos sensibles: manipular con cuidado.",
     ["Mayólica 60x60 (caja)", "Inodoro one piece", "Espejo biselado 80 cm"]),
    ("Electrónica y cómputo", "TECN", True, False, "Equipos electrónicos frágiles y de alto valor.",
     ["Laptop 15 pulgadas", "Televisor 55 pulgadas", "Monitor 24 pulgadas"]),
    ("Alimentos perecibles", "PERE", False, True, "Despacho prioritario y cadena de frío.",
     ["Yogurt pack x6", "Queso fresco 1 kg", "Frutas de estación (jaba)"]),
    ("Ferretería y construcción", "FERR", False, False, "Herramientas y materiales pesados.",
     ["Taladro percutor 800 W", "Cemento 42.5 kg", "Caja de tornillos x500"]),
]


class Command(BaseCommand):
    help = "Seed product-type categories and sample products for one company (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--company", required=True, help="Company name (exact) or UUID.")

    def handle(self, *args, company, **options):
        found = Company.objects.filter(name=company)
        if not found.exists():
            try:
                found = Company.objects.filter(pk=company)
                found.exists()
            except Exception:
                found = Company.objects.none()
        if found.count() != 1:
            raise CommandError(f"Company {company!r} not found (or ambiguous).")
        target = found.get()
        categories = products = 0
        with transaction.atomic():
            for name, prefix, fragile, perishable, description, items in CATALOG:
                category, made = Category.objects.get_or_create(
                    company=target,
                    name__iexact=name,
                    defaults={"name": name, "description": description,
                              "is_fragile": fragile, "is_perishable": perishable},
                )
                categories += made
                for index, item in enumerate(items, start=1):
                    _, made = Product.objects.get_or_create(
                        company=target,
                        sku=f"{prefix}-{index:03}",
                        defaults={"category": category, "name": item},
                    )
                    products += made
        self.stdout.write(
            f"{target.name}: {categories} categories and {products} products created "
            f"({len(CATALOG)} product types)."
        )
