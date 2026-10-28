from django.urls import include, path

from apps.accounts.operations import UserViewSet
from apps.boxes.views import BoxViewSet
from apps.catalog.views import CategoryViewSet, ProductViewSet
from apps.core.overview import OverviewView
from apps.core.references import ReferenceView
from apps.core.views import health, live
from apps.organizations.views import BranchViewSet, CompanyViewSet
from config.admin import site

urlpatterns = [
    path("admin/", site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/references/", ReferenceView.as_view()),
    path("api/v1/categories/", CategoryViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "api/v1/categories/<uuid:pk>/",
        CategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path("api/v1/boxes/", BoxViewSet.as_view({"get": "list", "post": "create"})),
    path(
        "api/v1/boxes/<uuid:pk>/",
        BoxViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    path("api/v1/health/", health, name="health"),
    path("api/v1/health/live/", live, name="live"),
]

for resource, view in [
    ("companies", CompanyViewSet),
    ("branches", BranchViewSet),
    ("products", ProductViewSet),
    ("users", UserViewSet),
]:
    methods = {"get": "retrieve", "put": "update", "patch": "partial_update"}
    if resource != "users":
        methods["delete"] = "destroy"
    urlpatterns += [
        path(f"api/v1/{resource}/", view.as_view({"get": "list", "post": "create"})),
        path(f"api/v1/{resource}/<uuid:pk>/", view.as_view(methods)),
    ]
urlpatterns.append(path("api/v1/overview/", OverviewView.as_view()))

handler404 = "apps.core.views.not_found"
handler500 = "apps.core.views.server_error"
