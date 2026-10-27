import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Superadministrador"
        COMPANY_ADMIN = "COMPANY_ADMIN", "Administrador de empresa"
        OPERATOR = "OPERATOR", "Operador"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    date_joined = None
    email = models.EmailField("correo electrónico", unique=True)
    role = models.CharField("rol", max_length=20, choices=Role, default=Role.OPERATOR)
    company = models.ForeignKey(
        "organizations.Company",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="empresa",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="user_email_ci"),
            models.CheckConstraint(
                condition=(
                    Q(role="SUPERADMIN", is_superuser=True, is_staff=True, company__isnull=True)
                    | (Q(role__in=["OPERATOR", "COMPANY_ADMIN"]) & Q(is_superuser=False))
                ),
                name="user_role_flags_consistent",
            ),
            models.CheckConstraint(
                condition=~Q(role="COMPANY_ADMIN") | Q(company__isnull=False),
                name="company_admin_requires_company",
            ),
        ]

    def clean(self):
        super().clean()
        self.email = (self.email or "").strip().lower()
        if self.is_superuser != (self.role == self.Role.SUPERADMIN):
            raise ValidationError("El rol y el indicador de superusuario deben coincidir.")
        if self.role == self.Role.SUPERADMIN and (not self.is_staff or self.company_id):
            raise ValidationError("El superadministrador debe ser staff y no tener empresa.")
        if self.role == self.Role.COMPANY_ADMIN and not self.company_id:
            raise ValidationError({"company": "El administrador debe tener una empresa asignada."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
