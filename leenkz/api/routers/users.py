"""Users router."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from leenkz.api.deps import get_current_superuser, get_db
from leenkz.api.schemas import User, UserCreate, UserUpdate
from leenkz.core.auth import get_password_hash
from leenkz.core.database import User as UserModel

router = APIRouter()


@router.get("/", response_model=List[User])
async def get_users(
    current_user: Annotated[UserModel, Depends(get_current_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[User]:
    """Get all users (admin only)."""
    result = await db.execute(
        select(UserModel).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return [User.model_validate(user) for user in users]


@router.post("/", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[UserModel, Depends(get_current_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Create a new user (admin only)."""
    # Check if user already exists
    from leenkz.core.auth import get_user_by_email, get_user_by_username
    
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = UserModel(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return User.model_validate(user)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: Annotated[UserModel, Depends(get_current_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get a specific user (admin only)."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    return User.from_orm(user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: Annotated[UserModel, Depends(get_current_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Update a user (admin only)."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Update fields
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)
    
    await db.commit()
    await db.refresh(user)
    
    return User.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: Annotated[UserModel, Depends(get_current_superuser)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Delete a user (admin only)."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"} 