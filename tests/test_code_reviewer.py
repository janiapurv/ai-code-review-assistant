import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from src.code_reviewer import CodeReviewer
from src.models import CodeReviewRequest, IssueType, Severity


class TestCodeReviewer:
    """Test cases for the CodeReviewer class."""
    
    @pytest.fixture
    def reviewer(self):
        """Create a CodeReviewer instance for testing."""
        return CodeReviewer()
    
    @pytest.fixture
    def mock_ai_analyzer(self):
        """Create a mock AI analyzer."""
        analyzer = Mock()
        analyzer.analyze_code = AsyncMock()
        return analyzer
    
    def test_init(self):
        """Test CodeReviewer initialization."""
        reviewer = CodeReviewer()
        assert reviewer.ai_analyzer is not None
        assert 'python' in reviewer.static_analyzers
        assert 'javascript' in reviewer.static_analyzers
    
    def test_init_with_custom_analyzer(self, mock_ai_analyzer):
        """Test CodeReviewer initialization with custom AI analyzer."""
        reviewer = CodeReviewer(ai_analyzer=mock_ai_analyzer)
        assert reviewer.ai_analyzer == mock_ai_analyzer
    
    def test_detect_language(self, reviewer):
        """Test language detection from file paths."""
        assert reviewer._detect_language("test.py") == "python"
        assert reviewer._detect_language("script.js") == "javascript"
        assert reviewer._detect_language("app.ts") == "typescript"
        assert reviewer._detect_language("Main.java") == "java"
        assert reviewer._detect_language("unknown.xyz") == "text"
    
    def test_analyze_python_static_bare_except(self, reviewer):
        """Test static analysis for Python bare except clauses."""
        code = """
def test_function():
    try:
        result = 1 / 0
    except:
        print("Error")
"""
        issues = reviewer._analyze_python_static(code)
        
        assert len(issues) >= 1
        bare_except_issue = next(
            (issue for issue in issues if "Bare Except" in issue.title), None
        )
        assert bare_except_issue is not None
        assert bare_except_issue.type == IssueType.BEST_PRACTICE
        assert bare_except_issue.severity == Severity.MEDIUM
    
    def test_analyze_python_static_hardcoded_password(self, reviewer):
        """Test static analysis for hardcoded passwords."""
        code = """
def connect_database():
    password = "secret123"
    return connect(user="admin", password=password)
"""
        issues = reviewer._analyze_python_static(code)
        
        assert len(issues) >= 1
        password_issue = next(
            (issue for issue in issues if "Hardcoded Password" in issue.title), None
        )
        assert password_issue is not None
        assert password_issue.type == IssueType.SECURITY
        assert password_issue.severity == Severity.HIGH
    
    def test_analyze_python_static_syntax_error(self, reviewer):
        """Test static analysis for syntax errors."""
        code = """
def test_function():
    print("Hello"
"""
        issues = reviewer._analyze_python_static(code)
        
        assert len(issues) >= 1
        syntax_issue = next(
            (issue for issue in issues if "Syntax Error" in issue.title), None
        )
        assert syntax_issue is not None
        assert syntax_issue.type == IssueType.BUG
        assert syntax_issue.severity == Severity.HIGH
    
    def test_analyze_javascript_static(self, reviewer):
        """Test static analysis for JavaScript code."""
        code = """
function test() {
    eval("console.log('test')");
    console.log("debug");
    var x = 1;
}
"""
        issues = reviewer._analyze_javascript_static(code)
        
        assert len(issues) >= 2  # eval and console.log issues
        
        eval_issue = next(
            (issue for issue in issues if "eval()" in issue.title), None
        )
        assert eval_issue is not None
        assert eval_issue.type == IssueType.SECURITY
        
        console_issue = next(
            (issue for issue in issues if "console.log" in issue.title), None
        )
        assert console_issue is not None
        assert console_issue.type == IssueType.STYLE
    
    def test_analyze_typescript_static(self, reviewer):
        """Test static analysis for TypeScript code."""
        code = """
interface Test {
    data: any;
}

// TODO: implement this function
function test() {
    return true;
}
"""
        issues = reviewer._analyze_typescript_static(code)
        
        assert len(issues) >= 1
        
        any_issue = next(
            (issue for issue in issues if "any type" in issue.title), None
        )
        assert any_issue is not None
        assert any_issue.type == IssueType.STYLE
    
    def test_analyze_java_static(self, reviewer):
        """Test static analysis for Java code."""
        code = """
public class Test {
    public void test() {
        System.out.println("Hello");
    }
    
    public void handleException() {
        try {
            // some code
        } catch (Exception e) {
            // handle
        }
    }
}
"""
        issues = reviewer._analyze_java_static(code)
        
        assert len(issues) >= 1
        
        system_out_issue = next(
            (issue for issue in issues if "System.out.println" in issue.title), None
        )
        assert system_out_issue is not None
        assert system_out_issue.type == IssueType.STYLE
    
    def test_calculate_overall_score_no_issues(self, reviewer):
        """Test overall score calculation with no issues."""
        from src.models import CodeReviewResponse
        
        ai_response = CodeReviewResponse(
            issues=[],
            suggestions=[],
            summary="No issues",
            overall_score=8.0
        )
        
        score = reviewer._calculate_overall_score([], ai_response)
        assert score == 8.0
    
    def test_calculate_overall_score_with_issues(self, reviewer):
        """Test overall score calculation with issues."""
        from src.models import CodeReviewResponse, CodeIssue
        
        issues = [
            CodeIssue(
                type=IssueType.SECURITY,
                severity=Severity.HIGH,
                title="Test Issue",
                description="Test description",
                confidence=0.8
            )
        ]
        
        ai_response = CodeReviewResponse(
            issues=[],
            suggestions=[],
            summary="Some issues",
            overall_score=7.0
        )
        
        score = reviewer._calculate_overall_score(issues, ai_response)
        assert 0.0 <= score <= 10.0
    
    @pytest.mark.asyncio
    async def test_review_code(self, reviewer, mock_ai_analyzer):
        """Test the main review_code method."""
        # Mock the AI analyzer response
        from src.models import CodeReviewResponse, CodeIssue, CodeSuggestion
        
        mock_response = CodeReviewResponse(
            issues=[
                CodeIssue(
                    type=IssueType.SECURITY,
                    severity=Severity.MEDIUM,
                    title="AI Found Issue",
                    description="AI description",
                    confidence=0.9
                )
            ],
            suggestions=[
                CodeSuggestion(
                    title="AI Suggestion",
                    description="AI suggestion description",
                    reasoning="AI reasoning",
                    impact="medium"
                )
            ],
            summary="AI review completed",
            overall_score=8.5
        )
        
        mock_ai_analyzer.analyze_code.return_value = mock_response
        reviewer.ai_analyzer = mock_ai_analyzer
        
        request = CodeReviewRequest(
            code="def test(): pass",
            language="python"
        )
        
        result = await reviewer.review_code(request)
        
        assert result.overall_score > 0
        assert len(result.issues) >= 1
        assert len(result.suggestions) >= 1
        assert "AI review completed" in result.summary
    
    @pytest.mark.asyncio
    async def test_review_file(self, reviewer):
        """Test file review functionality."""
        content = "def test(): pass"
        result = await reviewer.review_file("test.py", content)
        
        assert result.overall_score > 0
        assert isinstance(result.summary, str)
    
    @pytest.mark.asyncio
    async def test_review_security(self, reviewer, mock_ai_analyzer):
        """Test security review functionality."""
        mock_ai_analyzer.analyze_security = AsyncMock(return_value=[])
        reviewer.ai_analyzer = mock_ai_analyzer
        
        issues = await reviewer.review_security("def test(): pass", "python")
        assert isinstance(issues, list)
    
    @pytest.mark.asyncio
    async def test_review_performance(self, reviewer, mock_ai_analyzer):
        """Test performance review functionality."""
        mock_ai_analyzer.analyze_performance = AsyncMock(return_value=[])
        reviewer.ai_analyzer = mock_ai_analyzer
        
        issues = await reviewer.review_performance("def test(): pass", "python")
        assert isinstance(issues, list) 