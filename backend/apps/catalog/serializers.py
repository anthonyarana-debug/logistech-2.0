from rest_framework import serializers

from apps.core.api import Conflict, StrictModelSerializer, is_global
from apps.core.messages import message
from apps.core.operations_messages import text
from apps.organizations.models import Company

from .models import Category, Product


class CategorySerializer(StrictModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(status=Company.Status.ACTIVE), required=False
    )
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "description",
            "is_fragile",
            "is_perishable",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        validators = []  # La unicidad case-insensitive se comprueba con el ámbito impuesto.

    def validate(self, attrs):
        attrs = super().validate(attrs)
        company = attrs.get("company") or self.instance.company
        name = attrs.get("name", self.instance.name if self.instance else "")
        existing = Category.objects.filter(company=company, name__iexact=name)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise Conflict(message("a_category_with_this_name_already_exists_in_the_company"))
        return attrs


class ProductSerializer(StrictModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(status="ACTIVE"), required=False
    )
    company_name = serializers.CharField(source="company.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "company",
            "company_name",
            "category",
            "category_name",
            "sku",
            "name",
            "description",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        validators = []

    def get_fields(self):
        fields = super().get_fields()
        user = self.context["request"].user
        company = getattr(self.instance, "company_id", user.company_id)
        if self.instance is None and is_global(user):
            raw = getattr(self, "initial_data", {})
            try:
                import uuid

                company = uuid.UUID(str(raw.get("company", "")))
            except (ValueError, AttributeError):
                company = None
        fields["category"].queryset = Category.objects.filter(company_id=company)
        return fields

    def validate(self, attrs):
        attrs = super().validate(attrs)
        company = attrs.get("company") or self.instance.company
        category = attrs.get("category") or self.instance.category
        if category.company_id != company.pk:
            raise serializers.ValidationError({"category": text("category_scope")})
        sku = attrs.get("sku", self.instance.sku if self.instance else "").strip().upper()
        attrs["sku"] = sku
        existing = Product.objects.filter(company=company, sku=sku)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise Conflict(text("duplicate"))
        return attrs
