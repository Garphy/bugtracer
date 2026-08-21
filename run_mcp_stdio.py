#!/usr/bin/env python3
"""
BugTracer MCP Server Entry Point (STDIO)
Usage:
    python run_mcp_stdio.py
"""
import sys
import os
import asyncio

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.mcp.server import mcp

if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
