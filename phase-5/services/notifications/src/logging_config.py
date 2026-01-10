"""Logging configuration with structured logging and correlation ID support."""

import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import structlog

# Context variable to store correlation ID
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def set_correlation_id(correlation_id: str | None = None) -> str:
    """Set correlation ID for current context.

    Args:
        correlation_id: Optional correlation ID. If not provided, generates a new one.

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid4())
    correlation_id_ctx.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str | None:
    """Get correlation ID from current context.

    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id_ctx.get()


def add_correlation_id(logger: Any, method_name: str, event_dict: dict) -> dict:
    """Add correlation ID to log event.

    Args:
        logger: Logger instance
        method_name: Log method name
        event_dict: Event dictionary

    Returns:
        Updated event dictionary with correlation ID
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def configure_logging() -> None:
    """Configure structured logging with JSON output."""
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            add_correlation_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)


# Configure logging on module import
configure_logging()
