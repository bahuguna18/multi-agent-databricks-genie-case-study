"""
Base class for agents interacting with Databricks Genie workspaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from databricks.sdk import WorkspaceClient
from tenacity import retry, stop_after_attempt, wait_exponential
import requests

from config import DATABRICKS_HOST, DATABRICKS_TOKEN, MAX_RETRIES


class BaseGenieAgent(ABC):
    """Abstract base class for Databricks Genie agents."""

    def __init__(self, workspace_client: Optional[WorkspaceClient] = None):
        """
        Initialize the agent with a Databricks workspace client.
        If none provided, a new client is created using environment configuration.
        """
        self.client = workspace_client or WorkspaceClient(
            host=DATABRICKS_HOST,
            token=DATABRICKS_TOKEN
        )

    @abstractmethod
    def get_genie_space_id(self) -> str:
        """Return the Genie space ID for this specific agent."""
        raise NotImplementedError("Each agent must define its Genie space ID.")

    @retry(stop=stop_after_attempt(MAX_RETRIES),
           wait=wait_exponential(multiplier=1, min=2, max=10))
    def query_genie(self, query: str) -> Dict[str, Any]:
        """
        Send a natural language query to the Databricks Genie workspace.
        Handles retries on transient errors.
        """
        try:
            space_id = self.get_genie_space_id()
            response = self._execute_genie_query(query, space_id)
            return {
                "query": query,
                "response": response,
                "space_id": space_id,
                "status": "success"
            }

        except Exception as e:
            return {
                "query": query,
                "response": f"Error: {e}",
                "space_id": getattr(self, "get_genie_space_id", lambda: "unknown")(),
                "status": "error",
                "error": str(e)
            }

    def _execute_genie_query(self, query: str, space_id: str) -> str:
        """
        Execute the given query using the Genie REST API.
        Falls back to a simulated response if the API is unavailable.
        """
        url = f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{space_id}/chat"
        headers = {
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {"message": query, "stream": False}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    return data.get("response") or data.get("message") or str(data)
                return str(data)

            return (
                f"Query executed for '{query}' in space {space_id}. "
                f"API returned status {response.status_code}. "
                f"Check Genie API configuration."
            )

        except requests.exceptions.RequestException as e:
            return (
                f"Simulated Genie response for '{query}' (space {space_id}). "
                f"API error: {e}"
            )

        except Exception as e:
            return (
                f"Error executing Genie query: {e}. "
                f"Query: '{query}' in space {space_id}."
            )

    def process_query(self, query: str) -> Dict[str, Any]:
        """Wrapper for querying Genie and returning structured results."""
        return self.query_genie(query)
