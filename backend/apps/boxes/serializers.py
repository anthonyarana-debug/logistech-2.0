from decimal import Decimal

from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, transaction
from django.db.models import F
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Product
from apps.core.api import Conflict, StrictModelSerializer, is_global
from apps.organizations.models import Branch, Company

from .models import Box


class QuantityField(serializers.IntegerField):
    def to_internal_value(self, data):
        if isinstance(data, bool):
            self.fail("invalid")
        return super().to_internal_value(data)


class BoxSerializer(StrictModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(status=Company.Status.ACTIVE), required=False
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.none(),
        error_messages={"does_not_exist": "Referencia no disponible."},
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.none(),
        error_messages={"does_not_exist": "Referencia no disponible."},
    )
    company_name = serializers.CharField(source="company.name", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    quantity = QuantityField(min_value=1)
    weight_kg = serializers.DecimalField(
        max_digits=12, decimal_places=3, min_value=Decimal("0.001"), allow_null=True, required=False
    )

    class Meta:
        model = Box
        fields = [
            "id",
            "internal_id",
            "qr_code",
            "company",
            "company_name",
            "product",
            "product_name",
            "product_sku",
            "category_name",
            "branch",
            "branch_name",
            "quantity",
            "weight_kg",
            "priority",
            "status",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "internal_id", "qr_code", "created_by", "created_at"]

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        products = Product.objects.filter(
            status=Company.Status.ACTIVE,
            company__status=Company.Status.ACTIVE,
            category__company_id=F("company_id"),
        ).select_related("category")
        branches = Branch.objects.filter(status=Company.Status.ACTIVE, company__status="ACTIVE")
        if not is_global(user):
            products = products.filter(company_id=user.company_id)
            branches = branches.filter(company_id=user.company_id)
        fields["product"].queryset = products
        fields["branch"].queryset = branches
        return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        company = attrs.get("company") or self.instance.company
        for key in ("product", "branch"):
            related = attrs.get(key) or getattr(self.instance, key, None)
            if related and related.company_id != company.pk:
                raise ValidationError({key: "Referencia no disponible para esta empresa."})
        if self.instance is None:
            if attrs.get("status", Box.Status.REGISTERED) != Box.Status.REGISTERED:
                raise ValidationError({"status": "Una caja nueva debe estar registrada."})
        elif self.instance.status != Box.Status.REGISTERED:
            if any(getattr(self.instance, key) != value for key, value in attrs.items()):
                raise Conflict(
                    "Una caja recibida o rechazada no admite modificaciones en este CRUD."
                )
        return attrs

    def create(self, validated_data):
        for attempt in range(3):
            try:
                with transaction.atomic():
                    return Box.objects.create(**validated_data)
            except ModelValidationError as error:
                # Solo regenerar colisiones de identificadores generados, nunca ignorar integridad.
                fields = getattr(error, "error_dict", {})
                if not fields or not set(fields) <= {"id", "internal_id", "qr_code"}:
                    raise
                if not all(e.code == "unique" for errors in fields.values() for e in errors):
                    raise
            except IntegrityError as error:
                name = getattr(getattr(error.__cause__, "diag", None), "constraint_name", "")
                if name not in {
                    "boxes_box_pkey",
                    "boxes_box_internal_id_key",
                    "boxes_box_qr_code_key",
                }:
                    raise
        raise Conflict("No se pudo generar un identificador único. Intenta nuevamente.")
