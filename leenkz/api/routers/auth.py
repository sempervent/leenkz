"""Authentication router."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from leenkz.api.deps import get_db
from leenkz.api.schemas import LoginRequest, RegisterRequest, Token, User
from leenkz.core.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from leenkz.core.database import User as UserModel

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """Login endpoint."""
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", response_model=User)
async def register(
    register_data: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Register endpoint."""
    # Check if user already exists
    from leenkz.core.auth import get_user_by_email, get_user_by_username
    
    existing_user = await get_user_by_email(db, register_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    existing_username = await get_user_by_username(db, register_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    hashed_password = get_password_hash(register_data.password)
    user = UserModel(
        email=register_data.email,
        username=register_data.username,
        hashed_password=hashed_password,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return User.model_validate(user) 