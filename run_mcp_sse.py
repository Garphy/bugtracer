#!/usr/bin/env python3
"""
BugTracer Standalone MCP SSE Server Launcher
Usage:
    python run_mcp_sse.py [--port 5003] [--host 0.0.0.0]
"""
import sys
import os
import argparse
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.mcp.server import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=f"{settings.PROJECT_NAME} MCP SSE Server",
    version=settings.VERSION,
    description="BugTracer Dedicated MCP Server (Server-Sent Events)",
    lifespan=lifespan
)

# Mount MCP SSE app at root or /mcp
app.mount("/mcp", mcp.sse_app())
app.mount("/", mcp.sse_app())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BugTracer Standalone MCP SSE Server")
    parser.add_argument("--host", type=str, default=settings.HOST, help="Host to bind to")
    parser.add_argument("--port", type=int, default=5003, help="Port to listen on (default: 5003)")
    args = parser.parse_args()

    print(f"🚀 Starting BugTracer Standalone MCP SSE Server on http://{args.host}:{args.port}")
    print(f"📡 MCP SSE Endpoint: http://127.0.0.1:{args.port}/sse (or /mcp/sse)")
    uvicorn.run(app, host=args.host, port=args.port, reload=False)
