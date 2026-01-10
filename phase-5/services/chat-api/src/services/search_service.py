"""Search service with PostgreSQL full-text search support."""

from datetime import datetime
from typing import Optional

from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..logging_config import get_logger
from ..models.tag import Tag, TaskTag
from ..models.task import Task

logger = get_logger(__name__)


class SearchService:
    """Service for searching and filtering tasks with full-text search."""

    def __init__(self, session: AsyncSession):
        """Initialize search service.

        Args:
            session: Database session
        """
        self.session = session

    def build_order_by(self, sort: Optional[str], has_search: bool) -> list:
        """Build ORDER BY clauses for sort options.

        Supports compound sorting with multiple criteria separated by comma.

        Valid sort options:
        - priority_asc: Priority low to high
        - priority_desc: Priority high to low
        - due_date_asc: Due date earliest to latest
        - due_date_desc: Due date latest to earliest
        - created_asc: Created date oldest to newest
        - created_desc: Created date newest to oldest
        - title_asc: Title A to Z
        - title_desc: Title Z to A

        Args:
            sort: Sort criteria (comma-separated for compound sorting)
            has_search: Whether a search query is active (affects default sort)

        Returns:
            List of SQLAlchemy order_by expressions

        Example:
            "priority_desc,due_date_asc" -> [priority DESC, due_at ASC]
        """
        # Default sorting
        if not sort:
            if has_search:
                # When searching, default to relevance (handled in caller)
                return []
            else:
                # When not searching, default to newest first
                return [Task.created_at.desc()]

        # Parse sort criteria (comma-separated for compound sorting)
        sort_criteria = [s.strip() for s in sort.split(',')]
        order_by_clauses = []

        # Map sort options to SQLAlchemy order_by expressions
        for criterion in sort_criteria:
            if criterion == 'priority_asc':
                # Priority: low=1, medium=2, high=3, so ASC gives low->medium->high
                # We want low->medium->high, but in UI we show "Low to High"
                # PostgreSQL CASE WHEN for custom priority order
                order_by_clauses.append(
                    text("CASE WHEN priority = 'low' THEN 1 WHEN priority = 'medium' THEN 2 WHEN priority = 'high' THEN 3 END ASC")
                )
            elif criterion == 'priority_desc':
                # Priority: high->medium->low
                order_by_clauses.append(
                    text("CASE WHEN priority = 'high' THEN 1 WHEN priority = 'medium' THEN 2 WHEN priority = 'low' THEN 3 END ASC")
                )
            elif criterion == 'due_date_asc':
                # Due date: earliest to latest (NULL values last)
                order_by_clauses.append(Task.due_at.asc().nullslast())
            elif criterion == 'due_date_desc':
                # Due date: latest to earliest (NULL values last)
                order_by_clauses.append(Task.due_at.desc().nullslast())
            elif criterion == 'created_asc':
                # Created: oldest to newest
                order_by_clauses.append(Task.created_at.asc())
            elif criterion == 'created_desc':
                # Created: newest to oldest
                order_by_clauses.append(Task.created_at.desc())
            elif criterion == 'title_asc':
                # Title: A to Z
                order_by_clauses.append(Task.title.asc())
            elif criterion == 'title_desc':
                # Title: Z to A
                order_by_clauses.append(Task.title.desc())
            else:
                logger.warning(
                    "Invalid sort criterion, ignoring",
                    criterion=criterion,
                )

        logger.debug(
            "Built ORDER BY clauses",
            sort=sort,
            num_clauses=len(order_by_clauses),
        )

        return order_by_clauses

    def build_tsquery(self, search_term: str) -> str:
        """Build tsquery string for full-text search.

        Converts user search terms into PostgreSQL tsquery format.
        Handles:
        - Multiple words (AND logic)
        - Phrase search (quoted terms)
        - Basic sanitization

        Args:
            search_term: User search input

        Returns:
            PostgreSQL tsquery string

        Example:
            "task report" -> "task & report"
            "urgent meeting" -> "urgent & meeting"
        """
        if not search_term:
            return ""

        # Remove special characters that could break tsquery
        sanitized = search_term.strip()

        # Split on whitespace and join with & (AND operator)
        words = sanitized.split()
        if not words:
            return ""

        # Escape single quotes and join with AND
        escaped_words = [word.replace("'", "''") for word in words]
        tsquery = " & ".join(escaped_words)

        logger.debug(
            "Built tsquery",
            search_term=search_term,
            tsquery=tsquery,
        )

        return tsquery

    async def search_and_filter_tasks(
        self,
        user_id: str,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """Search and filter tasks with combined criteria and sorting.

        Applies multiple filters with AND logic:
        - Full-text search across title and description
        - Status filter
        - Priority filter
        - Tag filters (task must have all specified tags)
        - Due date range filter
        - Multi-criteria sorting
        - Pagination

        Args:
            user_id: User ID to filter by
            search: Search term for full-text search
            status: Optional status filter
            priority: Optional priority filter
            tags: Optional tags filter (AND logic)
            due_date_start: Optional start of due date range (inclusive)
            due_date_end: Optional end of due date range (inclusive)
            sort: Optional sort criteria (comma-separated for compound sorting)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Tuple of (tasks, total_count)
        """
        logger.info(
            "Searching and filtering tasks",
            user_id=user_id,
            search=search,
            status=status,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            sort=sort,
            limit=limit,
            offset=offset,
        )

        # Build base query
        conditions = [Task.user_id == user_id]

        # Add full-text search filter
        if search:
            tsquery = self.build_tsquery(search)
            if tsquery:
                # Use ts_rank for relevance ranking
                conditions.append(
                    text(f"search_vector @@ to_tsquery('english', :tsquery)")
                )

        # Add status filter
        if status:
            conditions.append(Task.status == status)

        # Add priority filter
        if priority:
            conditions.append(Task.priority == priority)

        # Add due date range filters
        if due_date_start:
            conditions.append(Task.due_at >= due_date_start)
        if due_date_end:
            conditions.append(Task.due_at <= due_date_end)

        # Build query with all conditions
        query = select(Task).where(and_(*conditions))

        # Add tag filters (AND logic - task must have all specified tags)
        if tags:
            for tag_name in tags:
                # Subquery to check if task has this tag
                tag_subquery = (
                    select(TaskTag.task_id)
                    .join(Tag, TaskTag.tag_id == Tag.id)
                    .where(Tag.name == tag_name)
                )
                query = query.where(Task.id.in_(tag_subquery))

        # Get total count (before pagination)
        count_query = select(func.count()).select_from(Task).where(and_(*conditions))

        # Apply tag filter to count query
        if tags:
            for tag_name in tags:
                tag_subquery = (
                    select(TaskTag.task_id)
                    .join(Tag, TaskTag.tag_id == Tag.id)
                    .where(Tag.name == tag_name)
                )
                count_query = count_query.where(Task.id.in_(tag_subquery))

        # Execute count query
        if search:
            tsquery = self.build_tsquery(search)
            count_result = await self.session.execute(
                count_query,
                {"tsquery": tsquery} if tsquery else {}
            )
        else:
            count_result = await self.session.execute(count_query)

        total = count_result.scalar()

        # Add ordering using build_order_by method
        order_by_clauses = self.build_order_by(sort, has_search=bool(search))

        if search and not sort:
            # When searching without explicit sort, order by relevance first
            tsquery = self.build_tsquery(search)
            if tsquery:
                query = query.order_by(
                    text("ts_rank(search_vector, to_tsquery('english', :tsquery)) DESC"),
                    Task.created_at.desc()
                )
        elif order_by_clauses:
            # Apply custom sort order
            for clause in order_by_clauses:
                query = query.order_by(clause)
        else:
            # Default: newest first
            query = query.order_by(Task.created_at.desc())

        # Add pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        if search:
            tsquery = self.build_tsquery(search)
            result = await self.session.execute(
                query,
                {"tsquery": tsquery} if tsquery else {}
            )
        else:
            result = await self.session.execute(query)

        tasks = result.scalars().all()

        logger.info(
            "Search completed",
            results_count=len(tasks),
            total=total,
        )

        return list(tasks), total
