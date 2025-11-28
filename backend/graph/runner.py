"""
Graph Runner
Executes the agent workflow and handles results
"""

import time
from typing import Dict, Optional
from pathlib import Path

from .builder import build_agent_graph
from .state import AgentState
from backend.config import settings


class AgentRunner:
    """
    Runs the LangGraph agent workflow
    """
    
    def __init__(
        self,
        provider: Optional[str] = None,
        max_retries: int = 3,
        project_root: str = "."
    ):
        """
        Initialize agent runner
        
        Args:
            provider: LLM provider name (None = use default)
            max_retries: Maximum retry attempts
            project_root: Project root directory
        """
        self.provider = provider or settings.default_provider
        self.max_retries = max_retries
        self.project_root = project_root
        self.graph = build_agent_graph()
    
    def run(self, error_log: str) -> Dict:
        """
        Run the agent on an error log
        
        Args:
            error_log: Raw error log text
            
        Returns:
            Final state dictionary with results
        """
        start_time = time.time()
        
        # Initialize state
        initial_state: AgentState = {
            # Input
            "raw_error_log": error_log,
            "project_root": self.project_root,
            "provider": self.provider,
            
            # Step results (all None initially)
            "parsed_error": None,
            "parse_success": False,
            
            "code_context": None,
            "context_success": False,
            
            "root_cause_analysis": None,
            "analysis_success": False,
            
            "fix_suggestions": None,
            "generation_success": False,
            
            "validation_result": None,
            "validation_success": False,
            
            # Retry logic
            "retry_count": 0,
            "max_retries": self.max_retries,
            "retry_feedback": None,
            
            # Output
            "final_fixes": None,
            "status": "pending",
            "error_message": None,
            
            # Metadata
            "tokens_used": 0,
            "execution_time": 0.0
        }
        
        # Execute graph
        try:
            print("\n" + "="*60)
            print("🤖 Starting rootCauseAI")
            print("="*60)
            
            final_state = self.graph.invoke(initial_state)
            
            # Calculate execution time
            final_state["execution_time"] = time.time() - start_time
            
            print("\n" + "="*60)
            print(f"✅ Agent finished in {final_state['execution_time']:.2f}s")
            print(f"   Status: {final_state['status']}")
            print(f"   Retries used: {final_state['retry_count']}/{self.max_retries}")
            print("="*60 + "\n")
            
            return final_state
            
        except Exception as e:
            print(f"\n❌ Agent execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                **initial_state,
                "status": "failed",
                "error_message": str(e),
                "execution_time": time.time() - start_time
            }
    
    def run_and_display(self, error_log: str) -> Dict:
        """
        Run agent and display results in a formatted way
        
        Args:
            error_log: Raw error log
            
        Returns:
            Final state
        """
        from rich.console import Console
        from rich.panel import Panel
        from rich.syntax import Syntax
        from rich.table import Table
        
        console = Console()
        
        # Run agent
        result = self.run(error_log)
        
        # Display results
        if result["status"] == "success" and result["final_fixes"]:
            console.print("\n[bold green]✅ Fixes Generated Successfully![/bold green]\n")
            
            # Display root cause
            if result["root_cause_analysis"]:
                console.print(Panel(
                    result["root_cause_analysis"],
                    title="[cyan]Root Cause Analysis[/cyan]",
                    border_style="cyan"
                ))
            
            # Display fixes
            console.print(f"\n[bold]Generated {len(result['final_fixes'])} Fix(es):[/bold]\n")
            
            for i, fix in enumerate(result["final_fixes"], 1):
                console.print(f"[bold cyan]Fix {i}:[/bold cyan] {fix.file_path}")
                console.print(f"[yellow]Confidence:[/yellow] {fix.confidence:.0%}")
                console.print(f"[yellow]Explanation:[/yellow] {fix.explanation}\n")
                
                # Show diff
                console.print("[red]- Original:[/red]")
                console.print(Syntax(fix.original_snippet, "python", theme="monokai", line_numbers=False))
                
                console.print("\n[green]+ Fixed:[/green]")
                console.print(Syntax(fix.new_snippet, "python", theme="monokai", line_numbers=False))
                console.print("\n" + "-"*60 + "\n")
        
        elif result["status"] == "failed":
            console.print(f"\n[bold red]❌ Agent Failed[/bold red]")
            console.print(f"Error: {result['error_message']}\n")
        
        else:
            console.print(f"\n[yellow]⚠️  No fixes generated[/yellow]")
            console.print(f"Status: {result['status']}\n")
        
        # Display stats
        stats_table = Table(title="Execution Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow")
        
        stats_table.add_row("Execution Time", f"{result['execution_time']:.2f}s")
        stats_table.add_row("Tokens Used", str(result.get('tokens_used', 0)))
        stats_table.add_row("Retries", f"{result['retry_count']}/{self.max_retries}")
        stats_table.add_row("Final Status", result['status'])
        
        console.print(stats_table)
        
        return result
