"""
Integration tests for Task Router.

Endpoints:
- POST /api/tasks/ - Create task
- GET /api/tasks/ - List tasks
- GET /api/tasks/{task_id} - Get task by ID
- POST /api/tasks/{task_id}/complete - Complete task
- POST /api/tasks/{task_id}/fail - Fail task
"""

import pytest


class TestTaskCreate:
    """Tests for task creation endpoint."""

    def test_create_task_success(self, client):
        """Create task with full payload returns 201."""
        payload = {
            "name": "Test Task",
            "description": "A test task description",
            "status": "pending",
            "priority": 2,
            "input": {"key": "value"},
        }

        response = client.post("/api/tasks/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Task"
        assert data["description"] == "A test task description"
        assert data["status"] == "pending"
        assert data["priority"] == 2
        assert data["input"] == {"key": "value"}
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_minimal_payload(self, client):
        """Create task with only required field (name) succeeds."""
        payload = {"name": "Minimal Task"}

        response = client.post("/api/tasks/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Task"
        assert data["status"] == "pending"  # Default
        assert data["priority"] == 1  # Default

    def test_create_task_validation_error_missing_name(self, client):
        """Create task without name returns 422."""
        payload = {"description": "No name provided"}

        response = client.post("/api/tasks/", json=payload)

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert any("name" in str(err) for err in detail)


class TestTaskGet:
    """Tests for getting tasks by ID."""

    def test_get_task_success(self, client):
        """Get existing task by ID returns 200."""
        # Create a task first
        create_resp = client.post(
            "/api/tasks/", json={"name": "Task to Get", "description": "Test"}
        )
        task_id = create_resp.json()["id"]

        response = client.get(f"/api/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["name"] == "Task to Get"

    def test_get_task_not_found(self, client):
        """Get non-existent task returns 404."""
        response = client.get("/api/tasks/nonexistent-id-12345")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestTaskList:
    """Tests for listing tasks."""

    def test_list_tasks_empty(self, client):
        """List tasks when none exist returns empty list."""
        response = client.get("/api/tasks/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_data(self, client):
        """List tasks returns all created tasks."""
        # Create multiple tasks
        client.post("/api/tasks/", json={"name": "Task 1"})
        client.post("/api/tasks/", json={"name": "Task 2"})
        client.post("/api/tasks/", json={"name": "Task 3"})

        response = client.get("/api/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        names = [t["name"] for t in data]
        assert "Task 1" in names
        assert "Task 2" in names
        assert "Task 3" in names


class TestTaskPagination:
    """Tests for task list pagination."""

    @pytest.fixture
    def populated_tasks(self, client):
        """Create 10 tasks for pagination testing."""
        for i in range(10):
            client.post("/api/tasks/", json={"name": f"Task {i:02d}"})
        return 10

    def test_list_tasks_pagination_skip(self, client, populated_tasks):
        """Skip parameter skips first N tasks."""
        response = client.get("/api/tasks/?skip=7")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 10 - 7 = 3 remaining

    def test_list_tasks_pagination_limit(self, client, populated_tasks):
        """Limit parameter returns max N tasks."""
        response = client.get("/api/tasks/?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_tasks_pagination_combined(self, client, populated_tasks):
        """Skip and limit work together."""
        response = client.get("/api/tasks/?skip=3&limit=4")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_list_tasks_pagination_skip_beyond_count(self, client, populated_tasks):
        """Skip beyond total count returns empty list."""
        response = client.get("/api/tasks/?skip=20")

        assert response.status_code == 200
        assert response.json() == []


class TestTaskComplete:
    """Tests for completing tasks."""

    def test_complete_task_success(self, client):
        """Complete task updates status to completed."""
        # Create task
        create_resp = client.post("/api/tasks/", json={"name": "Task to Complete"})
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/tasks/{task_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None

    def test_complete_task_with_result(self, client):
        """Complete task with result payload stores it."""
        # Create task
        create_resp = client.post("/api/tasks/", json={"name": "Task with Result"})
        task_id = create_resp.json()["id"]

        result_payload = {"output": "Success!", "metrics": {"score": 100}}
        response = client.post(f"/api/tasks/{task_id}/complete", json=result_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"] == result_payload

    def test_complete_task_not_found(self, client):
        """Complete non-existent task returns 404."""
        response = client.post("/api/tasks/nonexistent-id/complete")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestTaskFail:
    """Tests for failing tasks."""

    def test_fail_task_success(self, client):
        """Fail task updates status to failed."""
        # Create task
        create_resp = client.post("/api/tasks/", json={"name": "Task to Fail"})
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/tasks/{task_id}/fail?error=Something went wrong")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["completed_at"] is not None

    def test_fail_task_stores_error(self, client):
        """Fail task stores error message in result."""
        # Create task
        create_resp = client.post("/api/tasks/", json={"name": "Task with Error"})
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/tasks/{task_id}/fail?error=Connection timeout")

        assert response.status_code == 200
        data = response.json()
        assert data["result"]["error"] == "Connection timeout"

    def test_fail_task_not_found(self, client):
        """Fail non-existent task returns 404."""
        response = client.post("/api/tasks/nonexistent-id/fail?error=test")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestTaskExecute:
    """Tests for executing tasks via orchestrator."""

    def test_execute_task_success(self, client):
        """Execute task via orchestrator updates status to completed."""
        # Create task
        create_resp = client.post("/api/tasks/", json={"name": "Task to Execute", "description": "Test execution"})
        task_id = create_resp.json()["id"]

        response = client.post(f"/api/tasks/{task_id}/execute")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
        assert data["result"] is not None
        # Result should contain execution data
        assert "execution_id" in data["result"]
        assert "output" in data["result"]

    def test_execute_task_not_found(self, client):
        """Execute non-existent task returns 404."""
        response = client.post("/api/tasks/nonexistent-id/execute")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"


class TestTaskWorkflow:
    """End-to-end workflow tests."""

    def test_full_lifecycle_create_to_complete(self, client):
        """Full workflow: create -> list -> get -> complete -> verify."""
        # Create
        payload = {"name": "Lifecycle Test", "description": "Full workflow test"}
        create_resp = client.post("/api/tasks/", json=payload)
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]

        # List - verify it appears
        list_resp = client.get("/api/tasks/")
        assert any(t["id"] == task_id for t in list_resp.json())

        # Get by ID
        get_resp = client.get(f"/api/tasks/{task_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["status"] == "pending"

        # Complete
        complete_resp = client.post(
            f"/api/tasks/{task_id}/complete", json={"output": "Done!"}
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"

        # Verify final state
        final_resp = client.get(f"/api/tasks/{task_id}")
        assert final_resp.json()["status"] == "completed"
        assert final_resp.json()["result"]["output"] == "Done!"

    def test_full_lifecycle_create_to_fail(self, client):
        """Full workflow: create -> get -> fail -> verify."""
        # Create
        create_resp = client.post("/api/tasks/", json={"name": "Fail Workflow Test"})
        task_id = create_resp.json()["id"]

        # Get - verify pending
        get_resp = client.get(f"/api/tasks/{task_id}")
        assert get_resp.json()["status"] == "pending"

        # Fail
        fail_resp = client.post(f"/api/tasks/{task_id}/fail?error=Test failure")
        assert fail_resp.status_code == 200

        # Verify final state
        final_resp = client.get(f"/api/tasks/{task_id}")
        assert final_resp.json()["status"] == "failed"
        assert final_resp.json()["result"]["error"] == "Test failure"
