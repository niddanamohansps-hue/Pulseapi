from django.urls import path

from .views import health_check, health_ready

app_name = "core"

urlpatterns = [
    # Uptime monitor check (DB-free)
    path("health", health_check, name="health_check"),
    path("health/", health_check, name="health_check_slash"),
    # Deployment readiness check (DB connected)
    path("health/ready", health_ready, name="health_ready"),
    path("health/ready/", health_ready, name="health_ready_slash"),
]
