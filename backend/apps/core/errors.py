from django.http import JsonResponse
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, Throttled
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            response.data = {"detalle": "Credenciales o sesión no válidas."}
        elif isinstance(exc, Throttled):
            response.data = {"detalle": "Demasiadas solicitudes. Intenta nuevamente más tarde."}
        else:
            response.data = {"errores": response.data}
    return response


def csrf_failure(request, reason=""):
    # No reflejar motivos, cookies, cabeceras ni URLs de origen.
    return JsonResponse({"detalle": "La verificación CSRF no fue válida."}, status=403)
