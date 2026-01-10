"""Dapr State API client wrapper for state management."""

import os
from typing import Any, Optional

import httpx


class DaprStateClient:
    """Client for state management via Dapr State API.

    This wrapper abstracts PostgreSQL state operations, allowing technology
    substitution through Dapr component configuration.
    """

    def __init__(self):
        """Initialize Dapr State client."""
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.store_name = "statestore"  # Matches Dapr component name

    async def get(self, key: str) -> Optional[dict]:
        """Get state value by key.

        Args:
            key: State key

        Returns:
            State value as dict, or None if not found
        """
        state_url = f"{self.dapr_base_url}/v1.0/state/{self.store_name}/{key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(state_url, timeout=5.0)

            if response.status_code == 204:  # No content
                return None

            response.raise_for_status()
            return response.json()

    async def set(
        self,
        key: str,
        value: dict,
        etag: Optional[str] = None,
    ) -> None:
        """Set state value by key.

        Args:
            key: State key
            value: State value (must be JSON-serializable dict)
            etag: Optional ETag for optimistic concurrency control

        Raises:
            httpx.HTTPStatusError: If Dapr returns error (e.g., ETag mismatch)
        """
        state_url = f"{self.dapr_base_url}/v1.0/state/{self.store_name}"

        state_operations = [
            {
                "key": key,
                "value": value,
            }
        ]

        if etag:
            state_operations[0]["etag"] = etag

        async with httpx.AsyncClient() as client:
            response = await client.post(
                state_url,
                json=state_operations,
                timeout=5.0,
            )
            response.raise_for_status()

    async def delete(self, key: str, etag: Optional[str] = None) -> None:
        """Delete state by key.

        Args:
            key: State key
            etag: Optional ETag for optimistic concurrency control
        """
        state_url = f"{self.dapr_base_url}/v1.0/state/{self.store_name}/{key}"

        params = {}
        if etag:
            params["etag"] = etag

        async with httpx.AsyncClient() as client:
            response = await client.delete(state_url, params=params, timeout=5.0)
            response.raise_for_status()

    async def get_bulk(self, keys: list[str]) -> dict[str, dict]:
        """Get multiple state values by keys.

        Args:
            keys: List of state keys

        Returns:
            Dict mapping keys to their values
        """
        bulk_get_url = f"{self.dapr_base_url}/v1.0/state/{self.store_name}/bulk"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                bulk_get_url,
                json={"keys": keys},
                timeout=10.0,
            )
            response.raise_for_status()

            # Parse response: [{"key": "k1", "data": {...}}, ...]
            results = response.json()
            return {item["key"]: item.get("data") for item in results}

    async def transaction(
        self,
        operations: list[dict],
    ) -> None:
        """Execute multiple state operations as a transaction.

        Args:
            operations: List of operation dicts with "operation" (upsert/delete),
                       "request" (key, value, etag)

        Example:
            await state_client.transaction([
                {
                    "operation": "upsert",
                    "request": {"key": "key1", "value": {"data": "value1"}}
                },
                {
                    "operation": "delete",
                    "request": {"key": "key2"}
                }
            ])
        """
        transaction_url = f"{self.dapr_base_url}/v1.0/state/{self.store_name}/transaction"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                transaction_url,
                json={"operations": operations},
                timeout=10.0,
            )
            response.raise_for_status()


# Global instance
dapr_state: DaprStateClient | None = None


def get_state_client() -> DaprStateClient:
    """Get global Dapr State client instance.

    Returns:
        DaprStateClient: Initialized client
    """
    global dapr_state
    if dapr_state is None:
        dapr_state = DaprStateClient()
    return dapr_state
