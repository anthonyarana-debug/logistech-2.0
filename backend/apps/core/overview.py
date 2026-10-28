import uuid

from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company

from .api import PrivateUserThrottle, ResourcePermission, is_global
from .operations_messages import text


class OverviewView(APIView):
    permission_classes = [IsAuthenticated, ResourcePermission]
    throttle_classes = [PrivateUserThrottle]
    operator_write = False

    def get(self, request):
        params = request.query_params
        if any(k != "company" or len(params.getlist(k)) != 1 for k in params):
            raise ValidationError({"filtros": text("invalid_filters")})
        company = request.user.company_id
        global_actor = is_global(request.user)
        if "company" in params:
            try:
                company = uuid.UUID(params["company"])
            except ValueError:
                raise ValidationError({"company": text("invalid_filters")}) from None
            if not global_actor and company != request.user.company_id:
                raise PermissionDenied(text("scope_denied"))
        models = {"branches": Branch, "products": Product, "categories": Category, "boxes": Box}
        if request.user.role != User.Role.OPERATOR:
            models["users"] = User
        counts = {}
        for key, model in models.items():
            query = model.objects.all()
            if company:
                query = query.filter(company_id=company)
            counts[key] = query.count()
        if global_actor:
            counts["companies"] = (
                Company.objects.filter(pk=company).count() if company else Company.objects.count()
            )
        response = Response(
            {
                "role": request.user.role,
                "company": str(company) if company else None,
                "counts": counts,
            }
        )
        response["Cache-Control"] = "no-store"
        return response
