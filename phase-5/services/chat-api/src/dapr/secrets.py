"""Dapr Secrets API client wrapper for secure credential management."""

import os
from typing import Optional

import httpx


class DaprSecretsClient:
    """Client for retrieving secrets via Dapr Secrets API.

    This wrapper abstracts Kubernetes secrets access, ensuring credentials
    are never hardcoded in application code.
    """

    def __init__(self):
        """Initialize Dapr Secrets client."""
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.secret_store_name = "kubernetes-secrets"  # Matches Dapr component name

    async def get_secret(
        self,
        secret_name: str,
        key: Optional[str] = None,
    ) -> str | dict[str, str]:
        """Get secret value from Kubernetes secret store.

        Args:
            secret_name: Name of Kubernetes secret
            key: Optional specific key within secret (if multi-key secret)

        Returns:
            Secret value as string (if key specified) or dict of all keys

        Raises:
            httpx.HTTPStatusError: If secret not found or access denied
        """
        secrets_url = f"{self.dapr_base_url}/v1.0/secrets/{self.secret_store_name}/{secret_name}"

        # Add metadata to request specific key
        params = {}
        if key:
            params["metadata.key"] = key

        async with httpx.AsyncClient() as client:
            response = await client.get(secrets_url, params=params, timeout=5.0)
            response.raise_for_status()

            secret_data = response.json()

            # If specific key requested, return just that value
            if key and key in secret_data:
                return secret_data[key]

            # Otherwise return all keys
            return secret_data

    async def get_bulk_secrets(
        self,
        secret_names: list[str],
    ) -> dict[str, dict[str, str]]:
        """Get multiple secrets in a single call.

        Args:
            secret_names: List of secret names to retrieve

        Returns:
            Dict mapping secret names to their key-value pairs
        """
        bulk_secrets_url = f"{self.dapr_base_url}/v1.0/secrets/{self.secret_store_name}/bulk"

        async with httpx.AsyncClient() as client:
            response = await client.get(bulk_secrets_url, timeout=10.0)
            response.raise_for_status()

            all_secrets = response.json()

            # Filter to requested secrets only
            return {
                name: all_secrets.get(name, {})
                for name in secret_names
                if name in all_secrets
            }


# Global instance
dapr_secrets: DaprSecretsClient | None = None


def get_secrets_client() -> DaprSecretsClient:
    """Get global Dapr Secrets client instance.

    Returns:
        DaprSecretsClient: Initialized client
    """
    global dapr_secrets
    if dapr_secrets is None:
        dapr_secrets = DaprSecretsClient()
    return dapr_secrets
