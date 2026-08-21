#!/usr/bin/env python3
"""
BugTracer MCP Server Entry Point (STDIO)
Usage:
    python run_mcp_stdio.py
"""
import sys
import os
import asyncio

# Ensure project root is in sys.path and set as current working directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.chdir(project_root)

from backend.app.mcp.server import mcp

if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
