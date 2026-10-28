from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.core.api import TenantViewSet, is_global

from .models import Branch, Company
from .serializers import BranchSerializer, CompanySerializer


class GlobalAdministration(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active and is_global(request.user))


class CompanyViewSet(TenantViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, GlobalAdministration]
    uuid_filters = {}
    choice_filters = {"status": Company.Status.values}
    search_fields = ("name",)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()  # PROTECT references; historical users/boxes are never cascaded.


class BranchViewSet(TenantViewSet):
    queryset = Branch.objects.select_related("company")
    serializer_class = BranchSerializer
    choice_filters = {"status": Company.Status.values}
    search_fields = ("name", "address")
