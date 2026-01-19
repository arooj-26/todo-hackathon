"""Tag API endpoints for tag management and autocomplete."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.middleware import get_current_user
from ..database import get_session
from ..logging_config import get_correlation_id, get_logger, set_correlation_id
from ..models.tag import TagCreate, TagListResponse, TagResponse
from ..models.user import User
from ..services.tag_service import TagService
from .tasks import _get_correlation_id_from_request

logger = get_logger(__name__)

router = APIRouter(prefix="/tags", tags=["tags"])


async def _get_tag_service(session: AsyncSession = Depends(get_session)) -> TagService:
    """Get tag service instance.

    Args:
        session: Database session

    Returns:
        TagService instance
    """
    return TagService(session)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    tag_data: TagCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: TagService = Depends(_get_tag_service),
) -> TagResponse:
    """Create a new tag.

    If a tag with the same name already exists, returns the existing tag.

    Args:
        tag_data: Tag creation data
        request: FastAPI request
        current_user: Authenticated user from JWT token
        service: Tag service

    Returns:
        Created or existing tag

    Raises:
        HTTPException: If validation fails or creation fails

    Example:
        POST /tags
        {
            "name": "backend"
        }
    """
    user_id = current_user.id
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Creating tag via API",
        user_id=str(user_id),
        tag_name=tag_data.name,
    )

    try:
        tag = await service.create_tag(
            tag_data=tag_data,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        return TagResponse(
            id=tag.id,
            name=tag.name,
            usage_count=tag.usage_count,
        )
    except ValueError as e:
        logger.error("Tag creation validation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Tag creation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create tag")


@router.get("", response_model=TagListResponse)
async def list_tags(
    request: Request,
    current_user: User = Depends(get_current_user),
    search: Optional[str] = Query(
        None,
        description="Search string for autocomplete (matches tags containing this string)",
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tags to return"),
    service: TagService = Depends(_get_tag_service),
) -> TagListResponse:
    """List tags with optional search filter for autocomplete.

    Tags are ordered by usage count (descending) for autocomplete ranking.
    Most used tags appear first.

    Args:
        request: FastAPI request
        current_user: Authenticated user from JWT token
        search: Optional search string for filtering tags
        limit: Maximum tags to return (1-100)
        service: Tag service

    Returns:
        List of tags ordered by usage count

    Example:
        GET /tags?search=back&limit=10

        Returns tags containing "back" (e.g., "backend", "feedback")
        ordered by most frequently used first.
    """
    user_id = current_user.id
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Listing tags via API",
        user_id=str(user_id),
        search=search,
        limit=limit,
    )

    try:
        tags = await service.list_tags(
            user_id=user_id,
            search=search,
            limit=limit,
            correlation_id=correlation_id,
        )

        tag_responses = [
            TagResponse(
                id=tag.id,
                name=tag.name,
                usage_count=tag.usage_count,
            )
            for tag in tags
        ]

        return TagListResponse(tags=tag_responses)
    except Exception as e:
        logger.error("Tag listing failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list tags")
