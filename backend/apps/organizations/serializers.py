from rest_framework import serializers

from apps.core.api import Conflict, StrictModelSerializer
from apps.core.operational_serializers import OperationalSerializer
from apps.core.operations_messages import text

from .models import Branch, Company


class CompanySerializer(OperationalSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class BranchSerializer(StrictModelSerializer):
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(status="ACTIVE"), required=False
    )
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "company", "company_name", "name", "address", "status", "created_at"]
        read_only_fields = ["id", "created_at"]
        validators = []

    def validate(self, attrs):
        attrs = super().validate(attrs)
        company = attrs.get("company") or self.instance.company
        name = attrs.get("name", self.instance.name if self.instance else "")
        existing = Branch.objects.filter(company=company, name__iexact=name)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise Conflict(text("duplicate"))
        return attrs
