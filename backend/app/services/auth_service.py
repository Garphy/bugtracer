from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserUpdate, PasswordChange
from backend.app.core.security import verify_password, hash_password, create_access_token, generate_api_key

class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalars().first()
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def get_all_users(db: AsyncSession, active_only: bool = True) -> List[User]:
        stmt = select(User)
        if active_only:
            stmt = stmt.where(User.is_active == True)
        stmt = stmt.order_by(User.role, User.id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        # Check duplicate username
        stmt = select(User).where(User.username == user_in.username)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

        user = User(
            username=user_in.username,
            fullname=user_in.fullname or user_in.username,
            role=user_in.role or "coder",
            password_hash=hash_password(user_in.password or "123456"),
            api_key=generate_api_key(),
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate) -> User:
        user = await AuthService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        if user_in.username and user_in.username != user.username:
            stmt = select(User).where(User.username == user_in.username)
            result = await db.execute(stmt)
            if result.scalars().first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该用户名已存在")
            user.username = user_in.username

        if user_in.fullname is not None:
            user.fullname = user_in.fullname
        if user_in.role is not None:
            user.role = user_in.role
        if user_in.is_active is not None:
            user.is_active = user_in.is_active
        if user_in.password:
            user.password_hash = hash_password(user_in.password)

        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def change_password(db: AsyncSession, user: User, data: PasswordChange):
        if not verify_password(data.old_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
        user.password_hash = hash_password(data.new_password)
        await db.commit()

    @staticmethod
    async def regenerate_api_key(db: AsyncSession, user: User) -> str:
        user.api_key = generate_api_key()
        await db.commit()
        await db.refresh(user)
        return user.api_key
