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

        # 3. Create a coder user
        import time
        coder_username = f"coder_{int(time.time()*1000)}"
        create_user_res = await ac.post("/api/auth/users", headers=headers, json={
            "username": coder_username,
            "fullname": "开发小王",
            "role": "coder",
            "password": "password123"
        })
        assert create_user_res.status_code == 200

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

        # 6. Login as coder and test permissions
        coder_login = await ac.post("/api/auth/login", json={
            "username": coder_username,
            "password": "password123"
        })
        coder_token = coder_login.json()["access_token"]
        coder_headers = {"Authorization": f"Bearer {coder_token}"}

        # Coder attempts to set status to 0 (closed) -> Expect 403 Forbidden
        coder_close_res = await ac.put(f"/api/bugs/{bug_id}/status", headers=coder_headers, json={
            "status": 0
        })
        assert coder_close_res.status_code == 403

        # Coder sets status to 4 (fixed) -> Expect 200 OK
        coder_fix_res = await ac.put(f"/api/bugs/{bug_id}/status", headers=coder_headers, json={
            "status": 4,
            "close_reason": "已修改代码并测试通过"
        })
        assert coder_fix_res.status_code == 200
        assert coder_fix_res.json()["status"] == 4
        assert coder_fix_res.json()["status_code"] == "fixed"

        # 7. Admin sets status to 0 (closed) -> Expect 200 OK
        admin_close_res = await ac.put(f"/api/bugs/{bug_id}/status", headers=headers, json={
            "status": 0,
            "close_reason": "验收关闭"
        })
        assert admin_close_res.status_code == 200
        assert admin_close_res.json()["status"] == 0

        # 8. Add comment to bug
        comment_res = await ac.post(f"/api/bugs/{bug_id}/comments", headers=headers, json={
            "content": "回归测试通过，可以发版"
        })
        assert comment_res.status_code == 200
        assert comment_res.json()["content"] == "回归测试通过，可以发版"

        # 9. Query bug detail
        detail_res = await ac.get(f"/api/bugs/{bug_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert len(detail["comments"]) == 1
        assert len(detail["activities"]) >= 3

        # 10. Get project stats
        stats_res = await ac.get(f"/api/reports/stats/{project_id}", headers=headers)
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_bugs"] >= 1

        # 11. Search bug
        search_res = await ac.get(f"/api/bugs?project_id={project_id}&search={bug_id}", headers=headers)
        assert search_res.status_code == 200
        assert len(search_res.json()["items"]) == 1
