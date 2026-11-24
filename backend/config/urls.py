from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Core health & readiness endpoints
    path("", include("apps.core.urls")),
]
