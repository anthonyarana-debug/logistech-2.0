from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework.exceptions import ValidationError

from apps.core.api import Conflict, TenantViewSet

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(TenantViewSet):
    queryset = Category.objects.select_related("company")
    serializer_class = CategorySerializer
    search_fields = ("name", "description")
    extra_filters = ("is_fragile", "is_perishable")

    def filter_extra(self, queryset, params):
        for key in self.extra_filters:
            if key in params:
                if params[key] not in {"true", "false"}:
                    raise ValidationError({key: "Usa true o false."})
                queryset = queryset.filter(**{key: params[key] == "true"})
        return queryset

    def handle_exception(self, exc):
        if isinstance(exc, ModelValidationError) and "__all__" in getattr(exc, "error_dict", {}):
            exc = Conflict("La categoría entra en conflicto con un registro existente.")
        return super().handle_exception(exc)
