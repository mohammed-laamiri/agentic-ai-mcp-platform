# tests/unit/integration/test_tasks_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.task_service import TaskService

client = TestClient(app)

# ----------------------------
# Fixture to clear in-memory tasks
# ----------------------------
@pytest.fixture(autouse=True)
def clear_tasks():
    """
    Clear the TaskService in-memory storage before each test
    to ensure tests are isolated and consistent.
    """
    TaskService()._tasks.clear()


# ----------------------------
# Helpers
# ----------------------------
def create_sample_task_payload():
    return {
        "name": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": 1,
        "input": {"param": "value"},
    }


# ----------------------------
# Test Task Creation
# ----------------------------
def test_create_task():
    payload = create_sample_task_payload()
    response = client.post("/api/tasks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["status"] == payload["status"]
    assert "id" in data
    assert data["input"] == payload["input"]


# ----------------------------
# Test Get Task by ID
# ----------------------------
def test_get_task():
    payload = create_sample_task_payload()
    create_resp = client.post("/api/tasks/", json=payload)
    task_id = create_resp.json()["id"]

    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["name"] == payload["name"]


# ----------------------------
# Test Complete Task
# ----------------------------
def test_complete_task():
    payload = create_sample_task_payload()
    create_resp = client.post("/api/tasks/", json=payload)
    task_id = create_resp.json()["id"]

    result_payload = {"output": "Task completed successfully"}
    response = client.post(f"/api/tasks/{task_id}/complete", json=result_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "completed"
    assert data["result"] == result_payload
