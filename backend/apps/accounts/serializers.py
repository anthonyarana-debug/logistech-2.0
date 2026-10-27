from collections.abc import Mapping

from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({"detalle": "Se requiere un objeto JSON."})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {"campos": "La solicitud contiene campos no permitidos."}
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
                {"detalle": "No se pudo registrar con los datos proporcionados."}
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
            raise AuthenticationFailed("Credenciales inválidas o cuenta no disponible.")
        return {"user": user}


def identity(user):
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
