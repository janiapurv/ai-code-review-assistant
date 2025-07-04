#!/usr/bin/env python3
"""
Setup script for AI Code Review Assistant MCP Server.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-code-review-assistant",
    version="1.0.0",
    author="janiapurv",
    author_email="janiapurv@github.com",
    description="An AI-powered code review assistant using the Model Context Protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/janiapurv/ai-code-review-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-code-review=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="code-review ai mcp model-context-protocol openai github",
    project_urls={
        "Bug Reports": "https://github.com/janiapurv/ai-code-review-assistant/issues",
        "Source": "https://github.com/janiapurv/ai-code-review-assistant",
        "Documentation": "https://github.com/janiapurv/ai-code-review-assistant/blob/main/README.md",
    },
) 