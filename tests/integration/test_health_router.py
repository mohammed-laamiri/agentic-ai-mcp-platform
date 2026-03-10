"""
Integration tests for Health Router.

Endpoint: GET /api/health
"""

import pytest


class TestHealthRouter:
    """Tests for the health check endpoint."""

    def test_health_returns_ok(self, client):
        """Health check returns 200 with status ok."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_includes_environment(self, client):
        """Health check includes environment setting."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert data["environment"] == "development"  # Default setting
