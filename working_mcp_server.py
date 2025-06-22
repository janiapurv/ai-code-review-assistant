#!/usr/bin/env python3
"""
Working MCP server example.
"""

import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    Tool, TextContent
)

# Create the server
server = Server("working-test-server")

@server.list_tools()
async def list_tools(request: ListToolsRequest) -> ListToolsResult:
    """List available tools."""
    print("🔧 List tools called")
    tools = [
        Tool(
            name="hello",
            description="Say hello",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name to greet"}
                }
            }
        ),
        Tool(
            name="health_check",
            description="Check server health",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    return ListToolsResult(tools=tools)

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    print(f"🔧 Call tool called: {request.name}")
    try:
        if request.name == "hello":
            name = request.arguments.get("name", "World")
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Hello, {name}!"
                    )
                ]
            )
        elif request.name == "health_check":
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Server is healthy!"
                    )
                ]
            )
        else:
            raise ValueError(f"Unknown tool: {request.name}")
            
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ],
            isError=True
        )

async def main():
    """Main entry point for the working MCP server."""
    print("🚀 Starting working MCP server...")
    
    print("✅ Server created, starting stdio server...")
    
    async with stdio_server() as (read, write):
        print("🔌 Stdio server started, running server...")
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="working-test-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(tools_changed=True),
                    experimental_capabilities=None,
                ),
            ),
        )

    print("🏁 Server finished running.")

if __name__ == "__main__":
    print("🎯 Main block reached, starting asyncio...")
    asyncio.run(main())
    print("✅ Script completed.") 