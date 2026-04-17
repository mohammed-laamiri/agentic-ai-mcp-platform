"""
API Client for FastAPI Backend.

Provides httpx-based client for all backend API operations.
"""

from typing import Any
import httpx
from django.conf import settings

from .exceptions import APIError, APIConnectionError, APINotFoundError


class APIClient:
    """
    HTTP client for the Agentic AI MCP Platform backend API.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self.base_url = base_url or settings.BACKEND_API_URL
        self.timeout = timeout

    def _get_client(self) -> httpx.Client:
        return httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 404:
            raise APINotFoundError(f"Resource not found: {response.url}")
        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise APIError(f"API error ({response.status_code}): {detail}")
        return response.json()

    # ==========================================
    # Health
    # ==========================================

    def health_check(self) -> dict[str, Any]:
        """Check backend API health."""
        try:
            with self._get_client() as client:
                response = client.get("/health")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # Tasks
    # ==========================================

    def list_tasks(self, skip: int = 0, limit: int = 20) -> list[dict[str, Any]]:
        """List all tasks with pagination."""
        try:
            with self._get_client() as client:
                response = client.get("/tasks/", params={"skip": skip, "limit": limit})
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Get a single task by ID."""
        try:
            with self._get_client() as client:
                response = client.get(f"/tasks/{task_id}")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        try:
            with self._get_client() as client:
                response = client.post("/tasks/", json=data)
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def execute_task(self, task_id: str) -> dict[str, Any]:
        """Execute a task via orchestrator."""
        try:
            with self._get_client() as client:
                response = client.post(f"/tasks/{task_id}/execute")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def complete_task(self, task_id: str, result: dict[str, Any] | None = None) -> dict[str, Any]:
        """Mark a task as completed."""
        try:
            with self._get_client() as client:
                payload = {"result": result or {}}
                response = client.post(f"/tasks/{task_id}/complete", json=payload)
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def fail_task(self, task_id: str, error: str) -> dict[str, Any]:
        """Mark a task as failed."""
        try:
            with self._get_client() as client:
                payload = {"error": error}
                response = client.post(f"/tasks/{task_id}/fail", json=payload)
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # Tools
    # ==========================================

    def list_tools(self) -> list[dict[str, Any]]:
        """List all registered tools."""
        try:
            with self._get_client() as client:
                response = client.get("/tools/")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        """Get a single tool by ID."""
        try:
            with self._get_client() as client:
                response = client.get(f"/tools/{tool_id}")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def register_tool(self, data: dict[str, Any]) -> dict[str, Any]:
        """Register a new tool."""
        try:
            with self._get_client() as client:
                response = client.post("/tools/", json=data)
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # Agents
    # ==========================================

    def list_agents(self) -> list[dict[str, Any]]:
        """List all agents."""
        try:
            with self._get_client() as client:
                response = client.get("/agents/")
                return self._handle_response(response)
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")


# Singleton instance
api_client = APIClient()
