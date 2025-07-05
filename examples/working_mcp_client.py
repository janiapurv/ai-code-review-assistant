#!/usr/bin/env python3
"""
Working client to test the working MCP server.
"""

import asyncio
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_working_server():
    """Test the working MCP server."""
    print("🤖 Testing Working MCP Server")
    print("=" * 40)
    
    try:
        print("🔌 Connecting to working MCP server...")
        
        async with stdio_client(StdioServerParameters(
            command="python",
            args=["-m", "src.main"]
        )) as (read, write):
            print("✅ Connected to working MCP server")
            
            try:
                async with ClientSession(read, write) as session:
                    # Hand-shake
                    init = await session.initialize()
                    print(f"🟢 Connected to {init.serverInfo.name} {init.serverInfo.version}")

                    # List tools
                    tools = await session.list_tools()
                    print("Available tools:", [t.name for t in tools.tools])

                    # Call a tool
                    test_code = """
def example_function():
    x = 10
    return x * 2
"""
                    hello = await session.call_tool("review_code", {
                        "code": test_code,
                        "language": "python"
                    })
                    print("review_code() ⇒", hello.content[0].text)
                        
            except Exception as e:
                print(f"❌ Error in client session: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_working_server())