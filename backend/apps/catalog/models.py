from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

from apps.organizations.models import Company, CompanyOwned


class Category(CompanyOwned):
    name = models.CharField("nombre", max_length=120)
    description = models.TextField("descripción", blank=True)
    is_fragile = models.BooleanField("frágil", default=False)
    is_perishable = models.BooleanField("perecedera", default=False)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        constraints = [
            models.UniqueConstraint(Lower("name"), "company", name="category_company_name_ci")
        ]

    def __str__(self):
        return self.name


class Product(CompanyOwned):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="categoría")
    sku = models.CharField(max_length=64)
    name = models.CharField("nombre", max_length=160)
    description = models.TextField("descripción", blank=True)
    status = models.CharField(max_length=16, choices=Company.Status, default=Company.Status.ACTIVE)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        constraints = [
            models.UniqueConstraint(fields=["company", "sku"], name="product_company_sku")
        ]

    def clean(self):
        super().clean()
        self.sku = (self.sku or "").strip().upper()
        category_company = (
            Category.objects.filter(pk=self.category_id)
            .values_list("company_id", flat=True)
            .first()
        )
        if category_company and category_company != self.company_id:
            raise ValidationError({"category": "La categoría debe pertenecer a la misma empresa."})

    def __str__(self):
        return f"{self.sku} · {self.name}"
