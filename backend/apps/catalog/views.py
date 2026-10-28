from django.core.exceptions import ValidationError as ModelValidationError
from django.db.models import F
from rest_framework.exceptions import ValidationError

from apps.core.api import Conflict, TenantViewSet
from apps.core.messages import message

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(TenantViewSet):
    queryset = Category.objects.select_related("company")
    serializer_class = CategorySerializer
    search_fields = ("name", "description")
    extra_filters = ("is_fragile", "is_perishable")

    def filter_extra(self, queryset, params):
        for key in self.extra_filters:
            if key in params:
                if params[key] not in {"true", "false"}:
                    raise ValidationError({key: message("use_true_or_false")})
                queryset = queryset.filter(**{key: params[key] == "true"})
        return queryset

    def handle_exception(self, exc):
        if isinstance(exc, ModelValidationError) and "__all__" in getattr(exc, "error_dict", {}):
            exc = Conflict(message("the_category_conflicts_with_an_existing_record"))
        return super().handle_exception(exc)


class ProductViewSet(TenantViewSet):
    queryset = Product.objects.filter(category__company_id=F("company_id")).select_related(
        "company", "category"
    )
    serializer_class = ProductSerializer
    uuid_filters = {"company": "company_id", "category": "category_id"}
    choice_filters = {"status": ("ACTIVE", "INACTIVE")}
    search_fields = ("name", "sku", "description")

    def save_product(self, serializer, company):
        category = serializer.validated_data.get("category") or serializer.instance.category
        category = (
            Category.objects.select_for_update().filter(pk=category.pk, company=company).first()
        )
        if category is None:
            raise Conflict(message("references_must_belong_to_the_company"))
        serializer.save(company=company, category=category)

    def perform_create(self, serializer):
        self.save_product(serializer, self.lock_company(serializer.validated_data["company"]))

    def perform_update(self, serializer):
        self.save_product(serializer, self.lock_company(serializer.instance.company))
