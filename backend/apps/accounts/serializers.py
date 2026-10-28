from collections.abc import Mapping

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from apps.core.messages import message

User = get_user_model()


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({"detalle": message("a_json_object_is_required")})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {"campos": message("the_request_contains_fields_that_are_not_allowed")}
            )
        return super().to_internal_value(data)


class RegistrationSerializer(StrictSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate(self, attrs):
        attrs["email"] = attrs["email"].strip().lower()
        user = User(**{k: v for k, v in attrs.items() if k != "password"})
        try:
            password_validation.validate_password(attrs["password"], user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages}) from None
        return attrs

    def create(self, validated_data):
        try:
            with transaction.atomic():
                return User.objects.create_user(
                    **validated_data,
                    role=User.Role.OPERATOR,
                    company=None,
                    is_staff=False,
                    is_superuser=False,
                )
        except (DjangoValidationError, IntegrityError):
            raise serializers.ValidationError(
                {"detalle": message("registration_could_not_be_completed_with_the_supplied_data")}
            ) from None


class LoginSerializer(StrictSerializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"].strip().lower(),
            password=attrs["password"],
        )
        if user is None:
            raise AuthenticationFailed(message("invalid_credentials_or_unavailable_account"))
        return {"user": user}


def identity(user):
    """Return safe identity fields; never include password hashes or refresh tokens."""
    return {
        "id": str(user.pk),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "company": {"id": str(user.company_id), "name": user.company.name}
        if user.company_id
        else None,
        "assignment_pending": user.company_id is None and user.role != User.Role.SUPERADMIN,
    }
