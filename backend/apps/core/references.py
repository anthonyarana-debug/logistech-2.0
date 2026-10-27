"""Lectura mínima para selectores F4; no es CRUD de organizaciones/catálogo."""

import uuid

from django.db.models import F
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasCompanyAccess
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company

from .api import PrivateUserThrottle, is_global


class ReferenceView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyAccess]
    throttle_classes = [PrivateUserThrottle]

    def get(self, request):
        params = request.query_params
        if any(key != "company" or len(params.getlist(key)) != 1 for key in params):
            raise ValidationError({"filtros": "Filtro desconocido o repetido."})
        companies = Company.objects.filter(status="ACTIVE").order_by("name", "id")
        if not is_global(request.user):
            companies = companies.filter(pk=request.user.company_id)
        chosen = request.user.company_id
        if "company" in params:
            try:
                chosen = uuid.UUID(params["company"])
            except (ValueError, TypeError):
                raise ValidationError({"company": "Se requiere un UUID válido."}) from None
            if not is_global(request.user) and chosen != request.user.company_id:
                raise PermissionDenied("No tienes permiso para consultar ese ámbito.")
        company = companies.filter(pk=chosen).first() if chosen else None
        if chosen and company is None:
            raise ValidationError({"company": "Empresa no disponible."})
        products = Product.objects.none()
        branches = Branch.objects.none()
        categories = Category.objects.none()
        if company:
            products = (
                Product.objects.filter(
                    company=company, status="ACTIVE", category__company_id=F("company_id")
                )
                .select_related("category")
                .order_by("name", "id")
            )
            branches = Branch.objects.filter(company=company, status="ACTIVE").order_by(
                "name", "id"
            )
            categories = Category.objects.filter(company=company).order_by("name", "id")
        response = Response(
            {
                "companies": [{"id": str(c.pk), "name": c.name} for c in companies],
                "company": str(company.pk) if company else None,
                "products": [
                    {
                        "id": str(p.pk),
                        "name": p.name,
                        "sku": p.sku,
                        "category": str(p.category_id),
                        "category_name": p.category.name,
                    }
                    for p in products
                ],
                "branches": [{"id": str(b.pk), "name": b.name} for b in branches],
                "categories": [{"id": str(c.pk), "name": c.name} for c in categories],
            }
        )
        response["Cache-Control"] = "no-store"
        return response
