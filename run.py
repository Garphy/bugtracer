#!/usr/bin/env python3
"""
BugTracer Server Launcher
Usage:
    python run.py
"""
import uvicorn
from backend.app.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION} on http://{settings.HOST}:{settings.PORT}")
    print(f"📡 API Documentation: http://127.0.0.1:{settings.PORT}/docs")
    print(f"🤖 MCP Endpoint: http://127.0.0.1:{settings.PORT}/mcp")
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
