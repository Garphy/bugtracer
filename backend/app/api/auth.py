from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_user, get_current_admin
from backend.app.core.security import create_access_token
from backend.app.models.user import User
from backend.app.schemas.user import (
    UserLogin, Token, UserResponse, UserSimple, UserCreate, UserUpdate, PasswordChange
)
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate_user(db, data.username, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await AuthService.change_password(db, current_user, data)
    return {"message": "密码修改成功"}

@router.post("/regenerate-api-key")
async def regenerate_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_key = await AuthService.regenerate_api_key(db, current_user)
    return {"api_key": new_key}

@router.get("/users", response_model=List[UserSimple])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = await AuthService.get_all_users(db, active_only=True)
    return users

@router.get("/users/all", response_model=List[UserResponse])
async def list_all_users_admin(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    users = await AuthService.get_all_users(db, active_only=False)
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = await AuthService.create_user(db, user_in)
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    user = await AuthService.update_user(db, user_id, user_in)
    return user
