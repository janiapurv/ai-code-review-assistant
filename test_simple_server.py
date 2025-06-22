#!/usr/bin/env python3
"""
Minimal MCP server for testing.
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

class SimpleMCPServer:
    def __init__(self):
        self.server = Server("simple-test-server")
        
        # Register handlers using decorators
        self.server.list_tools_handler = self.list_tools
        self.server.call_tool_handler = self.call_tool
    
    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
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
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
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
    """Main entry point for the simple MCP server."""
    print("🚀 Starting simple MCP server...")
    
    # Create and run the server
    server = SimpleMCPServer()
    
    print("✅ Server created, starting stdio server...")
    
    async with stdio_server() as (read, write):
        print("🔌 Stdio server started, running server...")
        await server.server.run(
            read,
            write,
            InitializationOptions(
                server_name="simple-test-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
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