import pytest
from backend.app.mcp.tools import (
    mcp_list_projects,
    mcp_get_project_context,
    mcp_create_bug,
    mcp_get_bug_detail,
    mcp_update_bug_status,
    mcp_add_bug_comment,
    mcp_query_bugs,
    mcp_get_project_stats
)

@pytest.mark.asyncio
async def test_mcp_tools_flow():
    # 1. List projects
    projects = await mcp_list_projects()
    assert len(projects) >= 1
    project_id = projects[0]["id"]

    # 2. Get project context
    ctx = await mcp_get_project_context(project_id)
    assert ctx["id"] == project_id
    assert "modules" in ctx
    assert "members" in ctx

    # 3. Create bug via MCP
    bug = await mcp_create_bug(
        project_id=project_id,
        content="[AI发现] 首页数据加载存在内存泄漏风险",
        ver="v2.0.0",
        priority=2,
        status=1
    )
    assert bug["id"] > 0
    bug_id = bug["id"]

    # 4. Get bug detail via MCP
    detail = await mcp_get_bug_detail(bug_id)
    assert detail["id"] == bug_id
    assert "内存泄漏" in detail["content"]

    # 5. Add comment via MCP
    comment = await mcp_add_bug_comment(
        bug_id=bug_id,
        comment="已定位到事件监听器未在 unmount 时移除的问题。"
    )
    assert comment["bug_id"] == bug_id

    # 6. Update bug status via MCP to 4 (fixed)
    updated_bug = await mcp_update_bug_status(
        bug_id=bug_id,
        status=4,
        close_reason="已在 commit abc1234 中修复该泄漏"
    )
    assert updated_bug["status"] == 4
    assert updated_bug["status_code"] == "fixed"

    # 7. Query bugs via MCP
    query_res = await mcp_query_bugs(
        project_id=project_id,
        search="内存泄漏"
    )
    assert query_res["total"] >= 1

    # 8. Get project stats via MCP
    stats = await mcp_get_project_stats(project_id)
    assert stats["total_bugs"] >= 1
