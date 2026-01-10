"""Tag service for tag management and autocomplete."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..logging_config import get_logger
from ..models.tag import Tag, TagCreate, TaskTag

logger = get_logger(__name__)


class TagService:
    """Service for tag management with autocomplete and usage tracking."""

    def __init__(self, session: AsyncSession):
        """Initialize tag service.

        Args:
            session: Database session
        """
        self.session = session

    async def create_tag(
        self,
        tag_data: TagCreate,
        user_id: UUID,
        correlation_id: Optional[str] = None,
    ) -> Tag:
        """Create a new tag or return existing tag with same name.

        Args:
            tag_data: Tag creation data
            user_id: User ID creating the tag
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created or existing tag instance
        """
        logger.info(
            "Creating tag",
            user_id=str(user_id),
            tag_name=tag_data.name,
            correlation_id=correlation_id,
        )

        # Check if tag already exists
        result = await self.session.execute(
            select(Tag).where(Tag.name == tag_data.name)
        )
        existing_tag = result.scalar_one_or_none()

        if existing_tag:
            logger.info(
                "Tag already exists",
                tag_id=existing_tag.id,
                tag_name=existing_tag.name,
            )
            return existing_tag

        # Create new tag
        tag = Tag(name=tag_data.name, usage_count=0)
        self.session.add(tag)
        await self.session.commit()
        await self.session.refresh(tag)

        logger.info(
            "Tag created",
            tag_id=tag.id,
            tag_name=tag.name,
        )

        return tag

    async def list_tags(
        self,
        user_id: UUID,
        search: Optional[str] = None,
        limit: int = 50,
        correlation_id: Optional[str] = None,
    ) -> list[Tag]:
        """List tags with optional search filter and autocomplete ranking.

        Tags are ranked by usage count (most used first) when search is provided.

        Args:
            user_id: User ID requesting tags
            search: Optional search string for autocomplete
            limit: Maximum number of tags to return
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of tags ordered by usage count (descending)
        """
        logger.info(
            "Listing tags",
            user_id=str(user_id),
            search=search,
            limit=limit,
            correlation_id=correlation_id,
        )

        # Build query
        query = select(Tag)

        # Add search filter if provided
        if search:
            # Match tags that start with search string or contain it
            search_pattern = f"%{search.lower()}%"
            query = query.where(Tag.name.ilike(search_pattern))

        # Order by usage count (descending) for autocomplete ranking
        query = query.order_by(Tag.usage_count.desc()).limit(limit)

        # Execute query
        result = await self.session.execute(query)
        tags = result.scalars().all()

        logger.info(
            "Tags retrieved",
            count=len(tags),
            search=search,
        )

        return list(tags)

    async def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by name.

        Args:
            name: Tag name to retrieve

        Returns:
            Tag instance or None if not found
        """
        result = await self.session.execute(
            select(Tag).where(Tag.name == name)
        )
        return result.scalar_one_or_none()

    async def get_or_create_tag(self, name: str) -> Tag:
        """Get existing tag by name or create a new one.

        Args:
            name: Tag name

        Returns:
            Tag instance
        """
        # Check if tag exists
        tag = await self.get_tag_by_name(name)

        if tag:
            return tag

        # Create new tag
        tag = Tag(name=name, usage_count=0)
        self.session.add(tag)
        await self.session.flush()

        return tag

    async def associate_tags_with_task(
        self,
        task_id: int,
        tag_names: list[str],
        correlation_id: Optional[str] = None,
    ) -> list[Tag]:
        """Associate multiple tags with a task.

        Creates tags if they don't exist and increments usage count.

        Args:
            task_id: Task ID to associate tags with
            tag_names: List of tag names to associate
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of associated tags
        """
        logger.info(
            "Associating tags with task",
            task_id=task_id,
            tag_names=tag_names,
            correlation_id=correlation_id,
        )

        tags = []

        for tag_name in tag_names:
            # Get or create tag
            tag = await self.get_or_create_tag(tag_name)

            # Check if association already exists
            result = await self.session.execute(
                select(TaskTag).where(
                    TaskTag.task_id == task_id,
                    TaskTag.tag_id == tag.id,
                )
            )
            existing_association = result.scalar_one_or_none()

            if not existing_association:
                # Create association
                task_tag = TaskTag(task_id=task_id, tag_id=tag.id)
                self.session.add(task_tag)

                # Increment usage count
                tag.usage_count += 1

            tags.append(tag)

        await self.session.flush()

        logger.info(
            "Tags associated with task",
            task_id=task_id,
            tag_count=len(tags),
        )

        return tags

    async def remove_task_tags(
        self,
        task_id: int,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Remove all tag associations for a task and decrement usage counts.

        Args:
            task_id: Task ID to remove tags from
            correlation_id: Optional correlation ID for tracing
        """
        logger.info(
            "Removing task tags",
            task_id=task_id,
            correlation_id=correlation_id,
        )

        # Get all tag associations for task
        result = await self.session.execute(
            select(TaskTag).where(TaskTag.task_id == task_id)
        )
        task_tags = result.scalars().all()

        # Decrement usage count for each tag
        for task_tag in task_tags:
            tag_result = await self.session.execute(
                select(Tag).where(Tag.id == task_tag.tag_id)
            )
            tag = tag_result.scalar_one_or_none()

            if tag and tag.usage_count > 0:
                tag.usage_count -= 1

            # Delete association
            await self.session.delete(task_tag)

        await self.session.flush()

        logger.info(
            "Task tags removed",
            task_id=task_id,
            removed_count=len(task_tags),
        )

    async def get_task_tags(self, task_id: int) -> list[Tag]:
        """Get all tags for a task.

        Args:
            task_id: Task ID to get tags for

        Returns:
            List of tags
        """
        # Query tags through task_tags join
        result = await self.session.execute(
            select(Tag)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == task_id)
            .order_by(Tag.name)
        )
        tags = result.scalars().all()

        return list(tags)

    async def recalculate_tag_usage_counts(self) -> None:
        """Recalculate usage counts for all tags.

        This is useful for fixing inconsistencies in usage counts.
        Can be run as a maintenance task.
        """
        logger.info("Recalculating tag usage counts")

        # Get all tags
        result = await self.session.execute(select(Tag))
        tags = result.scalars().all()

        for tag in tags:
            # Count associations
            count_result = await self.session.execute(
                select(func.count(TaskTag.task_id)).where(TaskTag.tag_id == tag.id)
            )
            count = count_result.scalar()

            # Update usage count
            tag.usage_count = count

        await self.session.commit()

        logger.info(
            "Tag usage counts recalculated",
            tag_count=len(tags),
        )
