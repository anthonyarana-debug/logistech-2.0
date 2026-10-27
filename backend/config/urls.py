from django.urls import path

from apps.core.views import health, live

urlpatterns = [
    path("api/v1/health/", health, name="health"),
    path("api/v1/health/live/", live, name="live"),
]

handler404 = "apps.core.views.not_found"
handler500 = "apps.core.views.server_error"
