"""Shares router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from leenkz.api.deps import get_current_active_user, get_db
from leenkz.api.schemas import Share, ShareCreate
from leenkz.core.database import Share as ShareModel, Link, User

router = APIRouter()


@router.get("/", response_model=List[Share])
async def get_shares(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[Share]:
    """Get shares for current user."""
    result = await db.execute(
        select(ShareModel)
        .where(ShareModel.shared_with == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    shares = result.scalars().all()
    
    # Load link for each share
    for share in shares:
        link_result = await db.execute(
            select(Link).where(Link.id == share.link_id)
        )
        share.link = link_result.scalar_one()
    
    return [Share.model_validate(share) for share in shares]


@router.post("/", response_model=Share)
async def create_share(
    share_data: ShareCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Share:
    """Share a link with another user."""
    # Verify link belongs to current user
    link_result = await db.execute(
        select(Link).where(
            Link.id == share_data.link_id, Link.user_id == current_user.id
        )
    )
    link = link_result.scalar_one_or_none()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    
    # Verify target user exists
    target_user_result = await db.execute(
        select(User).where(User.id == share_data.shared_with)
    )
    target_user = target_user_result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found"
        )
    
    # Check if already shared
    existing_share = await db.execute(
        select(ShareModel).where(
            ShareModel.link_id == share_data.link_id,
            ShareModel.shared_with == share_data.shared_with,
        )
    )
    if existing_share.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link already shared with this user",
        )
    
    share = ShareModel(
        link_id=share_data.link_id,
        shared_by=current_user.id,
        shared_with=share_data.shared_with,
        message=share_data.message,
    )
    
    db.add(share)
    await db.commit()
    await db.refresh(share)
    
    # Load link
    share.link = link
    
    return Share.model_validate(share)


@router.delete("/{share_id}")
async def delete_share(
    share_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a share."""
    result = await db.execute(
        select(ShareModel).where(
            ShareModel.id == share_id,
            ShareModel.shared_by == current_user.id,
        )
    )
    share = result.scalar_one_or_none()
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Share not found"
        )
    
    await db.delete(share)
    await db.commit()
    
    return {"message": "Share deleted successfully"} 