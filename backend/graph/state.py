"""
Agent State Models
Defines the state that flows through the LangGraph
"""

from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field

from backend.parsers.base_parser import ParsedError
from backend.context.context_builder import CodeContext


class FixSuggestion(BaseModel):
    """Represents a single code fix suggestion"""
    
    file_path: str = Field(description="Path to file to fix")
    original_snippet: str = Field(description="Original code to replace")
    new_snippet: str = Field(description="New corrected code")
    explanation: str = Field(description="Why this fix works")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in this fix (0-1)"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Approximate line number"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "original_snippet": "result = x + y",
                "new_snippet": "result = int(x) + int(y)",
                "explanation": "Convert strings to integers before addition",
                "confidence": 0.95,
                "line_number": 42
            }
        }


class ValidationResult(BaseModel):
    """Result of fix validation"""
    
    is_valid: bool = Field(description="Whether fix is valid")
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if invalid"
    )
    validated_fixes: List[FixSuggestion] = Field(
        default_factory=list,
        description="Fixes that passed validation"
    )
    failed_fixes: List[tuple] = Field(
        default_factory=list,
        description="Fixes that failed validation"
    )


class AgentState(TypedDict):
    """
    Complete state that flows through the agent workflow
    This is passed between all nodes in the graph
    """
    
    # Input
    raw_error_log: str
    project_root: str
    provider: str
    
    # Step 1: Parse error
    parsed_error: Optional[ParsedError]
    parse_success: bool
    
    # Step 2: Gather context
    code_context: Optional[CodeContext]
    context_success: bool
    
    # Step 3: Analyze root cause
    root_cause_analysis: Optional[str]
    analysis_success: bool
    
    # Step 4: Generate fixes
    fix_suggestions: Optional[List[FixSuggestion]]
    generation_success: bool
    
    # Step 5: Validate fixes
    validation_result: Optional[ValidationResult]
    validation_success: bool
    
    # Retry logic
    retry_count: int
    max_retries: int
    retry_feedback: Optional[str]
    
    # Final output
    final_fixes: Optional[List[FixSuggestion]]
    status: Literal[
        "pending",
        "parsing",
        "gathering",
        "analyzing",
        "generating",
        "validating",
        "refining",
        "success",
        "failed"
    ]
    error_message: Optional[str]
    
    # Metadata
    tokens_used: int
    execution_time: float
