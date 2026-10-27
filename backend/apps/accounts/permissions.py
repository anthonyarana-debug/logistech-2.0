from rest_framework.permissions import BasePermission


class HasCompanyAccess(BasePermission):
    """Política inicial para futuros recursos privados; aún no hay CRUD REST."""

    message = "Se requiere una empresa activa asignada para acceder a este recurso."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.role == user.Role.SUPERADMIN and user.is_superuser:
            return True
        return user.company_id is not None and user.company.status == "ACTIVE"

    def has_object_permission(self, request, view, obj):
        if not self.has_permission(request, view):
            return False
        user = request.user
        if user.role == user.Role.SUPERADMIN and user.is_superuser:
            return True
        return getattr(obj, "company_id", None) == user.company_id
