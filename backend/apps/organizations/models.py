import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class ValidatedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Company(ValidatedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Activa"
        INACTIVE = "INACTIVE", "Inactiva"

    name = models.CharField("nombre", max_length=160)
    status = models.CharField(max_length=16, choices=Status, default=Status.ACTIVE)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"

    def __str__(self):
        return self.name


class CompanyOwned(ValidatedModel):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, verbose_name="empresa")

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if not self._state.adding:
            original = type(self).objects.filter(pk=self.pk).values_list("company_id", flat=True)
            if original.exists() and original.first() != self.company_id:
                raise ValidationError({"company": "No se permite cambiar la empresa del recurso."})


class Branch(CompanyOwned):
    name = models.CharField("nombre", max_length=120)
    address = models.CharField("dirección", max_length=240, blank=True)
    status = models.CharField(max_length=16, choices=Company.Status, default=Company.Status.ACTIVE)

    class Meta:
        verbose_name = "sucursal"
        verbose_name_plural = "sucursales"
        constraints = [
            models.UniqueConstraint(Lower("name"), "company", name="branch_company_name_ci")
        ]

    def __str__(self):
        return self.name
