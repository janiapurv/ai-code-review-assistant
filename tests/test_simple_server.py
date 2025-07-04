#!/usr/bin/env python3
"""
Simple MCP server using FastMCP library.
"""

from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Optional

# Create FastMCP instance
app = FastMCP("simple-test-server")

# Define input models for tools
class HelloInput(BaseModel):
    name: Optional[str] = "World"

class HealthCheckInput(BaseModel):
    pass

@app.tool()
async def hello(input: HelloInput) -> str:
    """Say hello to someone."""
    print(f"🔧 Hello tool called with name: {input.name}")
    return f"Hello, {input.name}!"

@app.tool()
async def health_check(input: HealthCheckInput) -> str:
    """Check server health."""
    print("🔧 Health check tool called")
    return "Server is healthy!"

@app.tool()
async def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"🔧 Add numbers tool called: {a} + {b}")
    return a + b

if __name__ == "__main__":
    print("🚀 Starting FastMCP server on TCP 127.0.0.1:9000 ...")
    app.run("tcp://127.0.0.1:9000") 