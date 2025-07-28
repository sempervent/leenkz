"""Tags router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from leenkz.api.deps import get_current_active_user, get_db
from leenkz.api.schemas import Tag, TagCreate, TagUpdate
from leenkz.core.database import Tag as TagModel, User

router = APIRouter()


@router.get("/", response_model=List[Tag])
async def get_tags(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[Tag]:
    """Get user's tags."""
    result = await db.execute(
        select(TagModel)
        .where(TagModel.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    tags = result.scalars().all()
    return [Tag.model_validate(tag) for tag in tags]


@router.post("/", response_model=Tag)
async def create_tag(
    tag_data: TagCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Tag:
    """Create a new tag."""
    # Check if tag name already exists for this user
    existing_tag = await db.execute(
        select(TagModel).where(
            TagModel.name == tag_data.name, TagModel.user_id == current_user.id
        )
    )
    if existing_tag.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists",
        )
    
    tag = TagModel(
        name=tag_data.name,
        color=tag_data.color,
        user_id=current_user.id,
    )
    
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return Tag.model_validate(tag)


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    tag_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Tag:
    """Get a specific tag."""
    result = await db.execute(
        select(TagModel).where(
            TagModel.id == tag_id, TagModel.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    
    return Tag.from_orm(tag)


@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Tag:
    """Update a tag."""
    result = await db.execute(
        select(TagModel).where(
            TagModel.id == tag_id, TagModel.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    
    # Check if new name conflicts with existing tag
    if tag_data.name and tag_data.name != tag.name:
        existing_tag = await db.execute(
            select(TagModel).where(
                TagModel.name == tag_data.name, TagModel.user_id == current_user.id
            )
        )
        if existing_tag.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists",
            )
    
    # Update fields
    if tag_data.name is not None:
        tag.name = tag_data.name
    if tag_data.color is not None:
        tag.color = tag_data.color
    
    await db.commit()
    await db.refresh(tag)
    
    return Tag.model_validate(tag)


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a tag."""
    result = await db.execute(
        select(TagModel).where(
            TagModel.id == tag_id, TagModel.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    
    await db.delete(tag)
    await db.commit()
    
    return {"message": "Tag deleted successfully"} 