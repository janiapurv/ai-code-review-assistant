#!/usr/bin/env python3
"""
Simple client to test the FastMCP server.
"""

import asyncio
from fastmcp import Client

async def test_fastmcp_server():
    """Test the FastMCP server."""
    print("🤖 Testing FastMCP Server")
    print("=" * 40)
    
    try:
        print("🔌 Connecting to FastMCP server...")
        
        # Create client that connects to our server
        client = Client("tcp://127.0.0.1:9000")
        
        print("✅ Connected to FastMCP server")
        
        # List available tools
        print("\n🔧 Listing available tools...")
        tools = await client.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test hello tool
        print("\n👋 Testing hello tool...")
        result = await client.hello(name="FastMCP")
        print(f"✅ Hello tool result: {result}")
        
        # Test hello tool with default name
        print("\n👋 Testing hello tool with default name...")
        result = await client.hello()
        print(f"✅ Hello tool result: {result}")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health_result = await client.health_check()
        print(f"✅ Health check result: {health_result}")
        
        # Test add numbers
        print("\n🔢 Testing add numbers...")
        sum_result = await client.add_numbers(a=5, b=3)
        print(f"✅ Add numbers result: {sum_result}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastmcp_server()) 