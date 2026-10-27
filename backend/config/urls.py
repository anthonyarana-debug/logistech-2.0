from django.urls import include, path

from apps.boxes.views import BoxViewSet
from apps.catalog.views import CategoryViewSet
from apps.core.views import health, live
from config.admin import site

urlpatterns = [
    path("admin/", site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
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

handler404 = "apps.core.views.not_found"
handler500 = "apps.core.views.server_error"
