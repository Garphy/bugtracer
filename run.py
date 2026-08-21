#!/usr/bin/env python3
"""
BugTracer Server Launcher
Usage:
    python run.py
"""
import sys
import os
import uvicorn

# Ensure project root is in sys.path and set as current working directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

from backend.app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION} on http://{settings.HOST}:{settings.PORT}")
    print(f"📡 Web Application: http://127.0.0.1:{settings.PORT}")
    print(f"📚 API Documentation: http://127.0.0.1:{settings.PORT}/docs")
    print(f"🤖 MCP SSE Endpoint: http://127.0.0.1:{settings.PORT}/mcp")
    print(f"🔑 Initial Admin: {settings.INITIAL_ADMIN_USERNAME} / {settings.INITIAL_ADMIN_PASSWORD}")
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
