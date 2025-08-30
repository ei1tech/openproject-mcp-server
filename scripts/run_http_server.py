#!/usr/bin/env python3
"""
Run the OpenProject MCP Server in HTTP mode

This script starts the FastMCP server for OpenProject integration in HTTP mode.
"""
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

if __name__ == "__main__":
    try:
        from mcp_server import app
        from config import settings
        # Run the FastMCP app in HTTP mode
        print(f"Starting OpenProject MCP Server in HTTP mode on {settings.mcp_host}:{settings.mcp_port}...")
        app.run(transport="sse", host=settings.mcp_host, port=settings.mcp_port)
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running server: {e}")
        sys.exit(1)
