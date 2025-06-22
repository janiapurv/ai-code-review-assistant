#!/usr/bin/env python3
"""
Minimal MCP test to debug initialization issues.
"""

import asyncio
import json
from mcp.client.stdio import stdio_client, StdioServerParameters

async def test_minimal():
    """Minimal test to check MCP protocol."""
    print("🔍 Minimal MCP Test")
    print("=" * 30)
    
    try:
        print("🔌 Connecting...")
        
        async with stdio_client(StdioServerParameters(
            command="python",
            args=["-m", "src.main"]
        )) as (read, write):
            print("✅ Connected")
            
            # Send initialization request manually
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
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("📤 Sending initialization request...")
            await write.send(json.dumps(init_request) + "\n")
            
            # Wait for response
            await asyncio.sleep(1)
            
            # Try to read response
            try:
                response = await read.receive()
                print(f"📥 Received: {response}")
            except Exception as e:
                print(f"❌ Error reading response: {e}")
            
            print("🏁 Test completed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal()) 