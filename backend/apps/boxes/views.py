import re

from django.db.models import F
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Product
from apps.core.api import Conflict, TenantViewSet
from apps.core.messages import message
from apps.organizations.models import Branch, Company

from .models import Box
from .serializers import BoxSerializer


class BoxViewSet(TenantViewSet):
    queryset = Box.objects.filter(
        product__company_id=F("company_id"),
        branch__company_id=F("company_id"),
        product__category__company_id=F("company_id"),
    ).select_related("company", "product__category", "branch", "created_by")
    serializer_class = BoxSerializer
    operator_write = True
    uuid_filters = {
        "company": "company_id",
        "product": "product_id",
        "branch": "branch_id",
        "category": "product__category_id",
        "qr_code": "qr_code",
    }
    choice_filters = {"status": Box.Status.values, "priority": Box.Priority.values}
    extra_filters = ("internal_id",)
    search_fields = ("internal_id", "product__name", "product__sku")

    def filter_extra(self, queryset, params):
        if "internal_id" in params:
            value = params["internal_id"].upper()
            if not re.fullmatch(r"CJ-[A-F0-9]{32}", value):
                raise ValidationError({"internal_id": message("invalid_internal_identifier")})
            queryset = queryset.filter(internal_id=value)
        return queryset

    def lock_references(self, serializer, company):
        """Lock and validate active references against the selected company."""
        for key, model in (("product", Product), ("branch", Branch)):
            related = serializer.validated_data.get(key) or getattr(serializer.instance, key, None)
            related = model.objects.select_for_update().filter(pk=related.pk).first()
            if related is None:
                raise Conflict(message("a_reference_is_no_longer_available"))
            if related.company_id != company.pk or related.status != Company.Status.ACTIVE:
                raise Conflict(message("references_must_be_active_and_belong_to_the_company"))
            if key == "product":
                category = related.category
                if category.company_id != company.pk:
                    raise Conflict(message("references_must_belong_to_the_company"))
            serializer.validated_data[key] = related

    def perform_create(self, serializer):
        company = self.lock_company(serializer.validated_data["company"])
        self.lock_references(serializer, company)
        serializer.save(company=company, created_by=self.request.user)

    def perform_update(self, serializer):
        company = self.lock_company(serializer.instance.company)
        self.lock_references(serializer, company)
        serializer.save(company=company)

    def perform_destroy(self, instance):
        if instance.status != Box.Status.REGISTERED:
            raise Conflict(
                message("only_registered_boxes_without_reception_or_rejection_can_be_deleted")
            )
        super().perform_destroy(instance)
