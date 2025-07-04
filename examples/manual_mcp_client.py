#!/usr/bin/env python3
"""
Manual MCP client that handles initialization properly.
"""

import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters

async def test_manual_client():
    """Test with manual initialization handling."""
    print("🤖 Manual MCP Client Test")
    print("=" * 40)
    
    try:
        print("🔌 Connecting to server...")
        
        async with stdio_client(StdioServerParameters(
            command="python",
            args=["working_mcp_server.py"]
        )) as (read, write):
            print("✅ Connected to server")
            
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "manual-test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("📤 Sending initialization request...")
            await write.send(json.dumps(init_request) + "\n")
            
            # Wait for initialization response
            print("⏳ Waiting for initialization response...")
            await asyncio.sleep(2)
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            print("📤 Sending initialized notification...")
            await write.send(json.dumps(initialized_notification) + "\n")
            
            await asyncio.sleep(1)
            
            # Now try to list tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            print("📤 Sending list tools request...")
            await write.send(json.dumps(list_tools_request) + "\n")
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Try to read response
            try:
                response = await read.receive()
                print(f"📥 Received response: {response}")
            except Exception as e:
                print(f"❌ Error reading response: {e}")
            
            print("🏁 Test completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_manual_client()) 