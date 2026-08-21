from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.core.security import decode_access_token
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Query(None)
) -> Optional[User]:
    """
    Extracts current user from:
    1. Bearer Token (Authorization: Bearer <token>)
    2. X-API-Key Header
    3. api_key query param (convenient for SSE/MCP)
    """
    # 1. Try Bearer Token
    if token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            stmt = select(User).where(User.id == int(user_id))
            result = await db.execute(stmt)
            user = result.scalars().first()
            if user and user.is_active:
                return user

    # 2. Try API Key
    effective_api_key = x_api_key or api_key
    if effective_api_key:
        stmt = select(User).where(User.api_key == effective_api_key)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if user and user.is_active:
            return user

    return None

async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录或提供有效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可执行此操作"
        )
    return current_user
