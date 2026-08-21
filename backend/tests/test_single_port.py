import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_single_port_spa_serving():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Test index.html served at root
        res_root = await ac.get("/")
        assert res_root.status_code == 200
        assert "BugTracer" in res_root.text

        # 2. Test SPA fallback for sub routes
        res_spa = await ac.get("/report")
        assert res_spa.status_code == 200
        assert "BugTracer" in res_spa.text

        # 3. Test API health
        res_api = await ac.get("/api/health")
        assert res_api.status_code == 200
        assert res_api.json()["status"] == "ok"
