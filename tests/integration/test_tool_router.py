"""
Integration tests for Tool Router.

Endpoints:
- POST /api/tools/ - Register tool
- GET /api/tools/ - List tools
- GET /api/tools/{tool_id} - Get tool by ID
- GET /api/tools/health - Tools health check
"""

import pytest


class TestToolRegister:
    """Tests for tool registration endpoint."""

    def test_register_tool_success(self, client):
        """Register tool with valid payload returns 201."""
        payload = {
            "tool_id": "web-search",
            "name": "Web Search Tool",
            "version": "1.0.0",
            "description": "Searches the web for information",
        }

        response = client.post("/api/tools/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["tool_id"] == "web-search"
        assert data["name"] == "Web Search Tool"
        assert data["version"] == "1.0.0"
        assert data["description"] == "Searches the web for information"

    def test_register_tool_validation_error_missing_fields(self, client):
        """Register tool with missing required fields returns 422."""
        payload = {"tool_id": "incomplete-tool"}  # Missing name, version, description

        response = client.post("/api/tools/", json=payload)

        assert response.status_code == 422

    def test_register_tool_overwrites_existing(self, client):
        """Registering same tool_id updates the existing tool."""
        # Register first version
        payload_v1 = {
            "tool_id": "updatable-tool",
            "name": "Original Name",
            "version": "1.0.0",
            "description": "Original description",
        }
        client.post("/api/tools/", json=payload_v1)

        # Register updated version with same tool_id
        payload_v2 = {
            "tool_id": "updatable-tool",
            "name": "Updated Name",
            "version": "2.0.0",
            "description": "Updated description",
        }
        response = client.post("/api/tools/", json=payload_v2)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["version"] == "2.0.0"

        # Verify only one tool exists
        list_resp = client.get("/api/tools/")
        assert len(list_resp.json()) == 1


class TestToolGet:
    """Tests for getting tools by ID."""

    def test_get_tool_success(self, client):
        """Get existing tool by ID returns 200."""
        # Register tool first
        payload = {
            "tool_id": "retrievable-tool",
            "name": "Tool to Get",
            "version": "1.0.0",
            "description": "A tool to retrieve",
        }
        client.post("/api/tools/", json=payload)

        response = client.get("/api/tools/retrievable-tool")

        assert response.status_code == 200
        data = response.json()
        assert data["tool_id"] == "retrievable-tool"
        assert data["name"] == "Tool to Get"

    def test_get_tool_not_found(self, client):
        """Get non-existent tool returns 404."""
        response = client.get("/api/tools/nonexistent-tool")

        assert response.status_code == 404
        assert response.json()["detail"] == "Tool not found"


class TestToolList:
    """Tests for listing tools."""

    def test_list_tools_empty(self, client):
        """List tools when none registered returns empty list."""
        response = client.get("/api/tools/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_tools_multiple(self, client):
        """List tools returns all registered tools."""
        # Register multiple tools
        tools = [
            {
                "tool_id": f"tool-{i}",
                "name": f"Tool {i}",
                "version": "1.0.0",
                "description": f"Description {i}",
            }
            for i in range(3)
        ]
        for tool in tools:
            client.post("/api/tools/", json=tool)

        response = client.get("/api/tools/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        tool_ids = [t["tool_id"] for t in data]
        assert "tool-0" in tool_ids
        assert "tool-1" in tool_ids
        assert "tool-2" in tool_ids


class TestToolHealth:
    """Tests for tools health endpoint."""

    def test_tools_health_endpoint(self, client):
        """Tools health check returns ok status."""
        response = client.get("/api/tools/health")

        # NOTE: Due to route ordering in tool_router.py, /health may be
        # matched by /{tool_id}. If this test fails with 404, it's a
        # bug in the router - /health should be defined BEFORE /{tool_id}.
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["router"] == "tools"


class TestToolWorkflow:
    """End-to-end workflow tests."""

    def test_register_then_retrieve(self, client):
        """Full workflow: register -> list -> get by ID."""
        # Register
        payload = {
            "tool_id": "workflow-tool",
            "name": "Workflow Test Tool",
            "version": "1.0.0",
            "description": "Tool for workflow testing",
        }
        reg_resp = client.post("/api/tools/", json=payload)
        assert reg_resp.status_code == 201

        # List - verify it appears
        list_resp = client.get("/api/tools/")
        assert any(t["tool_id"] == "workflow-tool" for t in list_resp.json())

        # Get by ID
        get_resp = client.get("/api/tools/workflow-tool")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "Workflow Test Tool"
