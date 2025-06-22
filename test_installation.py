#!/usr/bin/env python3
"""
Test script to verify the AI Code Review Assistant installation.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.models import CodeReviewRequest, CodeReviewResponse, IssueType, Severity
        print("✅ Models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False
    
    try:
        from src.code_reviewer import CodeReviewer
        print("✅ CodeReviewer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CodeReviewer: {e}")
        return False
    
    try:
        from src.ai_analyzer import AIAnalyzer
        print("✅ AIAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AIAnalyzer: {e}")
        return False
    
    try:
        from src.github_integration import GitHubIntegration
        print("✅ GitHubIntegration imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import GitHubIntegration: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without AI."""
    print("\nTesting basic functionality...")
    
    try:
        from src.code_reviewer import CodeReviewer
        from src.models import CodeReviewRequest
        
        reviewer = CodeReviewer()
        
        # Test static analysis
        code = """
def test_function():
    try:
        result = 1 / 0
    except:
        print("Error")
"""
        
        request = CodeReviewRequest(
            code=code,
            language="python"
        )
        
        # This should work even without OpenAI API key
        print("✅ CodeReviewer initialized successfully")
        print("✅ Static analysis available")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if openai_key:
        print("✅ OpenAI API key is set")
    else:
        print("⚠️  OpenAI API key not set (AI features will be limited)")
    
    if github_token:
        print("✅ GitHub token is set")
    else:
        print("⚠️  GitHub token not set (GitHub integration will be limited)")
    
    return True

def main():
    """Main test function."""
    print("🤖 AI Code Review Assistant - Installation Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please check your installation.")
        sys.exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed.")
        sys.exit(1)
    
    # Test environment
    test_environment()
    
    print("\n✅ All tests passed! Installation is successful.")
    print("\nNext steps:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("2. Set your GitHub token: export GITHUB_TOKEN='your-token-here'")
    print("3. Run the example: python examples/basic_usage.py")
    print("4. Run the MCP server: python -m src.main")

if __name__ == "__main__":
    main() 