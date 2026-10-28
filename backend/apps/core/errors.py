import logging

from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.messages import message


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        # No registrar str(exc), SQL, payloads, cookies o credenciales.
        logging.getLogger(__name__).error("Fallo interno de API: %s", type(exc).__name__)
        return Response({"detalle": message("internal_service_error")}, status=500)
    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = {"detalle": message("invalid_credentials_or_session")}
        elif isinstance(exc, Throttled):
            response.data = {"detalle": message("too_many_requests_please_try_again_later")}
        else:
            response.data = {"errores": response.data}
    return response


def csrf_failure(request, reason=""):
    # No reflejar motivos, cookies, cabeceras ni URLs de origen.
    return JsonResponse({"detalle": message("csrf_verification_failed")}, status=403)
