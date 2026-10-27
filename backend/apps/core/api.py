"""Infraestructura común del CRUD: alcance, filtros explícitos y escrituras atómicas."""

import uuid
from collections.abc import Mapping

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from apps.accounts.permissions import HasCompanyAccess
from apps.accounts.throttles import AuthThrottle
from apps.organizations.models import Company


def is_global(user):
    return user.role == user.Role.SUPERADMIN and user.is_superuser and user.is_staff


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "La operación entra en conflicto con el estado o las referencias del recurso."
    default_code = "conflict"


class PrivateUserThrottle(AuthThrottle):
    scope = "private_api"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": str(request.user.pk)}


class ResourcePermission(HasCompanyAccess):
    message = "No tienes permiso para realizar esta operación."

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if is_global(request.user) or request.method in SAFE_METHODS:
            return True
        if request.user.role == request.user.Role.COMPANY_ADMIN:
            return True
        return view.operator_write and request.method in {"POST", "PUT", "PATCH"}


class StrictModelSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        # Solo el superadmin elige empresa al crear. Nadie transfiere recursos por CRUD.
        request = self.context["request"]
        if not (is_global(request.user) and self.instance is None):
            fields["company"].read_only = True
        return fields

    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise ValidationError({"detalle": "Se requiere un objeto JSON."})
        if any(key not in self.fields or self.fields[key].read_only for key in data):
            raise ValidationError({"campos": "La solicitud contiene campos no permitidos."})
        return super().to_internal_value(data)

    def validate(self, attrs):
        user = self.context["request"].user
        if self.instance is None:
            if is_global(user) and "company" not in attrs:
                raise ValidationError({"company": "Elige explícitamente una empresa activa."})
            attrs.setdefault("company", user.company)
        return attrs


class TenantViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, ResourcePermission]
    throttle_classes = [PrivateUserThrottle]
    operator_write = False
    # Nombre de filtro -> lookup. Nunca aceptar lookups arbitrarios de ORM.
    uuid_filters = {"company": "company_id"}
    choice_filters = {}
    search_fields = ()
    extra_filters = ()
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not is_global(user):
            queryset = queryset.filter(company_id=user.company_id)
        params = self.request.query_params
        allowed = set(self.uuid_filters) | set(self.choice_filters) | set(self.extra_filters)
        allowed |= {"search"} if self.search_fields else set()
        if self.action != "list" and params:
            raise ValidationError({"filtros": "Los filtros solo se admiten en la colección."})
        if any(key not in allowed or len(params.getlist(key)) != 1 for key in params):
            raise ValidationError({"filtros": "Filtro desconocido o repetido."})
        for key, lookup in self.uuid_filters.items():
            if key not in params:
                continue
            try:
                value = uuid.UUID(params[key])
            except (ValueError, TypeError):
                raise ValidationError({key: "Se requiere un UUID válido."}) from None
            if key == "company" and not is_global(user) and value != user.company_id:
                raise PermissionDenied("No tienes permiso para consultar ese ámbito.")
            queryset = queryset.filter(**{lookup: value})
        for key, choices in self.choice_filters.items():
            if key in params:
                if params[key] not in choices:
                    raise ValidationError({key: "Valor de filtro no permitido."})
                queryset = queryset.filter(**{key: params[key]})
        if "search" in params:
            value = params["search"].strip()
            if not value or len(value) > 100:
                raise ValidationError({"search": "Usa entre 1 y 100 caracteres."})
            expression = Q()
            for field in self.search_fields:
                expression |= Q(**{f"{field}__icontains": value})
            queryset = queryset.filter(expression)
        queryset = self.filter_extra(queryset, params)
        if self.request.method not in SAFE_METHODS:
            queryset = queryset.select_for_update(of=("self",))
        return queryset.order_by("created_at", "id")

    def filter_extra(self, queryset, params):
        return queryset

    def lock_actor(self):
        # Releer el usuario en la transacción: rol/asignación no provienen del payload/JWT.
        actor = get_user_model().objects.select_for_update().filter(pk=self.request.user.pk).first()
        if actor is None:
            raise AuthenticationFailed("La cuenta no está disponible.")
        self.request.user = actor
        self.check_permissions(self.request)
        return actor

    def lock_company(self, company):
        company = Company.objects.select_for_update().filter(pk=company.pk).first()
        if company is None:
            raise Conflict("La empresa no está disponible.")
        if company.status != Company.Status.ACTIVE:
            raise Conflict("La empresa debe estar activa para modificar recursos.")
        return company

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.lock_actor()
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.lock_actor()
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        self.lock_actor()
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        company = self.lock_company(serializer.validated_data["company"])
        serializer.save(company=company)

    def perform_update(self, serializer):
        company = self.lock_company(serializer.instance.company)
        serializer.save(company=company)

    def perform_destroy(self, instance):
        self.lock_company(instance.company)
        instance.delete()

    def handle_exception(self, exc):
        if isinstance(exc, ModelValidationError):
            exc = ValidationError({"detalle": "Los datos no cumplen las reglas del recurso."})
        elif isinstance(exc, IntegrityError):
            exc = Conflict()
        return super().handle_exception(exc)
