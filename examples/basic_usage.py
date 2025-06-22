#!/usr/bin/env python3
"""
Basic usage example for the AI Code Review Assistant.

This example demonstrates how to use the code reviewer directly without MCP.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.code_reviewer import CodeReviewer
from src.models import CodeReviewRequest

# Load environment variables from .env file
load_dotenv()


async def main():
    """Main example function."""
    print("🤖 AI Code Review Assistant - Basic Usage Example")
    print("=" * 50)
    
    # Initialize the code reviewer
    reviewer = CodeReviewer()
    
    # Example 1: Review a simple Python function
    print("\n📝 Example 1: Reviewing a Python function")
    print("-" * 40)
    
    python_code = """
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
"""
    
    request = CodeReviewRequest(
        code=python_code,
        language="python",
        context="This function calculates the average of a list of numbers"
    )
    
    review = await reviewer.review_code(request)
    
    print(f"Overall Score: {review.overall_score:.1f}/10")
    print(f"Summary: {review.summary}")
    print(f"Issues Found: {len(review.issues)}")
    print(f"Suggestions: {len(review.suggestions)}")
    
    if review.issues:
        print("\nIssues:")
        for i, issue in enumerate(review.issues, 1):
            print(f"  {i}. {issue.title} ({issue.severity.value})")
            print(f"     {issue.description}")
    
    # Example 2: Review JavaScript code with security focus
    print("\n🔒 Example 2: Security-focused JavaScript review")
    print("-" * 40)
    
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
    
    request = CodeReviewRequest(
        code=js_code,
        language="javascript",
        review_focus=["security"]
    )
    
    review = await reviewer.review_code(request)
    
    print(f"Security Score: {review.security_score:.1f}/10" if review.security_score else "Security Score: Not available")
    print(f"Overall Score: {review.overall_score:.1f}/10")
    
    security_issues = [issue for issue in review.issues if issue.type.value == "security"]
    if security_issues:
        print("\nSecurity Issues:")
        for i, issue in enumerate(security_issues, 1):
            print(f"  {i}. {issue.title} ({issue.severity.value})")
            print(f"     {issue.description}")
            if issue.suggestion:
                print(f"     Suggestion: {issue.suggestion}")
    
    # Example 3: Review TypeScript code
    print("\n📘 Example 3: TypeScript code review")
    print("-" * 40)
    
    ts_code = """
interface User {
    id: number;
    name: string;
    data: any;  // Using any type
}

class UserService {
    private users: User[] = [];
    
    // TODO: implement pagination
    async getUsers(): Promise<User[]> {
        return this.users;
    }
    
    async createUser(userData: any): Promise<User> {
        const user: User = {
            id: Math.random(),
            name: userData.name,
            data: userData
        };
        this.users.push(user);
        return user;
    }
}
"""
    
    request = CodeReviewRequest(
        code=ts_code,
        language="typescript",
        review_focus=["maintainability", "style"]
    )
    
    review = await reviewer.review_code(request)
    
    print(f"Maintainability Score: {review.maintainability_score:.1f}/10" if review.maintainability_score else "Maintainability Score: Not available")
    print(f"Overall Score: {review.overall_score:.1f}/10")
    
    if review.suggestions:
        print("\nSuggestions:")
        for i, suggestion in enumerate(review.suggestions, 1):
            print(f"  {i}. {suggestion.title}")
            print(f"     {suggestion.description}")
            print(f"     Impact: {suggestion.impact}")
    
    # Example 4: File review
    print("\n📁 Example 4: File review")
    print("-" * 40)
    
    file_content = """
import os
import json

def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config

def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def process_files():
    config = load_config()
    for file in os.listdir('.'):
        if file.endswith('.txt'):
            with open(file, 'r') as f:
                content = f.read()
            save_data({'content': content}, f'{file}.json')
"""
    
    review = await reviewer.review_file("data_processor.py", file_content)
    
    print(f"File: data_processor.py")
    print(f"Overall Score: {review.overall_score:.1f}/10")
    print(f"Summary: {review.summary}")
    
    # Example 5: Specialized security review
    print("\n🛡️ Example 5: Specialized security review")
    print("-" * 40)
    
    security_code = """
import subprocess
import os

def execute_command(command):
    return subprocess.run(command, shell=True, capture_output=True)

def read_file(path):
    return open(path, 'r').read()

def validate_input(user_input):
    if '..' in user_input:
        return False
    return True
"""
    
    security_issues = await reviewer.review_security(security_code, "python")
    
    print(f"Security Issues Found: {len(security_issues)}")
    for i, issue in enumerate(security_issues, 1):
        print(f"  {i}. {issue.title} ({issue.severity.value})")
        print(f"     {issue.description}")
    
    print("\n✅ Examples completed!")


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features may not work.")
        print("   Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    
    asyncio.run(main()) 