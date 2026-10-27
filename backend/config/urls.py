from django.urls import include, path

from apps.core.views import health, live
from config.admin import site

urlpatterns = [
    path("admin/", site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/health/", health, name="health"),
    path("api/v1/health/live/", live, name="live"),
]

handler404 = "apps.core.views.not_found"
handler500 = "apps.core.views.server_error"
