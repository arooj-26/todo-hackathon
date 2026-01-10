"""
Comprehensive error response formatting
Provides consistent error responses with helpful messages
"""

from typing import Optional, Dict, Any
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import structlog

logger = structlog.get_logger(__name__)


class ErrorResponse:
    """Structured error response"""

    def __init__(
        self,
        error: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.correlation_id = correlation_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        response = {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code,
        }

        if self.details:
            response["details"] = self.details

        if self.correlation_id:
            response["correlation_id"] = self.correlation_id

        return response


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation errors with detailed field-level messages
    """
    correlation_id = getattr(request.state, "correlation_id", None)

    # Format validation errors
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    error_response = ErrorResponse(
        error="ValidationError",
        message="Request validation failed. Please check your input.",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details={"validation_errors": errors},
        correlation_id=correlation_id
    )

    logger.warning(
        "validation_error",
        errors=errors,
        correlation_id=correlation_id
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.to_dict()
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic errors with appropriate messages
    """
    correlation_id = getattr(request.state, "correlation_id", None)

    # Determine status code and error type
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
        error_type = type(exc).__name__
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_type = "InternalServerError"

    # Create error response
    error_response = ErrorResponse(
        error=error_type,
        message=str(exc) if str(exc) else "An unexpected error occurred",
        status_code=status_code,
        correlation_id=correlation_id
    )

    logger.error(
        "request_error",
        error_type=error_type,
        error_message=str(exc),
        status_code=status_code,
        correlation_id=correlation_id,
        exc_info=True
    )

    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )


# Common error messages for various scenarios
ERROR_MESSAGES = {
    "not_found": "The requested resource was not found",
    "unauthorized": "Authentication required. Please provide valid credentials",
    "forbidden": "You don't have permission to access this resource",
    "conflict": "A resource with this identifier already exists",
    "bad_request": "Invalid request. Please check your input",
    "internal_error": "An internal server error occurred. Please try again later",
    "service_unavailable": "Service temporarily unavailable. Please try again later",
    "rate_limited": "Too many requests. Please slow down",

    # Database errors
    "database_error": "Database operation failed",
    "connection_error": "Failed to connect to database",
    "constraint_violation": "Operation violates data constraints",

    # Business logic errors
    "task_not_found": "Task not found with the provided ID",
    "invalid_status": "Invalid task status transition",
    "invalid_recurrence": "Invalid recurrence pattern configuration",
    "reminder_conflict": "Reminder time conflicts with task due date",

    # External service errors
    "kafka_error": "Failed to publish event to message queue",
    "dapr_error": "Failed to communicate with service mesh",
    "notification_error": "Failed to send notification",
}


def get_error_message(error_key: str, default: str = None) -> str:
    """Get error message by key"""
    return ERROR_MESSAGES.get(error_key, default or error_key)
