"""
Graph Builder
Constructs the LangGraph workflow
"""

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    parse_error_node,
    gather_context_node,
    analyze_root_cause_node,
    generate_fixes_node,
    validate_fixes_node,
    refine_fixes_node
)
from .edges import (
    should_continue_after_parse,
    should_continue_after_gather,
    should_continue_after_analyze,
    should_continue_after_generate,
    should_retry_after_validate
)


def build_agent_graph() -> StateGraph:
    """
    Build the complete agent workflow graph
    
    Graph flow:
    1. parse_error → gather_context
    2. gather_context → analyze_root_cause
    3. analyze_root_cause → generate_fixes
    4. generate_fixes → validate_fixes
    5. validate_fixes → [refine_fixes OR end]
    6. refine_fixes → generate_fixes (retry loop)
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("parse_error", parse_error_node)
    workflow.add_node("gather_context", gather_context_node)
    workflow.add_node("analyze_root_cause", analyze_root_cause_node)
    workflow.add_node("generate_fixes", generate_fixes_node)
    workflow.add_node("validate_fixes", validate_fixes_node)
    workflow.add_node("refine_fixes", refine_fixes_node)
    
    # Set entry point
    workflow.set_entry_point("parse_error")
    
    # Add conditional edges with routing logic
    workflow.add_conditional_edges(
        "parse_error",
        should_continue_after_parse,
        {
            "gather": "gather_context",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "gather_context",
        should_continue_after_gather,
        {
            "analyze": "analyze_root_cause",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "analyze_root_cause",
        should_continue_after_analyze,
        {
            "generate": "generate_fixes",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_fixes",
        should_continue_after_generate,
        {
            "validate": "validate_fixes",
            "end": END
        }
    )
    
    # Key retry logic: validate → [refine OR end]
    workflow.add_conditional_edges(
        "validate_fixes",
        should_retry_after_validate,
        {
            "refine": "refine_fixes",
            "end": END
        }
    )
    
    # Refine loops back to generate
    workflow.add_edge("refine_fixes", "generate_fixes")
    
    # Compile the graph
    return workflow.compile()


def visualize_graph(graph: StateGraph, output_path: str = "agent_graph.png"):
    """
    Visualize the graph structure (optional)
    Requires pygraphviz: pip install pygraphviz
    
    Args:
        graph: Compiled graph
        output_path: Where to save visualization
    """
    try:
        from IPython.display import Image, display
        
        # Get mermaid diagram
        diagram = graph.get_graph().draw_mermaid()
        print("Graph structure (Mermaid):")
        print(diagram)
        
    except ImportError:
        print("Install pygraphviz to visualize graph: pip install pygraphviz")
