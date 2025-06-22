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
            args=["working_mcp_server.py"]
        )) as (read, write):
            print("✅ Connected to working MCP server")
            
            try:
                async with ClientSession(read, write) as session:
                    print("\n⏳ Waiting for server initialization...")
                    await asyncio.sleep(3)  # Longer wait for initialization
                    
                    print("🔧 Listing available tools...")
                    
                    try:
                        tools = await session.list_tools()
                        print(f"✅ Found {len(tools.tools)} tools:")
                        
                        for tool in tools.tools:
                            print(f"  - {tool.name}: {tool.description}")
                        
                        # Test hello tool
                        print("\n👋 Testing hello tool...")
                        result = await session.call_tool("hello", {"name": "MCP"})
                        
                        if result.isError:
                            print(f"❌ Hello tool failed: {result.content[0].text}")
                        else:
                            print(f"✅ Hello tool result: {result.content[0].text}")
                        
                        # Test health check
                        print("\n🏥 Testing health check...")
                        health_result = await session.call_tool("health_check", {})
                        
                        if health_result.isError:
                            print(f"❌ Health check failed: {health_result.content[0].text}")
                        else:
                            print(f"✅ Health check result: {health_result.content[0].text}")
                            
                    except Exception as e:
                        print(f"❌ Error during tool operations: {e}")
                        import traceback
                        traceback.print_exc()
                        
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