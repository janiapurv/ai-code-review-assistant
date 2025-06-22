#!/usr/bin/env python3
"""
Test client for the AI Code Review Assistant MCP Server.

This script demonstrates how to connect to and use the MCP server.
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any


class MCPClient:
    """Simple MCP client for testing the code review server."""
    
    def __init__(self, server_command: str = "python -m src.main"):
        self.server_command = server_command
        self.process = None
    
    async def start_server(self):
        """Start the MCP server as a subprocess."""
        print("🚀 Starting MCP server...")
        self.process = subprocess.Popen(
            self.server_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ MCP server started")
    
    async def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        # Send request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            return json.loads(response_line)
        return None
    
    async def list_tools(self):
        """List available tools."""
        print("\n🔧 Listing available tools...")
        response = await self.send_request("tools/list", {})
        if response and "result" in response:
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        return response
    
    async def review_code(self, code: str, language: str = "python"):
        """Review code using the MCP server."""
        print(f"\n📝 Reviewing {language} code...")
        response = await self.send_request("tools/call", {
            "name": "review_code",
            "arguments": {
                "code": code,
                "language": language
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"]
            if content and len(content) > 0:
                print("✅ Code review completed!")
                print(content[0]["text"])
            else:
                print("❌ No review content received")
        else:
            print(f"❌ Error: {response}")
        
        return response
    
    async def health_check(self):
        """Check server health."""
        print("\n🏥 Checking server health...")
        response = await self.send_request("tools/call", {
            "name": "health_check",
            "arguments": {}
        })
        
        if response and "result" in response:
            content = response["result"]["content"]
            if content and len(content) > 0:
                print(content[0]["text"])
            else:
                print("❌ No health check response")
        else:
            print(f"❌ Error: {response}")
        
        return response
    
    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            print("\n🛑 Stopping MCP server...")
            self.process.terminate()
            self.process.wait()
            print("✅ MCP server stopped")


async def main():
    """Main test function."""
    print("🤖 AI Code Review Assistant - MCP Client Test")
    print("=" * 50)
    
    client = MCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Wait a moment for server to initialize
        await asyncio.sleep(2)
        
        # Test health check
        await client.health_check()
        
        # List available tools
        await client.list_tools()
        
        # Test code review
        test_code = """
def insecure_function(user_input):
    # This is a security vulnerability
    result = eval(user_input)
    return result

def hardcoded_password():
    password = "secret123"
    return password

def long_function():
    # This function is too long and should be refactored
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    return a + b + c + d + e + f + g + h + i + j
"""
        
        await client.review_code(test_code, "python")
        
        # Test JavaScript review
        js_code = """
function processUserInput(input) {
    eval(input);  // Dangerous!
    console.log("Processing complete");
}

function authenticate(user, password) {
    if (user === "admin" && password === "secret123") {
        return true;
    }
    return false;
}
"""
        
        await client.review_code(js_code, "javascript")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop the server
        await client.stop_server()


if __name__ == "__main__":
    asyncio.run(main()) 