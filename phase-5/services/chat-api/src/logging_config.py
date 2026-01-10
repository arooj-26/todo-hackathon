"""Structured logging configuration with correlation ID support."""

import logging
import sys
from contextvars import ContextVar
from typing import Any

import structlog

# Context variable for correlation ID tracking across async contexts
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Get current correlation ID from context.

    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in current context.

    Args:
        correlation_id: Correlation ID to set
    """
    correlation_id_var.set(correlation_id)


def add_correlation_id(
    logger: logging.Logger, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Add correlation ID to log events.

    This processor adds the correlation ID from the context variable
    to every log event for distributed tracing.

    Args:
        logger: Logger instance
        method_name: Name of the logging method
        event_dict: Event dictionary to process

    Returns:
        Updated event dictionary with correlation_id
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Sets up structlog with JSON output, correlation ID tracking,
    and proper log levels for production use.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level to event dict
            structlog.stdlib.add_log_level,
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Add correlation ID from context
            add_correlation_id,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # Add stack info for exceptions
            structlog.processors.StackInfoRenderer(),
            # Format exceptions
            structlog.processors.format_exc_info,
            # Add call site info (file, line, function) - disabled in production for performance
            # structlog.processors.CallsiteParameterAdder(
            #     [
            #         structlog.processors.CallsiteParameter.FILENAME,
            #         structlog.processors.CallsiteParameter.LINENO,
            #         structlog.processors.CallsiteParameter.FUNC_NAME,
            #     ]
            # ),
            # Render to JSON for structured logging
            structlog.processors.JSONRenderer(),
        ],
        # Wrapper class for standard library logging
        wrapper_class=structlog.stdlib.BoundLogger,
        # Context class for binding data
        context_class=dict,
        # Logger factory
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("task_created", task_id=123, user_id="abc-123")
    """
    return structlog.get_logger(name)
