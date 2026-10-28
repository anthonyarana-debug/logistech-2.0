from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.messages import message

from .serializers import LoginSerializer, RegistrationSerializer, identity
from .throttles import (
    CsrfThrottle,
    LoginIdentityThrottle,
    LoginIPThrottle,
    LogoutThrottle,
    RefreshThrottle,
    RegistrationThrottle,
)

User = get_user_model()


def token_response(user, refresh):
    response = Response({"access": str(refresh.access_token), "user": identity(user)})
    response.set_cookie(
        settings.AUTH_REFRESH_COOKIE,
        str(refresh),
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="Lax",
        path="/api/v1/auth/",
    )
    return response


class AuthView(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class PublicAuthView(AuthView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get_authenticate_header(self, request):
        return "Bearer"


class CsrfView(PublicAuthView):
    throttle_classes = [CsrfThrottle]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(PublicAuthView):
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(identity(user), status=status.HTTP_201_CREATED)


@method_decorator(csrf_protect, name="dispatch")
class LoginView(PublicAuthView):
    throttle_classes = [LoginIPThrottle, LoginIdentityThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return token_response(user, RefreshToken.for_user(user))


def read_refresh(request):
    """Read only the HttpOnly cookie; reject missing, expired or invalid tokens."""
    raw = request.COOKIES.get(settings.AUTH_REFRESH_COOKIE)
    if not raw:
        raise AuthenticationFailed(message("the_session_is_unavailable"))
    try:
        return raw, RefreshToken(raw)
    except TokenError:
        raise AuthenticationFailed(message("the_session_is_unavailable")) from None


@method_decorator(csrf_protect, name="dispatch")
class RefreshView(PublicAuthView):
    throttle_classes = [RefreshThrottle]

    def post(self, request):
        raw, original = read_refresh(request)
        try:
            with transaction.atomic():
                # Serializa refresh concurrentes: solo uno puede consumir el token.
                OutstandingToken.objects.select_for_update().get(jti=original["jti"])
                original = RefreshToken(raw)
                user = User.objects.select_related("company").get(
                    pk=original["user_id"], is_active=True
                )
                original.blacklist()
                replacement = RefreshToken.for_user(user)
        except (TokenError, User.DoesNotExist, OutstandingToken.DoesNotExist, ValidationError):
            raise AuthenticationFailed(message("the_session_is_unavailable")) from None
        return token_response(user, replacement)


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(PublicAuthView):
    throttle_classes = [LogoutThrottle]

    def post(self, request):
        try:
            _, refresh = read_refresh(request)
            refresh.blacklist()
        except AuthenticationFailed:
            pass  # Cierre idempotente: una cookie ausente/expirada ya no autoriza refresh.
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.AUTH_REFRESH_COOKIE, path="/api/v1/auth/", samesite="Lax")
        return response


class MeView(AuthView):
    def get(self, request):
        return Response(identity(request.user))
