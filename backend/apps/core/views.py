from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache


@never_cache
def health_check(request):
    """
    Uptime monitor health check.
    PHASE 0 FIX 2: Does NOT touch the database to preserve Neon free compute budget (100 CU-hours).
    Always returns 200 OK immediately if the web process is running.
    """
    return JsonResponse(
        {
            "status": "ok",
            "service": "pulseapi-backend",
            "version": "0.1.0",
        },
        status=200,
    )


@never_cache
def health_ready(request):
    """
    Readiness probe for deploy checks.
    Touches the database to confirm active connectivity and migrations.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        return JsonResponse(
            {
                "status": "ready",
                "database": "connected",
            },
            status=200,
        )
    except Exception as exc:
        return JsonResponse(
            {
                "status": "unavailable",
                "database": "error",
                "detail": str(exc),
            },
            status=503,
        )
