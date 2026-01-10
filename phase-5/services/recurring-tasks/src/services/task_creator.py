"""Task creator service using Dapr Service Invocation."""

import logging
import os
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class TaskCreator:
    """Service for creating tasks via Chat API using Dapr Service Invocation."""

    def __init__(self):
        """Initialize task creator."""
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        self.chat_api_app_id = os.getenv("CHAT_API_APP_ID", "chat-api")

    async def create_next_task_instance(
        self,
        original_task: dict[str, Any],
        next_due_date: datetime,
        correlation_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """
        Create next recurring task instance via Dapr Service Invocation.

        Args:
            original_task: Original completed task data
            next_due_date: Due date for next instance
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created task data or None if creation failed
        """
        logger.info(
            f"Creating next task instance via Dapr Service Invocation",
            extra={
                "original_task_id": original_task.get("id"),
                "next_due_date": next_due_date.isoformat(),
                "correlation_id": correlation_id,
            },
        )

        # Build task creation payload
        task_payload = {
            "title": original_task.get("title"),
            "description": original_task.get("description"),
            "priority": original_task.get("priority", "medium"),
            "status": "todo",
            "due_at": next_due_date.isoformat(),
            "parent_task_id": original_task.get("id"),
            # Do NOT include recurrence_pattern - it's linked via parent task
        }

        # Invoke Chat API via Dapr Service Invocation
        invoke_url = f"{self.dapr_base_url}/v1.0/invoke/{self.chat_api_app_id}/method/tasks"

        headers = {
            "Content-Type": "application/json",
            "X-User-ID": original_task.get("user_id"),
        }

        if correlation_id:
            headers["X-Correlation-ID"] = correlation_id
            headers["traceparent"] = f"00-{correlation_id.replace('-', '')}-0000000000000000-01"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    invoke_url,
                    json=task_payload,
                    headers=headers,
                )

                if response.status_code == 201:
                    created_task = response.json()
                    logger.info(
                        f"Successfully created next task instance",
                        extra={
                            "original_task_id": original_task.get("id"),
                            "new_task_id": created_task.get("id"),
                            "next_due_date": next_due_date.isoformat(),
                        },
                    )
                    return created_task
                else:
                    logger.error(
                        f"Failed to create next task instance",
                        extra={
                            "original_task_id": original_task.get("id"),
                            "status_code": response.status_code,
                            "response": response.text,
                        },
                    )
                    return None

        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error creating next task instance",
                extra={
                    "original_task_id": original_task.get("id"),
                    "error": str(e),
                },
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error creating next task instance",
                extra={
                    "original_task_id": original_task.get("id"),
                    "error": str(e),
                },
                exc_info=True,
            )
            return None
