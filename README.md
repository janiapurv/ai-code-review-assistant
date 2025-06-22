# AI-Powered Code Review Assistant

An intelligent MCP (Model Context Protocol) server that provides automated code review suggestions using AI models.

## Features

- 🤖 AI-powered code analysis and suggestions
- 🔍 Automatic bug detection and security vulnerability scanning
- 📝 Intelligent documentation suggestions
- 🎯 Code quality improvement recommendations
- 🔗 GitHub/GitLab integration for pull request reviews
- 📊 Code complexity and maintainability analysis
- 🛡️ Security best practices enforcement

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-code-review-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Run the MCP server:
```bash
python -m src.main
```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
MODEL_NAME=gpt-4
MAX_TOKENS=4000
TEMPERATURE=0.1
```

## Usage

### As an MCP Server

The server can be used with any MCP-compatible client:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(
    command="python",
    args=["-m", "src.main"]
)) as (read, write):
    async with ClientSession(read, write) as session:
        # Use the code review tools
        result = await session.call_tool("review_code", {
            "code": "def hello(): print('Hello, World!')",
            "language": "python"
        })
```

### Direct API Usage

```python
from src.code_reviewer import CodeReviewer

reviewer = CodeReviewer()
review = await reviewer.review_code(
    code="your_code_here",
    language="python",
    context="Additional context about the code"
)
print(review.suggestions)
```

## API Endpoints

- `POST /review/code` - Review a single code snippet
- `POST /review/file` - Review an entire file
- `POST /review/pull-request` - Review a GitHub pull request
- `GET /health` - Health check endpoint

## Project Structure

```
src/
├── main.py                 # MCP server entry point
├── code_reviewer.py        # Core code review logic
├── github_integration.py   # GitHub API integration
├── ai_analyzer.py          # AI model integration
├── models.py              # Pydantic models
├── utils.py               # Utility functions
└── templates/             # HTML templates for reports
    └── review_report.html

tests/
├── test_code_reviewer.py
├── test_github_integration.py
└── test_ai_analyzer.py

docs/
├── api.md                 # API documentation
└── examples.md            # Usage examples
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 