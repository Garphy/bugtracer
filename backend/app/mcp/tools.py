from typing import Optional, List, Dict, Any
from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User
from backend.app.models.bug import STATUS_MAP, STATUS_NAMES
from backend.app.schemas.bug import BugCreate, BugStatusUpdate
from backend.app.services.project_service import ProjectService
from backend.app.services.bug_service import BugService
from backend.app.services.report_service import ReportService

# Helper to get default AI agent user
async def get_or_create_ai_user(db) -> User:
    stmt = select(User).where(User.username == "ai_agent")
    result = await db.execute(stmt)
    user = result.scalars().first()
    if not user:
        from backend.app.core.security import hash_password, generate_api_key
        user = User(
            username="ai_agent",
            password_hash=hash_password("ai_agent_internal_secret"),
            fullname="AI 助手",
            role="coder",
            api_key=generate_api_key("bt_ai_"),
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def mcp_list_projects() -> List[Dict[str, Any]]:
    """获取所有项目列表及活动缺陷概览"""
    await init_db()
    async with AsyncSessionLocal() as db:
        projects = await ProjectService.get_projects(db)
        return projects

async def mcp_get_project_context(project_id: int) -> Dict[str, Any]:
    """获取项目的模块列表、成员信息及上下文"""
    await init_db()
    async with AsyncSessionLocal() as db:
        detail = await ProjectService.get_project_detail(db, project_id)
        return detail

async def mcp_query_bugs(
    project_id: int,
    status_filter: Optional[List[int]] = None,
    module_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 30
) -> Dict[str, Any]:
    """
    在指定项目中检索缺陷列表。
    支持复杂搜索语法：如 '(1)' 查提出者、'{2}' 查指派人、'{2026-01-01~2026-02-01}' 查时间段、'102' 查ID、或关键词模糊匹配。
    """
    await init_db()
    async with AsyncSessionLocal() as db:
        res = await BugService.list_bugs(
            db=db,
            project_id=project_id,
            module_id=module_id,
            statuses=status_filter,
            search=search,
            mode="admin",
            page=page,
            page_size=page_size
        )
        return res

async def mcp_get_bug_detail(bug_id: int) -> Dict[str, Any]:
    """获取指定缺陷的详细描述、版本、附件、讨论评论及修改审计历史"""
    await init_db()
    async with AsyncSessionLocal() as db:
        detail = await BugService.get_bug(db, bug_id)
        return detail

async def mcp_create_bug(
    project_id: int,
    content: str,
    module_id: Optional[int] = None,
    ver: str = "",
    assignee_id: int = 0,
    priority: int = 0,
    status: int = 1
) -> Dict[str, Any]:
    """提交/录入新的缺陷或需求任务"""
    await init_db()
    async with AsyncSessionLocal() as db:
        ai_user = await get_or_create_ai_user(db)
        bug_in = BugCreate(
            project_id=project_id,
            module_id=module_id,
            content=content,
            ver=ver,
            assignee_id=assignee_id,
            priority=priority,
            status=status
        )
        bug = await BugService.create_bug(db, bug_in, ai_user)
        return await BugService.get_bug(db, bug.id)

async def mcp_update_bug_status(
    bug_id: int,
    status: int,
    close_reason: str = ""
) -> Dict[str, Any]:
    """
    更新缺陷状态。
    状态对应关系：
    0: closed (已关闭)
    1: new (新增)
    2: key (重要)
    3: part_fixed (部分处理)
    4: fixed (已解决)
    5: wont_fix (不处理)
    6: todo (待办)
    7: idea (备忘)
    """
    await init_db()
    async with AsyncSessionLocal() as db:
        ai_user = await get_or_create_ai_user(db)
        status_update = BugStatusUpdate(status=status, close_reason=close_reason)
        bug = await BugService.update_status(db, bug_id, status_update, ai_user)
        return await BugService.get_bug(db, bug.id)

async def mcp_add_bug_comment(bug_id: int, comment: str) -> Dict[str, Any]:
    """为指定缺陷添加技术方案分析、跟进说明或修复日志评论"""
    await init_db()
    async with AsyncSessionLocal() as db:
        ai_user = await get_or_create_ai_user(db)
        c = await BugService.add_comment(db, bug_id, comment, ai_user)
        return {
            "id": c.id,
            "bug_id": c.bug_id,
            "author": ai_user.fullname,
            "content": c.content,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }

async def mcp_get_project_stats(project_id: int) -> Dict[str, Any]:
    """获取项目的统计分析与质量分布概览"""
    await init_db()
    async with AsyncSessionLocal() as db:
        stats = await ReportService.get_project_stats(db, project_id)
        return stats
