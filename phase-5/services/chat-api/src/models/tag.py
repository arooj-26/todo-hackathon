"""Tag models for task categorization."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class TagBase(SQLModel):
    """Base tag fields."""

    name: str = Field(
        min_length=1,
        max_length=50,
        regex=r"^[a-z0-9-]+$",
        description="Tag name (lowercase, alphanumeric, hyphens)",
    )


class Tag(TagBase, table=True):
    """Tag entity with usage tracking."""

    __tablename__ = "tags"

    id: int = Field(default=None, primary_key=True)
    usage_count: int = Field(default=0, description="Number of tasks with this tag")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskTag(SQLModel, table=True):
    """Many-to-many relationship between tasks and tags."""

    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TagCreate(TagBase):
    """Tag creation schema."""

    pass


class TagResponse(TagBase):
    """Tag response schema."""

    id: int
    usage_count: int


class TagListResponse(SQLModel):
    """Tag list response."""

    tags: list[TagResponse]
