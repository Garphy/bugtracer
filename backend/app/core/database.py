import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Create Async Engine
# If SQLite, check_same_thread=False
connect_args = {}
if "sqlite" in settings.effective_database_url:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    settings.effective_database_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to yield database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initializes the database schema and seeds initial data if necessary."""
    from backend.app.models.user import User
    from backend.app.models.project import Project, ProjectMember
    from backend.app.models.module import Module
    from backend.app.models.bug import Bug
    from backend.app.models.attachment import Attachment
    from backend.app.models.comment import Comment
    from backend.app.models.activity import Activity
    from backend.app.core.security import hash_password, generate_api_key
    from sqlalchemy import select

    # 1. Create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed initial users, default project and members
    async with AsyncSessionLocal() as session:
        # Check / create default admin
        stmt = select(User).where(User.username == settings.INITIAL_ADMIN_USERNAME)
        result = await session.execute(stmt)
        admin = result.scalars().first()
        if not admin:
            admin = User(
                username=settings.INITIAL_ADMIN_USERNAME,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                fullname=settings.INITIAL_ADMIN_FULLNAME,
                role="admin",
                api_key=generate_api_key(),
                is_active=True
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            logger.info(f"Initialized default admin user: {admin.username}")

        # Check / create default AI agent user
        stmt_ai = select(User).where(User.username == "ai_agent")
        result_ai = await session.execute(stmt_ai)
        ai_user = result_ai.scalars().first()
        if not ai_user:
            ai_user = User(
                username="ai_agent",
                password_hash=hash_password("ai_agent_internal_secret"),
                fullname="AI 助手",
                role="coder",
                api_key=generate_api_key("bt_ai_"),
                is_active=True
            )
            session.add(ai_user)
            await session.commit()
            await session.refresh(ai_user)
            logger.info("Initialized default AI agent user: ai_agent")

        # Check / create default project
        stmt_proj = select(Project).where(Project.id == 1)
        result_proj = await session.execute(stmt_proj)
        project = result_proj.scalars().first()
        if not project:
            stmt_any = select(Project)
            result_any = await session.execute(stmt_any)
            if not result_any.scalars().first():
                project = Project(
                    id=1,
                    name="公共模块",
                    description="系统默认公共项目",
                    is_active=True
                )
                session.add(project)
                await session.flush()

                # Add default module
                module = Module(
                    project_id=project.id,
                    name="通用问题",
                    sort_order=1
                )
                session.add(module)

                # Bind admin and AI agent as members
                if admin:
                    session.add(ProjectMember(project_id=project.id, user_id=admin.id, role_in_project="lead"))
                if ai_user:
                    session.add(ProjectMember(project_id=project.id, user_id=ai_user.id, role_in_project="member"))

                await session.commit()
                logger.info("Initialized default project: 公共模块 with members")
