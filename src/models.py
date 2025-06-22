from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class Severity(str, Enum):
    """Severity levels for code review issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    """Types of issues that can be found during code review."""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICE = "best_practice"


class CodeIssue(BaseModel):
    """Represents a single issue found during code review."""
    type: IssueType
    severity: Severity
    title: str
    description: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class CodeSuggestion(BaseModel):
    """Represents a suggestion for code improvement."""
    title: str
    description: str
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    reasoning: str
    impact: str = "medium"


class CodeReviewRequest(BaseModel):
    """Request model for code review."""
    code: str
    language: str
    context: Optional[str] = None
    file_path: Optional[str] = None
    repository: Optional[str] = None
    branch: Optional[str] = None
    commit_hash: Optional[str] = None
    review_focus: Optional[List[str]] = None  # e.g., ["security", "performance"]


class CodeReviewResponse(BaseModel):
    """Response model for code review."""
    issues: List[CodeIssue] = []
    suggestions: List[CodeSuggestion] = []
    summary: str
    overall_score: float = Field(ge=0.0, le=10.0)
    complexity_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    security_score: Optional[float] = None
    performance_score: Optional[float] = None
    metadata: Dict[str, Any] = {}


class GitHubPullRequestRequest(BaseModel):
    """Request model for GitHub pull request review."""
    owner: str
    repo: str
    pull_number: int
    review_focus: Optional[List[str]] = None


class FileReviewRequest(BaseModel):
    """Request model for reviewing an entire file."""
    file_path: str
    content: str
    language: Optional[str] = None
    context: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str] = {}


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 