#!/usr/bin/env python3

import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import ServerCapabilities
from handlers import ToolHandler
from tools import get_tools

# Create MCP server
server = Server("telegram-messenger")
handler = ToolHandler()

@server.list_tools()
async def list_tools():
    """List available tools."""
    return get_tools()

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]):
    """Handle tool calls."""
    return await handler.handle_tool_call(name, arguments)

async def main():
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="telegram-messenger",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
