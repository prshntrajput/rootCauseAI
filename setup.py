"""
rootCauseAI Setup
Install as a command-line tool
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme = Path("README.md").read_text() if Path("README.md").exists() else ""

setup(
    name="rootcauseai",
    version="0.1.0",
    description="AI-powered error fixing for developers",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/ai-error-fixer",
    packages=find_packages(),
    install_requires=[
        "langchain-core>=0.3.15",
        "langchain-google-genai>=2.0.5",
        "langgraph>=0.2.45",
        "google-generativeai>=0.8.3",
        "groq>=0.9.0",
        "pydantic>=2.9.2",
        "pydantic-settings>=2.6.1",
        "python-dotenv>=1.0.1",
        "PyYAML>=6.0.2",
        "typer>=0.12.5",
        "rich>=13.9.4",
        "chardet>=5.2.0",
        "fastapi>=0.115.5",
        "uvicorn[standard]>=0.32.1",
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fix-error=backend.cli.main:main",
            "rootcauseai=backend.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
)
