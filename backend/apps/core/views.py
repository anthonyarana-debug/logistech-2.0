from django.db import DatabaseError, connection
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def live(request):
    """Comprueba el proceso, sin consultar dependencias."""
    return Response({"estado": "disponible", "servicio": "LogisTech API"})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request):
    """Readiness: confirma una consulta PostgreSQL sin exponer detalles."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                raise DatabaseError("Respuesta de comprobación no válida")
    except DatabaseError:
        return Response(
            {"estado": "no_disponible", "detalle": "Dependencia de datos no disponible."},
            status=503,
        )
    return Response({"estado": "disponible", "base_de_datos": "disponible"})


def not_found(request, exception):
    return JsonResponse({"detalle": "Recurso no encontrado."}, status=404)


def server_error(request):
    return JsonResponse({"detalle": "Error interno del servicio."}, status=500)
