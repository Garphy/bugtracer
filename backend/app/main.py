import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.projects import router as projects_router
from backend.app.api.bugs import router as bugs_router
from backend.app.api.upload import router as upload_router
from backend.app.api.reports import router as reports_router
from backend.app.mcp.server import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="现代化轻量级缺陷跟踪系统，支持全快捷键操作、SQLite/MySQL 双数据库及 AI Agent MCP 深度集成。",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(bugs_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)

# Mount MCP SSE Service if enabled
if settings.MCP_ENABLED:
    try:
        app.mount("/mcp", mcp.sse_app())
    except Exception as e:
        print(f"Warning: Failed to mount MCP SSE app: {e}")

@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Static files / Single port SPA hosting
static_dir = os.path.join(os.path.dirname(__file__), "static")
frontend_dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

effective_static_dir = None
if os.path.exists(static_dir) and os.path.exists(os.path.join(static_dir, "index.html")):
    effective_static_dir = static_dir
elif os.path.exists(frontend_dist_dir) and os.path.exists(os.path.join(frontend_dist_dir, "index.html")):
    effective_static_dir = frontend_dist_dir

if effective_static_dir:
    app.mount("/assets", StaticFiles(directory=os.path.join(effective_static_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept /api or /mcp
        if full_path.startswith("api") or full_path.startswith("mcp"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
            
        file_path = os.path.join(effective_static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(effective_static_dir, "index.html"))
