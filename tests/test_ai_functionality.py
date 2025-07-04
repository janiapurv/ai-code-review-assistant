#!/usr/bin/env python3
"""
Test script to verify AI functionality of the code review assistant.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.code_reviewer import CodeReviewer
from src.models import CodeReviewRequest

# Load environment variables from .env file
load_dotenv()

async def test_ai_review():
    """Test AI-powered code review."""
    print("🤖 Testing AI Code Review Functionality")
    print("=" * 50)
    
    # Check if OpenAI API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment variables")
        print("   Please set OPENAI_API_KEY in your .env file")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:10]}...")
    
    # Initialize the code reviewer
    reviewer = CodeReviewer()
    
    # Test code with obvious issues
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
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
    p = 16
    q = 17
    r = 18
    s = 19
    t = 20
    u = 21
    v = 22
    w = 23
    x = 24
    y = 25
    z = 26
    aa = 27
    bb = 28
    cc = 29
    dd = 30
    ee = 31
    ff = 32
    gg = 33
    hh = 34
    ii = 35
    jj = 36
    kk = 37
    ll = 38
    mm = 39
    nn = 40
    oo = 41
    pp = 42
    qq = 43
    rr = 44
    ss = 45
    tt = 46
    uu = 47
    vv = 48
    ww = 49
    xx = 50
    return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u + v + w + x + y + z + aa + bb + cc + dd + ee + ff + gg + hh + ii + jj + kk + ll + mm + nn + oo + pp + qq + rr + ss + tt + uu + vv + ww + xx
"""
    
    print("\n📝 Testing AI Code Review...")
    print("Code to review:")
    print(test_code)
    
    request = CodeReviewRequest(
        code=test_code,
        language="python",
        context="This code contains security vulnerabilities and maintainability issues"
    )
    
    try:
        review = await reviewer.review_code(request)
        
        print(f"\n✅ AI Review Completed!")
        print(f"Overall Score: {review.overall_score:.1f}/10")
        print(f"Summary: {review.summary}")
        print(f"Issues Found: {len(review.issues)}")
        print(f"Suggestions: {len(review.suggestions)}")
        
        if review.issues:
            print("\n🔍 Issues Found:")
            for i, issue in enumerate(review.issues, 1):
                print(f"  {i}. {issue.title} ({issue.severity.value})")
                print(f"     Type: {issue.type.value}")
                print(f"     Description: {issue.description}")
                if issue.suggestion:
                    print(f"     Suggestion: {issue.suggestion}")
                print()
        
        if review.suggestions:
            print("\n💡 Suggestions:")
            for i, suggestion in enumerate(review.suggestions, 1):
                print(f"  {i}. {suggestion.title}")
                print(f"     Description: {suggestion.description}")
                print(f"     Impact: {suggestion.impact}")
                print()
        
        # Check if AI was actually used
        if "AI unavailable" in review.summary:
            print("⚠️  Warning: AI analysis was not used, only static analysis was performed")
        else:
            print("✅ AI analysis was successfully used")
            
    except Exception as e:
        print(f"❌ Error during AI review: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_review()) 