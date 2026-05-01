"""
API Client for FastAPI Backend.

Provides httpx-based client for all backend API operations.
"""

from typing import Any, Dict, List, Optional, Union

import httpx
from django.conf import settings

from core.exceptions import APIError, APIConnectionError, APINotFoundError


class APIClient:
    """
    HTTP client for the Agentic AI MCP Platform backend API.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url or getattr(settings, "BACKEND_API_URL", "http://localhost:8000")
        self.timeout = timeout

    def _get_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response safely."""
        if response.status_code == 404:
            raise APINotFoundError(f"Resource not found: {response.url}")

        if response.status_code >= 400:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text

            raise APIError(f"API error ({response.status_code}): {detail}")

        try:
            return response.json()
        except Exception:
            return response.text

    # ==========================================
    # HEALTH
    # ==========================================

    def health_check(self) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.get("/health")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # TASKS
    # ==========================================

    def list_tasks(self, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            with self._get_client() as client:
                response = client.get(
                    "/tasks/",
                    params={"skip": skip, "limit": limit},
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def get_task(self, task_id: str) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.get(f"/tasks/{task_id}")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.post("/tasks/", json=data)
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.post(f"/tasks/{task_id}/execute")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def complete_task(
        self,
        task_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                payload = {"result": result or {}}
                response = client.post(f"/tasks/{task_id}/complete", json=payload)
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def fail_task(self, task_id: str, error: str) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.post(
                    f"/tasks/{task_id}/fail",
                    json={"error": error},
                )
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # TOOLS
    # ==========================================

    def list_tools(self) -> List[Dict[str, Any]]:
        try:
            with self._get_client() as client:
                response = client.get("/tools/")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def get_tool(self, tool_id: str) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.get(f"/tools/{tool_id}")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    def register_tool(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            with self._get_client() as client:
                response = client.post("/tools/", json=data)
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")

    # ==========================================
    # AGENTS
    # ==========================================

    def list_agents(self) -> List[Dict[str, Any]]:
        try:
            with self._get_client() as client:
                response = client.get("/agents/")
                return self._handle_response(response)
        except httpx.RequestError as e:
            raise APIConnectionError(f"Cannot connect to backend: {e}")


# Singleton instance (DO NOT CHANGE)
api_client = APIClient()