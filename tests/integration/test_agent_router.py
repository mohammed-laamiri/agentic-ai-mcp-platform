"""
Integration tests for Agent Router.

Endpoints:
- POST /api/agents/ - Create agent task
- GET /api/agents/ - List agent tasks
- GET /api/agents/{task_id} - Get agent task by ID
- POST /api/agents/{task_id}/complete - Complete agent task
- POST /api/agents/{task_id}/fail - Fail agent task

IMPORTANT: Agent router uses a SEPARATE TaskService singleton from Task router.
This means tasks created via /api/agents are NOT visible via /api/tasks.
"""

import pytest


class TestAgentTaskCRUD:
    """Tests for agent task CRUD operations."""

    def test_create_agent_task(self, client):
        """Create agent task returns 201."""
        payload = {
            "name": "Agent Task",
            "description": "Task created via agent endpoint",
        }

        response = client.post("/api/agents/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Agent Task"
        assert "id" in data

    def test_get_agent_task(self, client):
        """Get agent task by ID returns 200."""
        # Create via agent endpoint
        create_resp = client.post(
            "/api/agents/", json={"name": "Agent Task to Get"}
        )
        task_id = create_resp.json()["id"]

        response = client.get(f"/api/agents/{task_id}")

        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_list_agent_tasks(self, client):
        """List agent tasks returns all agent-created tasks."""
        client.post("/api/agents/", json={"name": "Agent Task 1"})
        client.post("/api/agents/", json={"name": "Agent Task 2"})

        response = client.get("/api/agents/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_agent_task_not_found(self, client):
        """Get non-existent agent task returns 404."""
        response = client.get("/api/agents/nonexistent-id")

        assert response.status_code == 404


class TestAgentTaskLifecycle:
    """Tests for agent task lifecycle operations."""

    def test_complete_agent_task(self, client):
        """Complete agent task updates status."""
        create_resp = client.post(
            "/api/agents/", json={"name": "Agent Task to Complete"}
        )
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/agents/{task_id}/complete")

        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_fail_agent_task(self, client):
        """Fail agent task updates status and stores error."""
        create_resp = client.post(
            "/api/agents/", json={"name": "Agent Task to Fail"}
        )
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/agents/{task_id}/fail?error=Agent error")

        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert response.json()["result"]["error"] == "Agent error"


class TestAgentTaskIsolation:
    """
    Tests verifying that Agent and Task routers have separate storage.

    This documents the current architecture where each router has its
    own TaskService singleton, resulting in complete data isolation.
    """

    def test_agent_task_not_visible_in_task_router(self, client):
        """Tasks created via /api/agents are NOT visible via /api/tasks."""
        # Create task via agent endpoint
        client.post("/api/agents/", json={"name": "Agent-Only Task"})

        # List via task endpoint - should be empty
        response = client.get("/api/tasks/")

        assert response.status_code == 200
        assert response.json() == []

    def test_task_not_visible_in_agent_router(self, client):
        """Tasks created via /api/tasks are NOT visible via /api/agents."""
        # Create task via task endpoint
        client.post("/api/tasks/", json={"name": "Task-Only Task"})

        # List via agent endpoint - should be empty
        response = client.get("/api/agents/")

        assert response.status_code == 200
        assert response.json() == []

    def test_separate_storage_verified(self, client):
        """Both routers maintain separate task stores."""
        # Create tasks in both routers
        task_resp = client.post("/api/tasks/", json={"name": "Task Router Item"})
        agent_resp = client.post("/api/agents/", json={"name": "Agent Router Item"})

        task_id = task_resp.json()["id"]
        agent_id = agent_resp.json()["id"]

        # Task endpoint only sees task router items
        task_list = client.get("/api/tasks/").json()
        assert len(task_list) == 1
        assert task_list[0]["name"] == "Task Router Item"

        # Agent endpoint only sees agent router items
        agent_list = client.get("/api/agents/").json()
        assert len(agent_list) == 1
        assert agent_list[0]["name"] == "Agent Router Item"

        # Cross-access returns 404
        assert client.get(f"/api/tasks/{agent_id}").status_code == 404
        assert client.get(f"/api/agents/{task_id}").status_code == 404
