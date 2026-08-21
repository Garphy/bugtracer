from typing import Optional, List, Dict, Any
from mcp.server import MCPServer
from backend.app.core.config import settings
from backend.app.mcp.tools import (
    mcp_list_projects,
    mcp_get_project_context,
    mcp_query_bugs,
    mcp_get_bug_detail,
    mcp_create_bug,
    mcp_update_bug_status,
    mcp_add_bug_comment,
    mcp_get_project_stats
)

mcp = MCPServer(settings.MCP_SERVER_NAME)

@mcp.tool()
async def list_projects() -> List[Dict[str, Any]]:
    """获取 BugTracer 中的所有有效项目列表及活动缺陷总览。"""
    return await mcp_list_projects()

@mcp.tool()
async def get_project_context(project_id: int) -> Dict[str, Any]:
    """获取指定项目的模块/分类清单、成员列表和项目上下文信息。"""
    return await mcp_get_project_context(project_id)

@mcp.tool()
async def query_bugs(
    project_id: int,
    status_filter: Optional[List[int]] = None,
    module_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 30
) -> Dict[str, Any]:
    """
    在指定项目中检索缺陷列表。
    search 参数支持 BugTracer 快捷语法：
    - '123' 或 '123,456': 按 Bug ID 查找
    - '(1)': 查找创建人用户 ID 为 1 的缺陷
    - '{2}': 查找分派给用户 ID 为 2 的缺陷
    - '!{2}': 查找非用户 ID 为 2 的缺陷
    - '{2026-01-01~2026-02-01}': 查找变更时间在此区间的缺陷
    - 普通文本: 模糊匹配缺陷描述、标题或版本
    """
    return await mcp_query_bugs(
        project_id=project_id,
        status_filter=status_filter,
        module_id=module_id,
        search=search,
        page=page,
        page_size=page_size
    )

@mcp.tool()
async def get_bug_detail(bug_id: int) -> Dict[str, Any]:
    """根据 Bug ID 获取缺陷的完整描述、版本、附件清单、讨论评论以及修改审计历史。"""
    return await mcp_get_bug_detail(bug_id)

@mcp.tool()
async def create_bug(
    project_id: int,
    content: str,
    module_id: Optional[int] = None,
    ver: str = "",
    assignee_id: int = 0,
    priority: int = 0,
    status: int = 1
) -> Dict[str, Any]:
    """
    提交/创建新的缺陷或开发任务。
    status 枚举: 0:关闭, 1:新建(默认), 2:重要, 3:部分处理, 4:已解决, 5:不处理, 6:待办, 7:备忘。
    priority 枚举: 0:普通, 1:高优, 2:严重。
    """
    return await mcp_create_bug(
        project_id=project_id,
        content=content,
        module_id=module_id,
        ver=ver,
        assignee_id=assignee_id,
        priority=priority,
        status=status
    )

@mcp.tool()
async def update_bug_status(
    bug_id: int,
    status: int,
    close_reason: str = ""
) -> Dict[str, Any]:
    """
    修改指定缺陷的状态（如将 Bug 标记为已解决 fixed=4 或 关闭 closed=0）。
    状态代码: 0=关闭, 1=新建, 2=重要, 3=部分处理, 4=已解决, 5=不处理, 6=待办, 7=备忘。
    """
    return await mcp_update_bug_status(bug_id=bug_id, status=status, close_reason=close_reason)

@mcp.tool()
async def add_bug_comment(bug_id: int, comment: str) -> Dict[str, Any]:
    """为指定缺陷追加技术分析方案、排查结论、复现过程或修复记录评论。"""
    return await mcp_add_bug_comment(bug_id=bug_id, comment=comment)

@mcp.tool()
async def get_project_stats(project_id: int) -> Dict[str, Any]:
    """获取项目的统计分析报表与质量分布概览（按人员负荷、按模块分布、近期趋势）。"""
    return await mcp_get_project_stats(project_id)
