from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.core.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.bug import (
    BugCreate, BugUpdate, BugStatusUpdate, BugListResponse, BugDetailResponse, BugListItem
)
from backend.app.schemas.comment import CommentCreate, CommentResponse
from backend.app.services.bug_service import BugService

router = APIRouter(prefix="/bugs", tags=["Bugs"])

@router.get("", response_model=BugListResponse)
async def list_bugs(
    request: Request,
    project_id: int = Query(..., description="项目ID"),
    module_id: Optional[int] = Query(None, description="模块ID"),
    status: Optional[str] = Query(None, description="状态列表，支持逗号分隔如 1,2,3 或多次传递"),
    search: Optional[str] = Query(None, description="搜索关键词或语法"),
    mode: str = Query("admin", description="模式: admin 或 coder"),
    order_by: str = Query("id", description="排序字段"),
    order_desc: bool = Query(True, description="是否倒序"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(30, ge=1, le=200, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    parsed_statuses: Optional[List[int]] = None
    if "status" in request.query_params or "status[]" in request.query_params:
        raw_list = request.query_params.getlist("status") + request.query_params.getlist("status[]")
        status_values = []
        for item in raw_list:
            if item.strip():
                for sub in item.split(","):
                    sub_str = sub.strip()
                    if sub_str.isdigit():
                        status_values.append(int(sub_str))
        parsed_statuses = status_values
    elif status is not None:
        status_values = []
        for sub in status.split(","):
            sub_str = sub.strip()
            if sub_str.isdigit():
                status_values.append(int(sub_str))
        parsed_statuses = status_values

    return await BugService.list_bugs(
        db=db,
        project_id=project_id,
        module_id=module_id,
        statuses=parsed_statuses,
        search=search,
        mode=mode,
        current_user=current_user,
        order_by=order_by,
        order_desc=order_desc,
        page=page,
        page_size=page_size
    )

@router.get("/{bug_id}", response_model=BugDetailResponse)
async def get_bug_detail(
    bug_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await BugService.get_bug(db, bug_id)

@router.post("", response_model=BugDetailResponse)
async def create_bug(
    bug_in: BugCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bug = await BugService.create_bug(db, bug_in, current_user)
    return await BugService.get_bug(db, bug.id)

@router.put("/{bug_id}", response_model=BugDetailResponse)
async def update_bug(
    bug_id: int,
    bug_in: BugUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bug = await BugService.update_bug(db, bug_id, bug_in, current_user)
    return await BugService.get_bug(db, bug.id)

@router.put("/{bug_id}/status", response_model=BugDetailResponse)
async def update_bug_status(
    bug_id: int,
    status_update: BugStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    bug = await BugService.update_status(db, bug_id, status_update, current_user)
    return await BugService.get_bug(db, bug.id)

@router.post("/{bug_id}/comments", response_model=CommentResponse)
async def add_bug_comment(
    bug_id: int,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = await BugService.add_comment(db, bug_id, comment_in.content, current_user)
    return {
        "id": comment.id,
        "bug_id": comment.bug_id,
        "user_id": comment.user_id,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "fullname": current_user.fullname,
            "role": current_user.role
        },
        "content": comment.content,
        "created_at": comment.created_at
    }
