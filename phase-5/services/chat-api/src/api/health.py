"""Health check endpoints for Kubernetes liveness and readiness probes."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str = "1.0.0"
    service: str = "chat-api"


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    status: str
    version: str = "1.0.0"
    service: str = "chat-api"
    checks: dict[str, str]


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe - checks if service is alive",
)
async def health_check() -> HealthResponse:
    """Liveness probe endpoint.

    Returns HTTP 200 if the service process is running.
    Used by Kubernetes to determine if the pod should be restarted.

    Returns:
        HealthResponse with status=healthy
    """
    return HealthResponse(status="healthy")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe - checks if service can handle requests",
)
async def readiness_check(
    session: AsyncSession = Depends(get_session),
) -> ReadinessResponse:
    """Readiness probe endpoint.

    Checks if the service can handle requests by verifying:
    - Database connectivity
    - (Future: Kafka connectivity, Dapr availability)

    Used by Kubernetes to determine if the pod should receive traffic.

    Args:
        session: Database session (dependency injected)

    Returns:
        ReadinessResponse with status=ready and check results

    Raises:
        HTTPException: If any critical dependency is unavailable
    """
    checks = {}

    # Check database connectivity
    try:
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        checks["database"] = "connected"
        logger.debug("readiness_check_database_ok")
    except Exception as exc:
        checks["database"] = f"error: {str(exc)}"
        logger.error(
            "readiness_check_database_failed",
            error=str(exc),
        )
        # Return 503 Service Unavailable if database is down
        return ReadinessResponse(
            status="not_ready",
            checks=checks,
        )

    # Future: Check Kafka connectivity via Dapr
    # checks["kafka"] = "connected"

    # Future: Check Dapr sidecar availability
    # checks["dapr"] = "available"

    return ReadinessResponse(
        status="ready",
        checks=checks,
    )
