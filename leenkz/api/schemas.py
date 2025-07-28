"""API schemas for leenkz."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl
from leenkz.models import S3Url, StorageUrl, CloudStorageUrl
from sqlmodel import SQLModel




# Base schemas
class UserBase(BaseModel):
    """Base user schema."""
    email: str
    username: str


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LinkBase(BaseModel):
    """Base link schema."""
    url: HttpUrl
    title: str
    description: Optional[str] = None


class S3LinkBase(BaseModel):
    """Base S3 link schema."""
    url: S3Url
    title: str
    description: Optional[str] = None


class LinkCreate(LinkBase):
    """Link creation schema."""
    tag_ids: Optional[List[int]] = []


class LinkUpdate(BaseModel):
    """Link update schema."""
    url: Optional[HttpUrl] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class Link(LinkBase):
    """Link response schema."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List["Tag"] = []

    model_config = {"from_attributes": True}


class TagBase(BaseModel):
    """Base tag schema."""
    name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    """Tag creation schema."""
    pass


class TagUpdate(BaseModel):
    """Tag update schema."""
    name: Optional[str] = None
    color: Optional[str] = None


class Tag(TagBase):
    """Tag response schema."""
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ShareBase(BaseModel):
    """Base share schema."""
    link_id: int
    shared_with: int
    message: Optional[str] = None


class ShareCreate(ShareBase):
    """Share creation schema."""
    pass


class Share(ShareBase):
    """Share response schema."""
    id: int
    shared_by: int
    created_at: datetime
    link: Link

    model_config = {"from_attributes": True}


# Auth schemas
class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Register request schema."""
    email: str
    username: str
    password: str


class StorageLinkBase(BaseModel):
    """Base schema for cloud storage links."""
    url: StorageUrl
    title: str
    description: Optional[str] = None
    service_name: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate service name if not provided
        if not self.service_name:
            self.service_name = self.url.get_service_name()


class CloudStorageLinkBase(BaseModel):
    """Base schema for enterprise cloud storage links."""
    url: CloudStorageUrl
    title: str
    description: Optional[str] = None
    service_name: Optional[str] = None
    is_enterprise: Optional[bool] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate service name and enterprise flag if not provided
        if not self.service_name:
            self.service_name = self.url.get_service_name()
        if self.is_enterprise is None:
            self.is_enterprise = self.url.is_enterprise_service()


# Snapshot schemas
class SnapshotCreate(BaseModel):
    """Snapshot creation schema."""
    compression: str = "gzip"  # gzip, zstd, none
    force: bool = False  # Force creation even if duplicate exists


class Snapshot(SQLModel):
    """Snapshot response schema."""
    id: int
    link_id: int
    created_by: int
    mime_type: str
    size_original: int
    size_compressed: int
    compression: str
    checksum: str
    content_hash: str
    encoding: Optional[str] = None
    last_modified: Optional[datetime] = None
    etag: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


# Update forward references
Link.model_rebuild()
Tag.model_rebuild()
Share.model_rebuild() 