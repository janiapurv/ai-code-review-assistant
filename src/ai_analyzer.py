import os
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from src.models import (
    CodeIssue, CodeSuggestion, CodeReviewResponse, 
    IssueType, Severity, CodeReviewRequest
)

# Load environment variables from .env file
load_dotenv()

class AIAnalyzer:
    """AI-powered code analyzer using OpenAI models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
    
    async def analyze_code(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Analyze code using AI and return comprehensive review."""
        
        # Prepare the analysis prompt
        prompt = self._build_analysis_prompt(request)
        
        try:
            print(f"🤖 Attempting AI analysis with model: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            print(f"✅ AI response received successfully")
            
            # Parse the AI response
            ai_response = json.loads(response.choices[0].message.content)
            return self._parse_ai_response(ai_response, request)
            
        except Exception as e:
            print(f"❌ AI analysis failed: {str(e)}")
            # Fallback to basic analysis if AI fails
            return await self._fallback_analysis(request)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI model."""
        return """You are an expert code reviewer. Analyze code and provide feedback in JSON format:
{
    "issues": [{"type": "bug|security|performance|style", "severity": "low|medium|high|critical", "title": "...", "description": "...", "line_number": null, "suggestion": "..."}],
    "suggestions": [{"title": "...", "description": "...", "code_before": "...", "code_after": "...", "reasoning": "...", "impact": "low|medium|high"}],
    "summary": "...",
    "overall_score": 0.0-10.0,
    "complexity_score": 0.0-10.0,
    "maintainability_score": 0.0-10.0,
    "security_score": 0.0-10.0,
    "performance_score": 0.0-10.0
}"""
    
    def _build_analysis_prompt(self, request: CodeReviewRequest) -> str:
        """Build the analysis prompt for the AI model."""
        prompt = f"Analyze this {request.language} code:\n\n```{request.language}\n{request.code}\n```\n\n"
        
        if request.context:
            prompt += f"Context: {request.context}\n\n"
        
        if request.file_path:
            prompt += f"File: {request.file_path}\n\n"
        
        if request.review_focus:
            prompt += f"Focus: {', '.join(request.review_focus)}\n\n"
        
        prompt += "Provide comprehensive review in JSON format."
        
        return prompt
    
    def _parse_ai_response(self, ai_response: Dict[str, Any], request: CodeReviewRequest) -> CodeReviewResponse:
        """Parse the AI response into structured data."""
        try:
            issues = []
            for issue_data in ai_response.get("issues", []):
                try:
                    issue = CodeIssue(
                        type=IssueType(issue_data["type"]),
                        severity=Severity(issue_data["severity"]),
                        title=issue_data["title"],
                        description=issue_data["description"],
                        line_number=issue_data.get("line_number"),
                        column_number=issue_data.get("column_number"),
                        code_snippet=issue_data.get("code_snippet"),
                        suggestion=issue_data.get("suggestion"),
                        confidence=0.8
                    )
                    issues.append(issue)
                except Exception as e:
                    # Skip malformed issues
                    continue
            
            suggestions = []
            for suggestion_data in ai_response.get("suggestions", []):
                try:
                    suggestion = CodeSuggestion(
                        title=suggestion_data["title"],
                        description=suggestion_data["description"],
                        code_before=suggestion_data.get("code_before"),
                        code_after=suggestion_data.get("code_after"),
                        reasoning=suggestion_data["reasoning"],
                        impact=suggestion_data.get("impact", "medium")
                    )
                    suggestions.append(suggestion)
                except Exception as e:
                    # Skip malformed suggestions
                    continue
            
            return CodeReviewResponse(
                issues=issues,
                suggestions=suggestions,
                summary=ai_response.get("summary", "Code review completed"),
                overall_score=float(ai_response.get("overall_score", 7.0)),
                complexity_score=ai_response.get("complexity_score"),
                maintainability_score=ai_response.get("maintainability_score"),
                security_score=ai_response.get("security_score"),
                performance_score=ai_response.get("performance_score"),
                metadata={
                    "model_used": self.model,
                    "language": request.language,
                    "file_path": request.file_path
                }
            )
            
        except Exception as e:
            # Fallback response if parsing fails
            return CodeReviewResponse(
                issues=[],
                suggestions=[],
                summary=f"Error parsing AI response: {str(e)}",
                overall_score=5.0,
                metadata={"error": str(e)}
            )
    
    async def _fallback_analysis(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Fallback analysis when AI is unavailable."""
        # Basic static analysis
        issues = []
        suggestions = []
        
        # Check for common issues
        code = request.code.lower()
        
        # Security checks
        if "password" in code and "=" in code:
            issues.append(CodeIssue(
                type=IssueType.SECURITY,
                severity=Severity.HIGH,
                title="Hardcoded Password",
                description="Password appears to be hardcoded in the code",
                suggestion="Use environment variables or secure configuration management",
                confidence=0.7
            ))
        
        # Performance checks
        if "for" in code and "for" in code and code.count("for") > 2:
            suggestions.append(CodeSuggestion(
                title="Consider List Comprehension",
                description="Multiple nested loops detected",
                reasoning="List comprehensions are often more efficient and readable",
                impact="medium"
            ))
        
        return CodeReviewResponse(
            issues=issues,
            suggestions=suggestions,
            summary="Basic analysis completed (AI unavailable)",
            overall_score=6.0,
            metadata={"fallback": True}
        )
    
    async def analyze_security(self, code: str, language: str) -> List[CodeIssue]:
        """Specialized security analysis."""
        security_prompt = f"""Analyze this {language} code for security vulnerabilities:

```{language}
{code}
```

Focus specifically on:
- SQL injection
- Cross-site scripting (XSS)
- Command injection
- Authentication bypass
- Authorization issues
- Input validation
- Secure coding practices

Return only security-related issues in JSON format."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a security expert. Focus only on security vulnerabilities."},
                    {"role": "user", "content": security_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            return [CodeIssue(**issue) for issue in ai_response.get("issues", [])]
            
        except Exception as e:
            return []
    
    async def analyze_performance(self, code: str, language: str) -> List[CodeIssue]:
        """Specialized performance analysis."""
        performance_prompt = f"""Analyze this {language} code for performance issues:

```{language}
{code}
```

Focus specifically on:
- Algorithm efficiency
- Memory usage
- Database query optimization
- I/O operations
- Caching opportunities
- Resource management

Return only performance-related issues in JSON format."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a performance optimization expert. Focus only on performance issues."},
                    {"role": "user", "content": performance_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            return [CodeIssue(**issue) for issue in ai_response.get("issues", [])]
            
        except Exception as e:
            return [] 