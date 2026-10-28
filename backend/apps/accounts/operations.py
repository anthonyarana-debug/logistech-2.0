from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as ModelValidationError
from django.db.models import F, Q
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.core.api import ResourcePermission, TenantViewSet, is_global
from apps.core.operational_serializers import OperationalSerializer
from apps.core.operations_messages import text
from apps.organizations.models import Branch, Company

from .models import User


def assignment_changed(instance, attrs):
    if instance is None:
        return True
    return (
        any(
            getattr(attrs.get(key, getattr(instance, key)), "pk", None)
            != getattr(instance, f"{key}_id")
            for key in ("company", "branch")
        )
        or attrs.get("role", instance.role) != instance.role
    )


class UserAdministration(ResourcePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            is_global(request.user) or request.user.role == User.Role.COMPANY_ADMIN
        )


class UserAdministrationSerializer(OperationalSerializer):
    password = serializers.CharField(
        write_only=True, min_length=12, max_length=128, trim_whitespace=False, required=False
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.none(), required=False, allow_null=True
    )
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    branch_name = serializers.CharField(source="branch.name", read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "company",
            "company_name",
            "branch",
            "branch_name",
            "is_active",
            "password",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        validators = []

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            # Password reset requires a dedicated session-revocation flow, outside this block.
            fields["password"].read_only = True
        actor = self.context["request"].user
        global_actor = is_global(actor)
        if not global_actor:
            fields["role"].read_only = True
            fields["company"].read_only = True
        # Resolve references only within the effective company, never the entire directory.
        company = getattr(self.instance, "company_id", actor.company_id)
        raw = getattr(self, "initial_data", {})
        if global_actor and isinstance(raw, dict) and "company" in raw:
            import uuid

            try:
                company = uuid.UUID(str(raw["company"]))
            except ValueError:
                company = None
        available = Q(status="ACTIVE")
        if isinstance(self.instance, User):
            # Existing inactive assignments may be retained while disabling an account.
            # validate/save_user still reject new or changed inactive assignments.
            available |= Q(pk=self.instance.branch_id)
        fields["branch"].queryset = Branch.objects.filter(available, company_id=company)
        return fields

    def validate(self, attrs):
        actor = self.context["request"].user
        target = self.instance
        if target and (
            target.pk == actor.pk or target.role == User.Role.SUPERADMIN or target.is_staff
        ):
            raise PermissionDenied(text("protected_user"))
        if not is_global(actor):
            if target and target.role != User.Role.OPERATOR:
                raise PermissionDenied(text("operator_only"))
            if not target:
                attrs.update(company=actor.company, role=User.Role.OPERATOR)
        role = attrs.get("role", target.role if target else User.Role.OPERATOR)
        company = attrs.get("company", target.company if target else None)
        branch = attrs.get("branch", target.branch if target else None)
        if role == User.Role.SUPERADMIN:
            raise serializers.ValidationError({"role": text("root_role")})
        if (role == User.Role.COMPANY_ADMIN or branch) and company is None:
            raise serializers.ValidationError({"company": text("company_required")})
        if branch and (company is None or branch.company_id != company.pk):
            raise serializers.ValidationError({"branch": text("branch_scope")})
        if company and company.status != "ACTIVE" and assignment_changed(target, attrs):
            raise serializers.ValidationError({"company": text("company_status")})
        email = attrs.get("email", target.email if target else "").strip().lower()
        attrs["email"] = email
        if (
            User.objects.filter(email__iexact=email)
            .exclude(pk=target.pk if target else None)
            .exists()
        ):
            raise serializers.ValidationError({"email": text("duplicate_email")})
        if not target and "password" not in attrs:
            raise serializers.ValidationError({"password": text("password_required")})
        if "password" in attrs:
            probe = User(
                email=email,
                first_name=attrs.get("first_name", target.first_name if target else ""),
                last_name=attrs.get("last_name", target.last_name if target else ""),
            )
            try:
                password_validation.validate_password(attrs["password"], probe)
            except ModelValidationError as error:
                raise serializers.ValidationError({"password": error.messages}) from None
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data, is_staff=False, is_superuser=False)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class UserViewSet(TenantViewSet):
    queryset = User.objects.filter(
        Q(branch__isnull=True) | Q(branch__company_id=F("company_id"))
    ).select_related("company", "branch")
    serializer_class = UserAdministrationSerializer
    permission_classes = [IsAuthenticated, UserAdministration]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    search_fields = ("email", "first_name", "last_name")
    uuid_filters = {"company": "company_id", "branch": "branch_id"}
    choice_filters = {"role": User.Role.values}
    extra_filters = ("is_active",)

    def filter_extra(self, queryset, params):
        if "is_active" in params:
            if params["is_active"] not in {"true", "false"}:
                raise serializers.ValidationError({"is_active": text("invalid_filters")})
            queryset = queryset.filter(is_active=params["is_active"] == "true")
        return queryset

    def save_user(self, serializer):
        changed = assignment_changed(serializer.instance, serializer.validated_data)
        company = serializer.validated_data.get(
            "company", serializer.instance.company if serializer.instance else None
        )
        if company:
            company = Company.objects.select_for_update().filter(pk=company.pk).first()
            if company is None or (changed and company.status != "ACTIVE"):
                raise serializers.ValidationError({"company": text("company_status")})
            serializer.validated_data["company"] = company
        branch = serializer.validated_data.get(
            "branch", serializer.instance.branch if serializer.instance else None
        )
        if branch:
            branch = (
                Branch.objects.select_for_update().filter(pk=branch.pk, company=company).first()
            )
            if branch is None or (changed and branch.status != "ACTIVE"):
                raise serializers.ValidationError({"branch": text("branch_scope")})
            serializer.validated_data["branch"] = branch
        serializer.save()

    def perform_create(self, serializer):
        self.save_user(serializer)

    def perform_update(self, serializer):
        self.save_user(serializer)
