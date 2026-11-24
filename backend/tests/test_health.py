from unittest.mock import patch

from django.test import Client


class TestHealthEndpoints:
    def setup_method(self):
        self.client = Client()

    def test_health_check_runs_without_database_access(self):
        """
        Phase 0 Review Fix 2: /health must not query the database,
        preserving Neon free plan 100 CU-hours compute budget.
        Even if database connection is completely broken, /health returns 200 OK.
        """
        with patch("django.db.connection.cursor", side_effect=RuntimeError("Neon DB is asleep")):
            response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "pulseapi-backend"
        assert data["version"] == "0.1.0"

    def test_health_ready_checks_database_connection(self):
        """
        /health/ready executes SELECT 1 to verify DB connectivity during deploy.
        """
        with patch("apps.core.views.connection.cursor") as mock_cursor:
            response = self.client.get("/health/ready")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ready"
            assert data["database"] == "connected"
            mock_cursor.assert_called_once()

    def test_health_ready_returns_503_on_db_failure(self):
        """
        If the database connection fails, /health/ready returns 503 Service Unavailable.
        """
        with patch(
            "apps.core.views.connection.cursor", side_effect=Exception("DB Connection refused")
        ):
            response = self.client.get("/health/ready")
            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "unavailable"
