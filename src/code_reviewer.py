import os
import ast
import re
from typing import List, Optional, Dict, Any
from pathlib import Path
from src.models import (
    CodeReviewRequest, CodeReviewResponse, CodeIssue, CodeSuggestion,
    IssueType, Severity
)
from src.ai_analyzer import AIAnalyzer


class CodeReviewer:
    """Main code reviewer that orchestrates the review process."""
    
    def __init__(self, ai_analyzer: Optional[AIAnalyzer] = None):
        self.ai_analyzer = ai_analyzer or AIAnalyzer()
        self.static_analyzers = {
            'python': self._analyze_python_static,
            'javascript': self._analyze_javascript_static,
            'typescript': self._analyze_typescript_static,
            'java': self._analyze_java_static,
        }
    
    async def review_code(self, request: CodeReviewRequest) -> CodeReviewResponse:
        """Perform comprehensive code review."""
        # Static analysis first
        static_issues = self._perform_static_analysis(request)
        
        # AI analysis
        ai_response = await self.ai_analyzer.analyze_code(request)
        
        # Combine results
        combined_issues = static_issues + ai_response.issues
        combined_suggestions = ai_response.suggestions
        
        # Calculate overall scores
        overall_score = self._calculate_overall_score(combined_issues, ai_response)
        
        return CodeReviewResponse(
            issues=combined_issues,
            suggestions=combined_suggestions,
            summary=ai_response.summary,
            overall_score=overall_score,
            complexity_score=ai_response.complexity_score,
            maintainability_score=ai_response.maintainability_score,
            security_score=ai_response.security_score,
            performance_score=ai_response.performance_score,
            metadata={
                **ai_response.metadata,
                "static_issues_count": len(static_issues),
                "ai_issues_count": len(ai_response.issues)
            }
        )
    
    def _perform_static_analysis(self, request: CodeReviewRequest) -> List[CodeIssue]:
        """Perform static analysis based on language."""
        language = request.language.lower()
        analyzer = self.static_analyzers.get(language)
        
        if analyzer:
            return analyzer(request.code)
        return []
    
    def _analyze_python_static(self, code: str) -> List[CodeIssue]:
        """Static analysis for Python code."""
        issues = []
        
        try:
            # Parse AST
            tree = ast.parse(code)
            
            # Check for common issues
            for node in ast.walk(tree):
                # Check for bare except clauses
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(CodeIssue(
                        type=IssueType.BEST_PRACTICE,
                        severity=Severity.MEDIUM,
                        title="Bare Except Clause",
                        description="Using bare except clauses can mask errors",
                        suggestion="Specify the exception type to catch",
                        confidence=0.9
                    ))
                
                # Check for hardcoded credentials
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and 'password' in target.id.lower():
                            issues.append(CodeIssue(
                                type=IssueType.SECURITY,
                                severity=Severity.HIGH,
                                title="Hardcoded Password",
                                description="Password appears to be hardcoded",
                                suggestion="Use environment variables or secure configuration",
                                confidence=0.8
                            ))
                
                # Check for long functions
                if isinstance(node, ast.FunctionDef):
                    lines = len(code.split('\n'))
                    if lines > 50:
                        issues.append(CodeIssue(
                            type=IssueType.MAINTAINABILITY,
                            severity=Severity.MEDIUM,
                            title="Long Function",
                            description=f"Function has {lines} lines",
                            suggestion="Consider breaking into smaller functions",
                            confidence=0.7
                        ))
        
        except SyntaxError as e:
            issues.append(CodeIssue(
                type=IssueType.BUG,
                severity=Severity.HIGH,
                title="Syntax Error",
                description=f"Python syntax error: {str(e)}",
                suggestion="Fix the syntax error",
                confidence=1.0
            ))
        
        return issues
    
    def _analyze_javascript_static(self, code: str) -> List[CodeIssue]:
        """Static analysis for JavaScript code."""
        issues = []
        
        # Check for common JavaScript issues
        patterns = [
            (r'eval\s*\(', IssueType.SECURITY, Severity.HIGH, "Use of eval()", "eval() can be dangerous", "Avoid eval() and use safer alternatives"),
            (r'console\.log', IssueType.STYLE, Severity.LOW, "Console.log in production", "console.log should be removed from production code", "Use proper logging framework"),
            (r'var\s+', IssueType.STYLE, Severity.LOW, "Use of var", "var has function scope, prefer let/const", "Use let or const instead of var"),
        ]
        
        for pattern, issue_type, severity, title, description, suggestion in patterns:
            if re.search(pattern, code):
                issues.append(CodeIssue(
                    type=issue_type,
                    severity=severity,
                    title=title,
                    description=description,
                    suggestion=suggestion,
                    confidence=0.8
                ))
        
        return issues
    
    def _analyze_typescript_static(self, code: str) -> List[CodeIssue]:
        """Static analysis for TypeScript code."""
        issues = []
        
        # Check for TypeScript-specific issues
        patterns = [
            (r'any\s*:', IssueType.STYLE, Severity.MEDIUM, "Use of any type", "any type defeats TypeScript's type checking", "Use specific types instead of any"),
            (r'//\s*todo', IssueType.DOCUMENTATION, Severity.LOW, "TODO comment", "TODO comments should be addressed", "Address the TODO or create an issue"),
        ]
        
        for pattern, issue_type, severity, title, description, suggestion in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(CodeIssue(
                    type=issue_type,
                    severity=severity,
                    title=title,
                    description=description,
                    suggestion=suggestion,
                    confidence=0.7
                ))
        
        return issues
    
    def _analyze_java_static(self, code: str) -> List[CodeIssue]:
        """Static analysis for Java code."""
        issues = []
        
        # Check for Java-specific issues
        patterns = [
            (r'System\.out\.println', IssueType.STYLE, Severity.LOW, "System.out.println", "Use proper logging framework", "Use SLF4J or Log4j"),
            (r'catch\s*\(Exception\s+e\)', IssueType.BEST_PRACTICE, Severity.MEDIUM, "Generic Exception catch", "Catching generic Exception is not recommended", "Catch specific exceptions"),
        ]
        
        for pattern, issue_type, severity, title, description, suggestion in patterns:
            if re.search(pattern, code):
                issues.append(CodeIssue(
                    type=issue_type,
                    severity=severity,
                    title=title,
                    description=description,
                    suggestion=suggestion,
                    confidence=0.8
                ))
        
        return issues
    
    def _calculate_overall_score(self, issues: List[CodeIssue], ai_response: CodeReviewResponse) -> float:
        """Calculate overall code quality score."""
        if not issues:
            return 9.0
        
        # Weight issues by severity
        severity_weights = {
            Severity.LOW: 0.1,
            Severity.MEDIUM: 0.3,
            Severity.HIGH: 0.6,
            Severity.CRITICAL: 1.0
        }
        
        total_weight = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_weight = len(issues) * 1.0
        
        if max_possible_weight == 0:
            return 10.0
        
        # Calculate score (higher is better)
        score = 10.0 - (total_weight / max_possible_weight) * 5.0
        
        # Consider AI score if available
        if ai_response.overall_score:
            score = (score + ai_response.overall_score) / 2
        
        return max(0.0, min(10.0, score))
    
    async def review_file(self, file_path: str, content: str, language: Optional[str] = None) -> CodeReviewResponse:
        """Review an entire file."""
        if not language:
            language = self._detect_language(file_path)
        
        request = CodeReviewRequest(
            code=content,
            language=language,
            file_path=file_path
        )
        
        return await self.review_code(request)
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
        }
        
        return language_map.get(ext, 'text')
    
    async def review_security(self, code: str, language: str) -> List[CodeIssue]:
        """Specialized security review."""
        return await self.ai_analyzer.analyze_security(code, language)
    
    async def review_performance(self, code: str, language: str) -> List[CodeIssue]:
        """Specialized performance review."""
        return await self.ai_analyzer.analyze_performance(code, language) 