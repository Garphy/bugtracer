from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_user, get_current_admin
from backend.app.models.user import User
from backend.app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetail
)
from backend.app.schemas.module import (
    ModuleCreate, ModuleUpdate, ModuleResponse
)
from backend.app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProjectService.get_projects(db, current_user.id)

@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project_detail(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ProjectService.get_project_detail(db, project_id)

@router.post("", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    project = await ProjectService.create_project(db, project_in)
    return await ProjectService.get_project_detail(db, project.id)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    project = await ProjectService.update_project(db, project_id, project_in)
    return await ProjectService.get_project_detail(db, project.id)

@router.post("/{project_id}/modules", response_model=ModuleResponse)
async def add_module(
    project_id: int,
    module_in: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    module_in.project_id = project_id
    return await ProjectService.add_module(db, module_in)

@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_in: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    return await ProjectService.update_module(db, module_id, module_in)

@router.delete("/modules/{module_id}")
async def delete_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    await ProjectService.delete_module(db, module_id)
    return {"message": "模块分类已删除"}
