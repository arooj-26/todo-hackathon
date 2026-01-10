"""Dapr Pub/Sub client wrapper for event publishing."""

import os
from typing import Any
from uuid import uuid4

import httpx
from pydantic import BaseModel


class DaprPubSubClient:
    """Client for publishing events to Kafka via Dapr Pub/Sub API."""

    def __init__(self):
        """Initialize Dapr Pub/Sub client."""
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.pubsub_name = "kafka-pubsub"

    async def publish(
        self,
        topic: str,
        event: BaseModel | dict,
        correlation_id: str | None = None,
    ) -> None:
        """Publish event to specified topic.

        Args:
            topic: Kafka topic name
            event: Event data
            correlation_id: Optional correlation ID for tracing

        Raises:
            httpx.HTTPStatusError: If Dapr returns error response
        """
        if correlation_id is None:
            correlation_id = str(uuid4())

        event_data = event.dict() if isinstance(event, BaseModel) else event

        if "correlation_id" not in event_data:
            event_data["correlation_id"] = correlation_id

        publish_url = f"{self.dapr_base_url}/v1.0/publish/{self.pubsub_name}/{topic}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                publish_url,
                json=event_data,
                headers={
                    "Content-Type": "application/json",
                    "traceparent": f"00-{correlation_id.replace('-', '')}-0000000000000000-01",
                },
                timeout=5.0,
            )
            response.raise_for_status()


# Global instance
dapr_pubsub: DaprPubSubClient | None = None


def get_pubsub_client() -> DaprPubSubClient:
    """Get global Dapr Pub/Sub client instance.

    Returns:
        DaprPubSubClient: Initialized client
    """
    global dapr_pubsub
    if dapr_pubsub is None:
        dapr_pubsub = DaprPubSubClient()
    return dapr_pubsub
