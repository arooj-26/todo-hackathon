"""Error handling middleware for FastAPI."""

import traceback
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

from ..logging_config import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware:
    """Middleware to handle exceptions and return structured error responses.

    Catches all unhandled exceptions, logs them with correlation ID,
    and returns appropriate HTTP error responses to clients.
    """

    def __init__(self, app):
        """Initialize middleware.

        Args:
            app: FastAPI application instance
        """
        self.app = app

    async def __call__(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and handle exceptions.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)
            return response

        except IntegrityError as exc:
            # Database constraint violations (unique, foreign key, etc.)
            logger.error(
                "database_integrity_error",
                error=str(exc),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": "conflict",
                    "message": "Resource conflict (duplicate or constraint violation)",
                    "detail": str(exc.orig) if hasattr(exc, "orig") else str(exc),
                },
            )

        except OperationalError as exc:
            # Database connection/operational errors
            logger.error(
                "database_operational_error",
                error=str(exc),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "error": "service_unavailable",
                    "message": "Database temporarily unavailable",
                    "detail": "Please try again in a moment",
                },
            )

        except ValueError as exc:
            # Validation errors not caught by Pydantic
            logger.warning(
                "validation_error",
                error=str(exc),
                path=request.url.path,
                method=request.method,
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "validation_error",
                    "message": str(exc),
                },
            )

        except Exception as exc:
            # Catch-all for unexpected errors
            logger.error(
                "unhandled_exception",
                error=str(exc),
                error_type=type(exc).__name__,
                path=request.url.path,
                method=request.method,
                traceback=traceback.format_exc(),
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "detail": str(exc) if logger.isEnabledFor(10) else None,  # Include details in DEBUG mode only
                },
            )


def add_error_handler_middleware(app):
    """Add error handling middleware to FastAPI app.

    Args:
        app: FastAPI application instance

    Example:
        from fastapi import FastAPI
        from src.middleware.error_handler import add_error_handler_middleware

        app = FastAPI()
        add_error_handler_middleware(app)
    """
    app.middleware("http")(ErrorHandlerMiddleware(app))
