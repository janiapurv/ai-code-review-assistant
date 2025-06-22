#!/usr/bin/env python3
"""
AI-Powered Code Review Assistant MCP Server

This server provides intelligent code review capabilities through the Model Context Protocol.
"""

print("🚀 Starting MCP server script...")

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.lowlevel.server import NotificationOptions
from mcp.types import (
    CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
    Tool, TextContent, ImageContent, EmbeddedResource, NotificationParams, ToolsCapability
)
import mcp.types as types
from types import SimpleNamespace

from src.code_reviewer import CodeReviewer
from src.github_integration import GitHubIntegration
from src.models import (
    CodeReviewRequest, CodeReviewResponse, GitHubPullRequestRequest,
    FileReviewRequest, HealthResponse, CodeIssue
)

# Load environment variables from .env file
load_dotenv()

print("📦 All imports loaded successfully!")

# Create the server
server = Server("ai-code-review-assistant")
reviewer = CodeReviewer()
github_integration = GitHubIntegration()

@server.list_tools()
async def list_tools(request: ListToolsRequest) -> ListToolsResult:
    """List available tools."""
    print("🔧 List tools method called!")
    
    tools = [
        Tool(
            name="review_code",
            description="Review a code snippet using AI analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to review"},
                    "language": {"type": "string", "description": "Programming language"},
                    "context": {"type": "string", "description": "Additional context"},
                    "review_focus": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Focus areas (security, performance, etc.)"
                    }
                },
                "required": ["code", "language"]
            }
        ),
        Tool(
            name="review_file",
            description="Review an entire file",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "File content"},
                    "language": {"type": "string", "description": "Programming language"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["file_path", "content"]
            }
        ),
        Tool(
            name="review_pull_request",
            description="Review a GitHub pull request",
            inputSchema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "pull_number": {"type": "integer", "description": "Pull request number"},
                    "review_focus": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Focus areas for review"
                    }
                },
                "required": ["owner", "repo", "pull_number"]
            }
        ),
        Tool(
            name="review_security",
            description="Perform security-focused code review",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to review"},
                    "language": {"type": "string", "description": "Programming language"}
                },
                "required": ["code", "language"]
            }
        ),
        Tool(
            name="review_performance",
            description="Perform performance-focused code review",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to review"},
                    "language": {"type": "string", "description": "Programming language"}
                },
                "required": ["code", "language"]
            }
        ),
        Tool(
            name="health_check",
            description="Check the health of the code review service",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    print(f"🔧 Returning {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    result = ListToolsResult(tools=tools)
    print(f"🔧 ListToolsResult created with {len(result.tools)} tools")
    return result

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    print(f"🔧 Call tool called: {request.name}")
    try:
        if request.name == "review_code":
            return await _handle_review_code(request.arguments)
        elif request.name == "review_file":
            return await _handle_review_file(request.arguments)
        elif request.name == "review_pull_request":
            return await _handle_review_pull_request(request.arguments)
        elif request.name == "review_security":
            return await _handle_review_security(request.arguments)
        elif request.name == "review_performance":
            return await _handle_review_performance(request.arguments)
        elif request.name == "health_check":
            return await _handle_health_check(request.arguments)
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

async def _handle_review_code(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle code review tool call."""
    request = CodeReviewRequest(
        code=arguments["code"],
        language=arguments["language"],
        context=arguments.get("context"),
        review_focus=arguments.get("review_focus")
    )
    
    review = await reviewer.review_code(request)
    
    # Format the response
    response_text = _format_review_response(review)
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=response_text
            )
        ]
    )

async def _handle_review_file(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle file review tool call."""
    request = FileReviewRequest(
        file_path=arguments["file_path"],
        content=arguments["content"],
        language=arguments.get("language"),
        context=arguments.get("context")
    )
    
    review = await reviewer.review_file(
        request.file_path,
        request.content,
        request.language
    )
    
    response_text = _format_review_response(review)
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=response_text
            )
        ]
    )

async def _handle_review_pull_request(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle pull request review tool call."""
    request = GitHubPullRequestRequest(
        owner=arguments["owner"],
        repo=arguments["repo"],
        pull_number=arguments["pull_number"],
        review_focus=arguments.get("review_focus")
    )
    
    result = await github_integration.review_pull_request(request)
    
    if "error" in result:
        response_text = f"Error reviewing pull request: {result['error']}"
    else:
        response_text = _format_pr_review_response(result)
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=response_text
            )
        ]
    )

async def _handle_review_security(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle security review tool call."""
    issues = await reviewer.review_security(
        arguments["code"],
        arguments["language"]
    )
    
    response_text = _format_security_review(issues)
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=response_text
            )
        ]
    )

async def _handle_review_performance(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle performance review tool call."""
    issues = await reviewer.review_performance(
        arguments["code"],
        arguments["language"]
    )
    
    response_text = _format_performance_review(issues)
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=response_text
            )
        ]
    )

async def _handle_health_check(arguments: Dict[str, Any]) -> CallToolResult:
    """Handle health check tool call."""
    health = HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "ai_analyzer": "available",
            "github_integration": "available" if github_integration.token else "not_configured"
        }
    )
    
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=f"AI Code Review Assistant Server\nHealth Check: {health.status}\nVersion: {health.version}\nServices: {health.services}"
            )
        ]
    )

def _format_review_response(review: CodeReviewResponse) -> str:
    """Format a code review response for display."""
    lines = [
        f"# Code Review Results",
        f"",
        f"**Overall Score:** {review.overall_score:.1f}/10",
        f"**Summary:** {review.summary}",
        f""
    ]
    
    if review.complexity_score is not None:
        lines.append(f"**Complexity Score:** {review.complexity_score:.1f}/10")
    if review.maintainability_score is not None:
        lines.append(f"**Maintainability Score:** {review.maintainability_score:.1f}/10")
    if review.security_score is not None:
        lines.append(f"**Security Score:** {review.security_score:.1f}/10")
    if review.performance_score is not None:
        lines.append(f"**Performance Score:** {review.performance_score:.1f}/10")
    
    lines.append("")
    
    if review.issues:
        lines.append("## Issues Found")
        for i, issue in enumerate(review.issues, 1):
            lines.append(f"### {i}. {issue.title}")
            lines.append(f"**Severity:** {issue.severity.value}")
            lines.append(f"**Type:** {issue.type.value}")
            lines.append(f"**Description:** {issue.description}")
            if issue.line_number:
                lines.append(f"**Line:** {issue.line_number}")
            if issue.suggestion:
                lines.append(f"**Suggestion:** {issue.suggestion}")
            lines.append("")
    
    if review.suggestions:
        lines.append("## Suggestions")
        for i, suggestion in enumerate(review.suggestions, 1):
            lines.append(f"### {i}. {suggestion.title}")
            lines.append(f"**Description:** {suggestion.description}")
            lines.append(f"**Reasoning:** {suggestion.reasoning}")
            lines.append(f"**Impact:** {suggestion.impact}")
            if suggestion.code_before and suggestion.code_after:
                lines.append("**Code Change:**")
                lines.append(f"```")
                lines.append(f"// Before:")
                lines.append(suggestion.code_before)
                lines.append(f"// After:")
                lines.append(suggestion.code_after)
                lines.append(f"```")
            lines.append("")
    
    return "\n".join(lines)

def _format_pr_review_response(result: Dict[str, Any]) -> str:
    """Format a pull request review response."""
    pr = result["pull_request"]
    lines = [
        f"# Pull Request Review: #{pr['number']} - {pr['title']}",
        f"",
        f"**Author:** {pr['author']}",
        f"**Status:** {pr['state']}",
        f"**URL:** {pr['url']}",
        f"",
        f"## Summary",
        f"{result['summary']}",
        f"",
        f"**Files Reviewed:** {result['total_files_reviewed']}",
        f"**Total Issues:** {result['total_issues']}",
        f"**Total Suggestions:** {result['total_suggestions']}",
        f"**Overall Score:** {result['overall_score']:.1f}/10",
        f""
    ]
    
    if result["reviews"]:
        lines.append("## File Reviews")
        for file_review in result["reviews"]:
            file = file_review["file"]
            review = file_review["review"]
            lines.append(f"### {file}")
            lines.append(f"**Score:** {review['overall_score']:.1f}/10")
            lines.append(f"**Issues:** {len(review['issues'])}")
            lines.append(f"**Suggestions:** {len(review['suggestions'])}")
            lines.append("")
    
    return "\n".join(lines)

def _format_security_review(issues: List[CodeIssue]) -> str:
    """Format a security review response."""
    lines = [
        f"# Security Review Results",
        f"",
        f"**Issues Found:** {len(issues)}",
        f""
    ]
    
    if not issues:
        lines.append("✅ No security issues found!")
    else:
        for i, issue in enumerate(issues, 1):
            lines.append(f"### {i}. {issue.title}")
            lines.append(f"**Severity:** {issue.severity.value}")
            lines.append(f"**Description:** {issue.description}")
            if issue.suggestion:
                lines.append(f"**Recommendation:** {issue.suggestion}")
            lines.append("")
    
    return "\n".join(lines)

def _format_performance_review(issues: List[CodeIssue]) -> str:
    """Format a performance review response."""
    lines = [
        f"# Performance Review Results",
        f"",
        f"**Issues Found:** {len(issues)}",
        f""
    ]
    
    if not issues:
        lines.append("✅ No performance issues found!")
    else:
        for i, issue in enumerate(issues, 1):
            lines.append(f"### {i}. {issue.title}")
            lines.append(f"**Severity:** {issue.severity.value}")
            lines.append(f"**Description:** {issue.description}")
            if issue.suggestion:
                lines.append(f"**Recommendation:** {issue.suggestion}")
            lines.append("")
    
    return "\n".join(lines)

async def main():
    """Main entry point for the MCP server."""
    print("🔧 Initializing MCP server...")
    
    print("✅ Server created, starting stdio server...")
    
    async with stdio_server() as (read, write):
        print("🔌 Stdio server started, running server...")
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="ai-code-review-assistant",
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