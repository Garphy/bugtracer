import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.core.database import init_db

@pytest.mark.asyncio
async def test_full_api_flow():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Health check
        res = await ac.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        # 2. Login as admin
        login_res = await ac.post("/api/auth/login", json={
            "username": "admin",
            "password": "123456"
        })
        assert login_res.status_code == 200
        data = login_res.json()
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get me
        me_res = await ac.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["username"] == "admin"

        # 4. Get projects list
        prj_res = await ac.get("/api/projects", headers=headers)
        assert prj_res.status_code == 200
        projects = prj_res.json()
        assert len(projects) >= 1
        project_id = projects[0]["id"]

        # 5. Create a new bug
        bug_res = await ac.post("/api/bugs", headers=headers, json={
            "project_id": project_id,
            "content": "测试缺陷：[b]支付弹窗无法关闭[/b]，见图1",
            "ver": "v2.0.0",
            "priority": 1,
            "status": 1
        })
        assert bug_res.status_code == 200
        bug_data = bug_res.json()
        bug_id = bug_data["id"]
        assert bug_data["status"] == 1
        assert bug_data["status_code"] == "new"

        # 6. Change bug status to fixed (4)
        status_res = await ac.put(f"/api/bugs/{bug_id}/status", headers=headers, json={
            "status": 4,
            "close_reason": "已修改代码并测试通过"
        })
        assert status_res.status_code == 200
        assert status_res.json()["status"] == 4
        assert status_res.json()["status_code"] == "fixed"

        # 7. Add comment to bug
        comment_res = await ac.post(f"/api/bugs/{bug_id}/comments", headers=headers, json={
            "content": "回归测试通过，可以发版"
        })
        assert comment_res.status_code == 200
        assert comment_res.json()["content"] == "回归测试通过，可以发版"

        # 8. Query bug detail
        detail_res = await ac.get(f"/api/bugs/{bug_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert len(detail["comments"]) == 1
        assert len(detail["activities"]) >= 2

        # 9. Get project stats
        stats_res = await ac.get(f"/api/reports/stats/{project_id}", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_bugs"] >= 1

        # 10. Search bug
        search_res = await ac.get(f"/api/bugs?project_id={project_id}&search={bug_id}", headers=headers)
        assert search_res.status_code == 200
        assert len(search_res.json()["items"]) == 1
