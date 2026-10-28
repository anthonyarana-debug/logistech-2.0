from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework.exceptions import ValidationError

from apps.core.api import Conflict, TenantViewSet
from apps.core.messages import message

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
                    raise ValidationError({key: message("use_true_or_false")})
                queryset = queryset.filter(**{key: params[key] == "true"})
        return queryset

    def handle_exception(self, exc):
        if isinstance(exc, ModelValidationError) and "__all__" in getattr(exc, "error_dict", {}):
            exc = Conflict(message("the_category_conflicts_with_an_existing_record"))
        return super().handle_exception(exc)
