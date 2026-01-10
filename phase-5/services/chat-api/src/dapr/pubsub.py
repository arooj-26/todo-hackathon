"""Dapr Pub/Sub client wrapper for event publishing."""

import os
from typing import Any
from uuid import uuid4

import httpx
from pydantic import BaseModel


class DaprPubSubClient:
    """Client for publishing events to Kafka via Dapr Pub/Sub API.

    This wrapper abstracts Kafka operations, allowing technology substitution
    through Dapr component configuration without code changes.
    """

    def __init__(self):
        """Initialize Dapr Pub/Sub client."""
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.pubsub_name = "kafka-pubsub"  # Matches Dapr component name

    async def publish(
        self,
        topic: str,
        event: BaseModel | dict,
        correlation_id: str | None = None,
    ) -> None:
        """Publish event to specified topic.

        Args:
            topic: Kafka topic name (task-events, reminders, task-updates)
            event: Event data (Pydantic model or dict)
            correlation_id: Optional correlation ID for distributed tracing

        Raises:
            httpx.HTTPStatusError: If Dapr returns error response
        """
        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid4())

        # Convert Pydantic model to dict if needed
        event_data = event.dict() if isinstance(event, BaseModel) else event

        # Ensure correlation_id is in event data
        if "correlation_id" not in event_data:
            event_data["correlation_id"] = correlation_id

        # Publish via Dapr HTTP API
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

    async def publish_bulk(
        self,
        topic: str,
        events: list[BaseModel | dict],
        correlation_id: str | None = None,
    ) -> None:
        """Publish multiple events to specified topic.

        Args:
            topic: Kafka topic name
            events: List of event data
            correlation_id: Optional correlation ID for distributed tracing
        """
        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid4())

        # Convert events to dict format
        event_data_list = [
            (event.dict() if isinstance(event, BaseModel) else event)
            for event in events
        ]

        # Ensure correlation_id is in all events
        for event_data in event_data_list:
            if "correlation_id" not in event_data:
                event_data["correlation_id"] = correlation_id

        # Publish via Dapr bulk publish API
        bulk_publish_url = f"{self.dapr_base_url}/v1.0-alpha1/publish/bulk/{self.pubsub_name}/{topic}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                bulk_publish_url,
                json=event_data_list,
                headers={
                    "Content-Type": "application/json",
                    "traceparent": f"00-{correlation_id.replace('-', '')}-0000000000000000-01",
                },
                timeout=10.0,
            )
            response.raise_for_status()


# Global instance (will be initialized on app startup)
dapr_pubsub: DaprPubSubClient | None = None


def get_pubsub_client() -> DaprPubSubClient:
    """Get global Dapr Pub/Sub client instance.

    Returns:
        DaprPubSubClient: Initialized client

    Raises:
        RuntimeError: If client not initialized
    """
    global dapr_pubsub
    if dapr_pubsub is None:
        dapr_pubsub = DaprPubSubClient()
    return dapr_pubsub
