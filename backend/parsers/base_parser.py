"""
Abstract Base Classes for Error Parsing
Defines the interface and data models for all parsers
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class StackFrame(BaseModel):
    """Represents a single frame in a stack trace"""
    
    file_path: str = Field(description="Path to the file where error occurred")
    line: int = Field(description="Line number", ge=1)
    column: Optional[int] = Field(default=None, description="Column number (if available)", ge=1)
    function: Optional[str] = Field(default=None, description="Function/method name")
    code_snippet: Optional[str] = Field(default=None, description="The actual line of code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "app.py",
                "line": 42,
                "column": 10,
                "function": "calculate_sum",
                "code_snippet": "result = x + y"
            }
        }


class ParsedError(BaseModel):
    """Structured representation of a parsed error"""
    
    language: Literal["python", "javascript", "typescript", "jsx", "tsx", "unknown"] = Field(
        description="Programming language"
    )
    framework: Optional[str] = Field(
        default=None,
        description="Framework/library (react, vue, express, django, etc.)"
    )
    error_type: str = Field(
        description="Error class/type (TypeError, SyntaxError, etc.)"
    )
    message: str = Field(
        description="Error message"
    )
    stack_frames: List[StackFrame] = Field(
        default_factory=list,
        description="Stack trace frames"
    )
    severity: Literal["error", "warning", "info"] = Field(
        default="error",
        description="Severity level"
    )
    category: Literal["syntax", "runtime", "import", "type", "linting", "build", "unknown"] = Field(
        description="Error category"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Parser confidence score"
    )
    raw_error: Optional[str] = Field(
        default=None,
        description="Original error text for reference"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "python",
                "framework": "fastapi",
                "error_type": "AttributeError",
                "message": "'NoneType' object has no attribute 'get'",
                "stack_frames": [
                    {
                        "file_path": "main.py",
                        "line": 15,
                        "function": "get_user"
                    }
                ],
                "severity": "error",
                "category": "runtime",
                "confidence": 0.95
            }
        }


class BaseParser(ABC):
    """
    Abstract base class for all error parsers
    Each parser must implement detection and parsing logic
    """
    
    @abstractmethod
    def can_parse(self, error_log: str) -> float:
        """
        Determine if this parser can handle the error
        
        Args:
            error_log: Raw error log text
            
        Returns:
            Confidence score (0.0 to 1.0)
            - 0.0 = Cannot parse
            - 0.5 = Maybe can parse
            - 1.0 = Definitely can parse
        """
        pass
    
    @abstractmethod
    def parse(self, error_log: str) -> ParsedError:
        """
        Parse the error log into structured format
        
        Args:
            error_log: Raw error log text
            
        Returns:
            ParsedError object with structured data
            
        Raises:
            ValueError: If parsing fails
        """
        pass
    
    def get_parser_name(self) -> str:
        """Get the name of this parser"""
        return self.__class__.__name__.replace("Parser", "")
