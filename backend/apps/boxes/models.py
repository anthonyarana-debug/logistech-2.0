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


class ImmutableQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Historical records cannot be changed.")

    def delete(self):
        raise ValidationError("Historical records cannot be deleted.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError("Historical records cannot be changed.")


class ImmutableRecord(CompanyOwned):
    objects = ImmutableQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Historical records cannot be changed.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Historical records cannot be deleted.")


class Receipt(ImmutableRecord):
    class Reason(models.TextChoices):
        DAMAGED = "DAMAGED", "Damaged"
        INCORRECT_ITEM = "INCORRECT_ITEM", "Incorrect item"
        OTHER = "OTHER", "Other"

    class Source(models.TextChoices):
        RECEIPT_API = "RECEIPT_API", "Receipt API"
        BOX_STATUS_UPDATE = "BOX_STATUS_UPDATE", "Box status update"

    box = models.OneToOneField(Box, on_delete=models.PROTECT, related_name="receipt")
    internal_id = models.CharField(max_length=35)
    branch = models.ForeignKey("organizations.Branch", on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    result = models.CharField(
        max_length=16, choices=[("RECEIVED", "Received"), ("REJECTED", "Rejected")]
    )
    reason = models.CharField(max_length=20, choices=Reason, blank=True, default="")
    source = models.CharField(max_length=20, choices=Source)
    idempotency_key = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "actor", "idempotency_key"], name="receipt_actor_company_key"
            ),
            models.CheckConstraint(
                condition=Q(result="RECEIVED", reason="")
                | Q(result="REJECTED", reason__in=["DAMAGED", "INCORRECT_ITEM", "OTHER"]),
                name="receipt_valid_outcome",
            ),
            models.CheckConstraint(
                condition=Q(source__in=["RECEIPT_API", "BOX_STATUS_UPDATE"]),
                name="receipt_valid_source",
            ),
        ]
        indexes = [models.Index(fields=["company", "created_at"], name="receipt_company_date")]


class BoxEvent(ImmutableRecord):
    class EventType(models.TextChoices):
        BOX_CREATED = "BOX_CREATED", "Box created"
        BOX_UPDATED = "BOX_UPDATED", "Box updated"
        BOX_DELETED = "BOX_DELETED", "Box deleted"
        RECEIPT_RECORDED = "RECEIPT_RECORDED", "Receipt recorded"

    # A snapshot UUID deliberately survives deletion of a registered box.
    box = models.UUIDField()
    internal_id = models.CharField(max_length=35)
    branch = models.ForeignKey("organizations.Branch", on_delete=models.PROTECT)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    event_type = models.CharField(max_length=20, choices=EventType)
    outcome = models.CharField(max_length=16, choices=Box.Status)
    data = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(
                    event_type__in=["BOX_CREATED", "BOX_UPDATED", "BOX_DELETED", "RECEIPT_RECORDED"]
                ),
                name="box_event_valid_type",
            ),
            models.CheckConstraint(
                condition=Q(outcome__in=["REGISTERED", "RECEIVED", "REJECTED"]),
                name="box_event_valid_outcome",
            ),
        ]
        indexes = [
            models.Index(fields=["company", "box", "created_at"], name="event_company_box_date")
        ]

    def clean(self):
        super().clean()
        import json

        allowed = {
            "product",
            "quantity",
            "weight_kg",
            "priority",
            "status",
            "branch",
            "receipt",
            "result",
            "reason",
            "source",
        }
        if (
            not isinstance(self.data, dict)
            or set(self.data) - allowed
            or len(json.dumps(self.data)) > 2048
        ):
            raise ValidationError({"data": "Event data must be an allowlisted bounded snapshot."})
        if any(
            not isinstance(value, (str, int, type(None))) or isinstance(value, bool)
            for value in self.data.values()
        ):
            raise ValidationError({"data": "Event snapshot values must be scalar."})
