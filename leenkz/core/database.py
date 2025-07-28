"""Database configuration and models."""

import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel, select

from leenkz.core.config import settings


# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def run_migrations() -> None:
    """Run database migrations."""
    from alembic import command
    from alembic.config import Config
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


# Models
class User(SQLModel, table=True):
    """User model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username."""
    async with AsyncSessionLocal() as session:
        result = await session.exec(select(User).where(User.username == username))
        return result.first()


class Link(SQLModel, table=True):
    """Link model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True)
    title: str
    description: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Tag(SQLModel, table=True):
    """Tag model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    color: Optional[str] = None
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LinkTag(SQLModel, table=True):
    """Link-Tag association model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    link_id: int = Field(foreign_key="link.id")
    tag_id: int = Field(foreign_key="tag.id")


class Share(SQLModel, table=True):
    """Share model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    link_id: int = Field(foreign_key="link.id")
    shared_by: int = Field(foreign_key="user.id")
    shared_with: int = Field(foreign_key="user.id")
    message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LinkSnapshot(SQLModel, table=True):
    """Link snapshot model."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    link_id: int = Field(foreign_key="link.id")
    created_by: int = Field(foreign_key="user.id")
    
    # Content metadata
    mime_type: str
    size_original: int
    size_compressed: int
    compression: str = "none"  # gzip, zstd, none
    checksum: str
    content_hash: str = Field(index=True)  # SHA-256 hash for deduplication
    
    # HTTP metadata
    encoding: Optional[str] = None
    last_modified: Optional[datetime] = None
    etag: Optional[str] = None
    
    # Content storage (as bytes)
    content: bytes
    
    created_at: datetime = Field(default_factory=datetime.utcnow) 