import uuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q

from apps.organizations.models import CompanyOwned


def internal_id():
    return f"CJ-{uuid.uuid4().hex.upper()}"


class Box(CompanyOwned):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Registrada"
        RECEIVED = "RECEIVED", "Recibida"
        REJECTED = "REJECTED", "Rechazada"

    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "Alta"

    internal_id = models.CharField(max_length=35, unique=True, default=internal_id, editable=False)
    qr_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.PROTECT, verbose_name="producto"
    )
    branch = models.ForeignKey(
        "organizations.Branch", on_delete=models.PROTECT, verbose_name="sucursal"
    )
    quantity = models.PositiveIntegerField("cantidad")
    weight_kg = models.DecimalField(
        "peso kg", max_digits=12, decimal_places=3, null=True, blank=True
    )
    priority = models.CharField(max_length=10, choices=Priority, default=Priority.NORMAL)
    status = models.CharField(max_length=16, choices=Status, default=Status.REGISTERED)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "caja"
        verbose_name_plural = "cajas"
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gt=0), name="box_quantity_positive"),
            models.CheckConstraint(
                condition=Q(weight_kg__isnull=True) | Q(weight_kg__gt=0), name="box_weight_positive"
            ),
            models.CheckConstraint(
                condition=Q(status__in=["REGISTERED", "RECEIVED", "REJECTED"]),
                name="box_status_allowed",
            ),
            models.CheckConstraint(
                condition=Q(priority__in=["LOW", "NORMAL", "HIGH"]),
                name="box_priority_allowed",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "status", "created_at"], name="box_company_status_date")
        ]

    def clean(self):
        super().clean()
        for field in ("product", "branch"):
            try:
                related = getattr(self, field)
            except ObjectDoesNotExist:
                continue  # full_clean ya registra el error de FK requerido/inexistente.
            if related.company_id != self.company_id:
                raise ValidationError({field: "El recurso debe pertenecer a la misma empresa."})
        # El creador histórico permanece válido aunque después cambie su asignación.
        if self.created_by_id and self._state.adding:
            try:
                user = self.created_by
            except ObjectDoesNotExist:
                return
            if user.role != user.Role.SUPERADMIN and user.company_id != self.company_id:
                raise ValidationError({"created_by": "El creador debe pertenecer a la empresa."})
        elif not self._state.adding:
            original = (
                type(self)
                .objects.filter(pk=self.pk)
                .values_list("created_by_id", flat=True)
                .first()
            )
            if original is not None and original != self.created_by_id:
                raise ValidationError({"created_by": "No se permite cambiar el creador histórico."})

    def __str__(self):
        return self.internal_id
