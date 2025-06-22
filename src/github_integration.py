import os
import asyncio
from typing import List, Optional, Dict, Any
from github3 import GitHub
from github3.pulls import PullRequest
from github3.repos import Repository
from dotenv import load_dotenv
from src.models import CodeReviewResponse, CodeReviewRequest, GitHubPullRequestRequest
from src.code_reviewer import CodeReviewer

# Load environment variables from .env file
load_dotenv()

class GitHubIntegration:
    """GitHub integration for pull request reviews."""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.github = GitHub(token=self.token) if self.token else None
        self.reviewer = CodeReviewer()
    
    async def review_pull_request(self, request: GitHubPullRequestRequest) -> Dict[str, Any]:
        """Review a GitHub pull request."""
        if not self.github:
            raise ValueError("GitHub token not configured")
        
        try:
            # Get repository and pull request
            repo = self.github.repository(request.owner, request.repo)
            pr = repo.pull_request(request.pull_number)
            
            # Get all files in the PR
            files = list(pr.files())
            
            all_reviews = []
            total_issues = 0
            total_suggestions = 0
            
            for file in files:
                if self._should_review_file(file.filename):
                    # Get file content
                    content = self._get_file_content(repo, file.filename, pr.head.sha)
                    
                    if content:
                        # Review the file
                        review_request = CodeReviewRequest(
                            code=content,
                            language=self._detect_language(file.filename),
                            file_path=file.filename,
                            repository=f"{request.owner}/{request.repo}",
                            branch=pr.head.ref,
                            commit_hash=pr.head.sha,
                            review_focus=request.review_focus
                        )
                        
                        review = await self.reviewer.review_code(review_request)
                        all_reviews.append({
                            "file": file.filename,
                            "review": review.dict(),
                            "status": file.status
                        })
                        
                        total_issues += len(review.issues)
                        total_suggestions += len(review.suggestions)
            
            # Generate summary
            summary = self._generate_pr_summary(all_reviews, total_issues, total_suggestions)
            
            return {
                "pull_request": {
                    "number": request.pull_number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "url": pr.html_url,
                    "state": pr.state
                },
                "reviews": all_reviews,
                "summary": summary,
                "total_files_reviewed": len(all_reviews),
                "total_issues": total_issues,
                "total_suggestions": total_suggestions,
                "overall_score": self._calculate_pr_score(all_reviews)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "pull_request": None,
                "reviews": [],
                "summary": f"Error reviewing pull request: {str(e)}"
            }
    
    def _should_review_file(self, filename: str) -> bool:
        """Determine if a file should be reviewed."""
        # Skip certain file types
        skip_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.zip', '.tar', '.gz', '.rar',
            '.lock', '.min.js', '.min.css'
        }
        
        # Skip certain directories
        skip_dirs = {
            'node_modules', 'vendor', 'dist', 'build',
            '.git', '.github', '.vscode', '.idea'
        }
        
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in skip_extensions:
            return False
        
        for skip_dir in skip_dirs:
            if skip_dir in filename.split('/'):
                return False
        
        return True
    
    def _get_file_content(self, repo: Repository, filename: str, sha: str) -> Optional[str]:
        """Get file content from GitHub."""
        try:
            # Try to get content from the specific commit
            content = repo.file_contents(filename, ref=sha)
            if content and hasattr(content, 'decoded'):
                return content.decoded.decode('utf-8')
        except:
            pass
        
        try:
            # Fallback to default branch
            content = repo.file_contents(filename)
            if content and hasattr(content, 'decoded'):
                return content.decoded.decode('utf-8')
        except:
            pass
        
        return None
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        ext = os.path.splitext(filename)[1].lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
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
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.sql': 'sql',
            '.sh': 'bash',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
        }
        
        return language_map.get(ext, 'text')
    
    def _generate_pr_summary(self, reviews: List[Dict], total_issues: int, total_suggestions: int) -> str:
        """Generate a summary of the pull request review."""
        if not reviews:
            return "No files were reviewed."
        
        critical_issues = sum(
            1 for review in reviews
            for issue in review["review"]["issues"]
            if issue["severity"] == "critical"
        )
        
        high_issues = sum(
            1 for review in reviews
            for issue in review["review"]["issues"]
            if issue["severity"] == "high"
        )
        
        summary_parts = [
            f"Reviewed {len(reviews)} files",
            f"Found {total_issues} issues ({critical_issues} critical, {high_issues} high)",
            f"Provided {total_suggestions} suggestions"
        ]
        
        if critical_issues > 0:
            summary_parts.append("⚠️ Critical issues found - review required!")
        elif high_issues > 0:
            summary_parts.append("⚠️ High priority issues found")
        else:
            summary_parts.append("✅ No critical or high priority issues")
        
        return ". ".join(summary_parts)
    
    def _calculate_pr_score(self, reviews: List[Dict]) -> float:
        """Calculate overall score for the pull request."""
        if not reviews:
            return 0.0
        
        scores = []
        for review in reviews:
            score = review["review"].get("overall_score", 5.0)
            scores.append(score)
        
        return sum(scores) / len(scores)
    
    async def create_review_comment(self, owner: str, repo: str, pr_number: int, 
                                  file: str, line: int, comment: str) -> bool:
        """Create a review comment on a pull request."""
        if not self.github:
            return False
        
        try:
            repo_obj = self.github.repository(owner, repo)
            pr = repo_obj.pull_request(pr_number)
            
            # Create review comment
            pr.create_review_comment(
                body=comment,
                commit_id=pr.head.sha,
                path=file,
                position=line
            )
            
            return True
        except Exception as e:
            print(f"Error creating review comment: {e}")
            return False
    
    async def create_pull_request_review(self, owner: str, repo: str, pr_number: int,
                                       reviews: List[Dict]) -> bool:
        """Create a comprehensive pull request review."""
        if not self.github:
            return False
        
        try:
            repo_obj = self.github.repository(owner, repo)
            pr = repo_obj.pull_request(pr_number)
            
            # Prepare review comments
            comments = []
            for review in reviews:
                file = review["file"]
                for issue in review["review"]["issues"]:
                    if issue.get("line_number"):
                        comment = f"**{issue['title']}**\n\n{issue['description']}"
                        if issue.get("suggestion"):
                            comment += f"\n\n**Suggestion:** {issue['suggestion']}"
                        
                        comments.append({
                            "path": file,
                            "position": issue["line_number"],
                            "body": comment
                        })
            
            # Determine review state
            critical_issues = sum(
                1 for review in reviews
                for issue in review["review"]["issues"]
                if issue["severity"] == "critical"
            )
            
            review_state = "REQUEST_CHANGES" if critical_issues > 0 else "APPROVE"
            
            # Create review
            pr.create_review(
                body=self._generate_review_body(reviews),
                event=review_state,
                comments=comments
            )
            
            return True
        except Exception as e:
            print(f"Error creating pull request review: {e}")
            return False
    
    def _generate_review_body(self, reviews: List[Dict]) -> str:
        """Generate the body text for a pull request review."""
        total_issues = sum(len(review["review"]["issues"]) for review in reviews)
        total_suggestions = sum(len(review["review"]["suggestions"]) for review in reviews)
        
        body = f"## AI Code Review Results\n\n"
        body += f"- **Files reviewed:** {len(reviews)}\n"
        body += f"- **Issues found:** {total_issues}\n"
        body += f"- **Suggestions:** {total_suggestions}\n\n"
        
        if total_issues == 0:
            body += "✅ No issues found! Great job!\n\n"
        else:
            body += "### Issues by Severity:\n"
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            
            for review in reviews:
                for issue in review["review"]["issues"]:
                    severity_counts[issue["severity"]] += 1
            
            for severity, count in severity_counts.items():
                if count > 0:
                    body += f"- **{severity.title()}:** {count}\n"
            
            body += "\nPlease review the inline comments for detailed feedback.\n"
        
        if total_suggestions > 0:
            body += f"\n### Suggestions for Improvement\n"
            body += f"Found {total_suggestions} suggestions to improve code quality.\n"
        
        return body 