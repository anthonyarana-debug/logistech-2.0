import re

from django.db.models import F
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Product
from apps.core.api import Conflict, TenantViewSet
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
                raise ValidationError({"internal_id": "Identificador interno no válido."})
            queryset = queryset.filter(internal_id=value)
        return queryset

    def lock_references(self, serializer, company):
        for key, model in (("product", Product), ("branch", Branch)):
            related = serializer.validated_data.get(key) or getattr(serializer.instance, key, None)
            related = model.objects.select_for_update().filter(pk=related.pk).first()
            if related is None:
                raise Conflict("Una referencia ya no está disponible.")
            if related.company_id != company.pk or related.status != Company.Status.ACTIVE:
                raise Conflict("Las referencias deben estar activas y pertenecer a la empresa.")
            if key == "product":
                category = related.category
                if category.company_id != company.pk:
                    raise Conflict("Las referencias deben pertenecer a la empresa.")
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
            raise Conflict("Solo se pueden eliminar cajas registradas sin recepción ni rechazo.")
        super().perform_destroy(instance)
