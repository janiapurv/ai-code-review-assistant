#!/usr/bin/env python3
"""
Simple test script for the MCP server using the official MCP library.
"""

import asyncio
import sys
import traceback
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def test_mcp_server():
    """Test the MCP server with detailed error handling."""
    print("🤖 Testing MCP Server with Official Library")
    print("=" * 50)
    
    try:
        print("🔌 Connecting to MCP server...")
        
        async with stdio_client(StdioServerParameters(
            command="python",
            args=["-m", "src.main"]
        )) as (read, write):
            print("✅ Connected to MCP server")
            
            try:
                async with ClientSession(read, write) as session:
                    print("\n⏳ Waiting for server initialization...")
                    
                    # Give the server time to initialize
                    await asyncio.sleep(2)
                    
                    print("🔧 Listing available tools...")
                    
                    try:
                        print("📤 Sending list_tools request...")
                        tools = await session.list_tools()
                        print(f"📥 Received response from server")
                        print(f"✅ Found {len(tools.tools)} tools:")
                        
                        for tool in tools.tools:
                            print(f"  - {tool.name}: {tool.description}")
                        
                        # Verify we're connected to the correct server
                        print("\n🔍 Verifying server identity...")
                        expected_tools = ["review_code", "review_file", "review_security", "health_check"]
                        server_tools = [tool.name for tool in tools.tools]
                        
                        if all(tool in server_tools for tool in expected_tools):
                            print("✅ Server verification passed - connected to AI Code Review Assistant")
                        else:
                            print("❌ Server verification failed - unexpected tools found")
                            print(f"Expected: {expected_tools}")
                            print(f"Found: {server_tools}")
                        
                        # Test a simple tool call
                        print("\n🧪 Testing health check...")
                        result = await session.call_tool("health_check", {})
                        
                        if result.isError:
                            print(f"❌ Health check failed: {result.content[0].text}")
                        else:
                            health_text = result.content[0].text
                            print(f"✅ Health check passed: {health_text}")
                            
                            # Additional verification
                            if "AI Code Review Assistant" in health_text:
                                print("✅ Server identity confirmed via health check")
                            else:
                                print("⚠️  Server identity unclear from health check")
                            
                    except Exception as e:
                        print(f"❌ Error during tool operations: {e}")
                        print(f"Traceback: {traceback.format_exc()}")
                        
            except Exception as e:
                print(f"❌ Error in client session: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 