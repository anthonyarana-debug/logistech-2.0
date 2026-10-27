from rest_framework import serializers

from apps.core.api import Conflict, StrictModelSerializer
from apps.organizations.models import Company

from .models import Category


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
            raise Conflict("Ya existe una categoría con ese nombre en la empresa.")
        return attrs
