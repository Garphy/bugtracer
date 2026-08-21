from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.models.project import Project, ProjectMember
from backend.app.models.module import Module
from backend.app.models.bug import Bug
from backend.app.models.user import User
from backend.app.schemas.project import ProjectCreate, ProjectUpdate
from backend.app.schemas.module import ModuleCreate, ModuleUpdate

ACTIVE_STATUS_IDS = [1, 2, 3]  # new, key, part_fixed

class ProjectService:
    @staticmethod
    async def get_projects(db: AsyncSession, current_user_id: Optional[int] = None) -> List[Dict]:
        stmt = select(Project).where(Project.is_active == True).order_by(Project.id)
        result = await db.execute(stmt)
        projects = list(result.scalars().all())

        # Count active bugs per project
        active_counts_stmt = select(
            Bug.project_id,
            func.count(Bug.id).label("count")
        ).where(Bug.status.in_(ACTIVE_STATUS_IDS)).group_by(Bug.project_id)
        active_res = await db.execute(active_counts_stmt)
        active_map = {row.project_id: row.count for row in active_res.all()}

        # Count my active bugs per project
        my_map = {}
        if current_user_id:
            my_stmt = select(
                Bug.project_id,
                func.count(Bug.id).label("count")
            ).where(
                Bug.status.in_(ACTIVE_STATUS_IDS),
                Bug.assignee_id == current_user_id
            ).group_by(Bug.project_id)
            my_res = await db.execute(my_stmt)
            my_map = {row.project_id: row.count for row in my_res.all()}

        out = []
        for p in projects:
            p_dict = {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "default_version": p.default_version,
                "is_active": p.is_active,
                "created_at": p.created_at,
                "active_bugs_count": active_map.get(p.id, 0),
                "my_bugs_count": my_map.get(p.id, 0)
            }
            out.append(p_dict)
        return out

    @staticmethod
    async def get_project_detail(db: AsyncSession, project_id: int) -> Dict:
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.modules),
                selectinload(Project.members).selectinload(ProjectMember.user)
            )
        )
        result = await db.execute(stmt)
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        # Bug count per module
        mod_counts_stmt = select(
            Bug.module_id,
            func.count(Bug.id).label("count")
        ).where(Bug.project_id == project_id).group_by(Bug.module_id)
        mod_res = await db.execute(mod_counts_stmt)
        mod_map = {row.module_id: row.count for row in mod_res.all()}

        modules_out = []
        for m in sorted(project.modules, key=lambda x: x.sort_order):
            modules_out.append({
                "id": m.id,
                "project_id": m.project_id,
                "name": m.name,
                "sort_order": m.sort_order,
                "bug_count": mod_map.get(m.id, 0)
            })

        members_out = []
        for pm in project.members:
            if pm.user and pm.user.is_active:
                members_out.append({
                    "id": pm.user.id,
                    "username": pm.user.username,
                    "fullname": pm.user.fullname,
                    "role": pm.user.role
                })

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "default_version": project.default_version,
            "is_active": project.is_active,
            "created_at": project.created_at,
            "modules": modules_out,
            "members": members_out
        }

    @staticmethod
    async def create_project(db: AsyncSession, project_in: ProjectCreate) -> Project:
        project = Project(
            name=project_in.name,
            description=project_in.description,
            default_version=project_in.default_version,
            is_active=project_in.is_active
        )
        db.add(project)
        await db.flush()

        # Add initial modules if provided
        if project_in.modules:
            for idx, mod_name in enumerate(project_in.modules):
                if mod_name.strip():
                    m = Module(project_id=project.id, name=mod_name.strip(), sort_order=idx + 1)
                    db.add(m)
        else:
            # Default module
            db.add(Module(project_id=project.id, name="默认模块", sort_order=1))

        # Add members
        if project_in.member_ids:
            for uid in project_in.member_ids:
                pm = ProjectMember(project_id=project.id, user_id=uid)
                db.add(pm)

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def update_project(db: AsyncSession, project_id: int, project_in: ProjectUpdate) -> Project:
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project_in.name is not None:
            project.name = project_in.name
        if project_in.description is not None:
            project.description = project_in.description
        if project_in.default_version is not None:
            project.default_version = project_in.default_version
        if project_in.is_active is not None:
            project.is_active = project_in.is_active

        # Sync members if provided
        if project_in.member_ids is not None:
            # Clear old
            del_stmt = delete(ProjectMember).where(ProjectMember.project_id == project_id)
            await db.execute(del_stmt)
            for uid in project_in.member_ids:
                db.add(ProjectMember(project_id=project_id, user_id=uid))

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def add_module(db: AsyncSession, module_in: ModuleCreate) -> Module:
        m = Module(
            project_id=module_in.project_id,
            name=module_in.name,
            sort_order=module_in.sort_order
        )
        db.add(m)
        await db.commit()
        await db.refresh(m)
        return m

    @staticmethod
    async def update_module(db: AsyncSession, module_id: int, module_in: ModuleUpdate) -> Module:
        stmt = select(Module).where(Module.id == module_id)
        result = await db.execute(stmt)
        m = result.scalars().first()
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模块分类不存在")
        if module_in.name is not None:
            m.name = module_in.name
        if module_in.sort_order is not None:
            m.sort_order = module_in.sort_order
        await db.commit()
        await db.refresh(m)
        return m

    @staticmethod
    async def delete_module(db: AsyncSession, module_id: int):
        stmt = select(Module).where(Module.id == module_id)
        result = await db.execute(stmt)
        m = result.scalars().first()
        if not m:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="模块分类不存在")
        # Disassociate bugs in this module
        from sqlalchemy import update
        await db.execute(update(Bug).where(Bug.module_id == module_id).values(module_id=None))
        await db.delete(m)
        await db.commit()
