"""
Conditional Edges
Routing logic between nodes based on state
"""

from typing import Literal
from .state import AgentState


def should_continue_after_parse(state: AgentState) -> Literal["gather", "end"]:
    """
    Decide next step after parsing
    
    Returns:
        "gather" - Continue to context gathering
        "end" - Stop if parsing failed
    """
    if state["parse_success"]:
        return "gather"
    else:
        return "end"


def should_continue_after_gather(state: AgentState) -> Literal["analyze", "end"]:
    """
    Decide next step after gathering context
    
    Returns:
        "analyze" - Continue to root cause analysis
        "end" - Stop if gathering failed
    """
    if state["context_success"]:
        return "analyze"
    else:
        return "end"


def should_continue_after_analyze(state: AgentState) -> Literal["generate", "end"]:
    """
    Decide next step after analysis
    
    Returns:
        "generate" - Continue to fix generation
        "end" - Stop if analysis failed
    """
    if state["analysis_success"]:
        return "generate"
    else:
        return "end"


def should_continue_after_generate(state: AgentState) -> Literal["validate", "end"]:
    """
    Decide next step after generating fixes
    
    Returns:
        "validate" - Continue to validation
        "end" - Stop if generation failed
    """
    if state["generation_success"] and state["fix_suggestions"]:
        return "validate"
    else:
        return "end"


def should_retry_after_validate(state: AgentState) -> Literal["refine", "end"]:
    """
    Decide whether to retry after validation
    
    Returns:
        "refine" - Retry with feedback
        "end" - Stop (either success or max retries reached)
    """
    # If validation succeeded, we're done
    if state["validation_success"]:
        return "end"
    
    # If we haven't reached max retries, refine
    if state["retry_count"] < state["max_retries"]:
        return "refine"
    
    # Max retries reached, stop
    return "end"
