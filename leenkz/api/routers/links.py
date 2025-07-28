"""Links router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from leenkz.api.deps import get_current_active_user, get_db
from leenkz.api.schemas import Link, LinkCreate, LinkUpdate
from leenkz.core.database import Link as LinkModel, LinkTag, Tag, User

router = APIRouter()


@router.get("/", response_model=List[Link])
async def get_links(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[Link]:
    """Get user's links."""
    result = await db.execute(
        select(LinkModel)
        .where(LinkModel.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    links = result.scalars().all()
    
    # Load tags for each link
    for link in links:
        tag_result = await db.execute(
            select(Tag)
            .join(LinkTag, Tag.id == LinkTag.tag_id)
            .where(LinkTag.link_id == link.id)
        )
        link.tags = tag_result.scalars().all()
    
    return [Link.model_validate(link) for link in links]


@router.post("/", response_model=Link)
async def create_link(
    link_data: LinkCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Link:
    """Create a new link."""
    link = LinkModel(
        url=str(link_data.url),
        title=link_data.title,
        description=link_data.description,
        user_id=current_user.id,
    )
    
    db.add(link)
    await db.commit()
    await db.refresh(link)
    
    # Add tags if provided
    if link_data.tag_ids:
        for tag_id in link_data.tag_ids:
            # Verify tag belongs to user
            tag_result = await db.execute(
                select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
            )
            tag = tag_result.scalar_one_or_none()
            if tag:
                link_tag = LinkTag(link_id=link.id, tag_id=tag_id)
                db.add(link_tag)
        
        await db.commit()
        await db.refresh(link)
    
    return Link.model_validate(link)


@router.get("/{link_id}", response_model=Link)
async def get_link(
    link_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Link:
    """Get a specific link."""
    result = await db.execute(
        select(LinkModel).where(
            LinkModel.id == link_id, LinkModel.user_id == current_user.id
        )
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    
    # Load tags
    tag_result = await db.execute(
        select(Tag)
        .join(LinkTag, Tag.id == LinkTag.tag_id)
        .where(LinkTag.link_id == link.id)
    )
    link.tags = tag_result.scalars().all()
    
    return Link.model_validate(link)


@router.put("/{link_id}", response_model=Link)
async def update_link(
    link_id: int,
    link_data: LinkUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Link:
    """Update a link."""
    result = await db.execute(
        select(LinkModel).where(
            LinkModel.id == link_id, LinkModel.user_id == current_user.id
        )
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    
    # Update fields
    if link_data.url is not None:
        link.url = str(link_data.url)
    if link_data.title is not None:
        link.title = link_data.title
    if link_data.description is not None:
        link.description = link_data.description
    
    await db.commit()
    await db.refresh(link)
    
    # Update tags if provided
    if link_data.tag_ids is not None:
        # Remove existing tags
        await db.execute(
            select(LinkTag).where(LinkTag.link_id == link_id)
        )
        
        # Add new tags
        for tag_id in link_data.tag_ids:
            tag_result = await db.execute(
                select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
            )
            tag = tag_result.scalar_one_or_none()
            if tag:
                link_tag = LinkTag(link_id=link.id, tag_id=tag_id)
                db.add(link_tag)
        
        await db.commit()
        await db.refresh(link)
    
    # Load tags
    tag_result = await db.execute(
        select(Tag)
        .join(LinkTag, Tag.id == LinkTag.tag_id)
        .where(LinkTag.link_id == link.id)
    )
    link.tags = tag_result.scalars().all()
    
    return Link.model_validate(link)


@router.delete("/{link_id}")
async def delete_link(
    link_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a link."""
    result = await db.execute(
        select(LinkModel).where(
            LinkModel.id == link_id, LinkModel.user_id == current_user.id
        )
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    
    await db.delete(link)
    await db.commit()
    
    return {"message": "Link deleted successfully"} 