"""
CLI Commands Implementation
All command handlers for the CLI
"""

import sys
from pathlib import Path
from typing import Optional
import json

from backend.graph import AgentRunner
from backend.patcher import SmartPatcher
from .ui import CliUI, console


class Commands:
    """CLI command implementations"""
    
    def __init__(self):
        self.ui = CliUI()
        self.patcher = SmartPatcher()
    
    def run_command(
        self,
        command: str,
        provider: str = "gemini",
        max_retries: int = 2,
        interactive: bool = True,
        json_output: bool = False
    ):
        """
        Run a command and auto-fix errors
        
        Args:
            command: Command to run
            provider: LLM provider
            max_retries: Max retry attempts
            interactive: Interactive mode
            json_output: Output as JSON
        """
        import subprocess
        
        if not json_output:
            self.ui.print_header("🚀 rootCauseAI - Run & Fix")
            console.print(f"[cyan]Running:[/cyan] {command}\n")
        
        # Run command and capture output
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            # Check if command succeeded
            if result.returncode == 0:
                if not json_output:
                    self.ui.print_success("Command executed successfully!")
                    console.print(result.stdout)
                return
            
            # Command failed, try to fix
            error_log = result.stderr or result.stdout
            
            if not json_output:
                console.print("[red]Command failed with error:[/red]")
                console.print(error_log)
                console.print("\n[cyan]Analyzing error...[/cyan]\n")
            
            # Analyze and fix
            self.analyze_and_fix(
                error_log,
                provider=provider,
                max_retries=max_retries,
                interactive=interactive,
                json_output=json_output
            )
            
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                self.ui.print_error(f"Failed to run command: {e}")
    
    def analyze_and_fix(
        self,
        error_log: str,
        provider: str = "gemini",
        max_retries: int = 2,
        interactive: bool = True,
        json_output: bool = False
    ):
        """Analyze error and apply fixes"""
        try:
            # Run agent
            runner = AgentRunner(provider=provider, max_retries=max_retries)
            
            if not json_output:
                with console.status("[cyan]Analyzing error...", spinner="dots"):
                    result = runner.run(error_log)
            else:
                result = runner.run(error_log)
            
            # Handle JSON output
            if json_output:
                output = {
                    "status": result["status"],
                    "execution_time": result["execution_time"],
                    "fixes": []
                }
                
                if result.get("final_fixes"):
                    for fix in result["final_fixes"]:
                        output["fixes"].append({
                            "file_path": fix.file_path,
                            "confidence": fix.confidence,
                            "explanation": fix.explanation
                        })
                
                print(json.dumps(output, indent=2))
                return
            
            # Check status
            if result["status"] != "success" or not result.get("final_fixes"):
                self.ui.print_warning("No fixes generated")
                
                if result.get("root_cause_analysis"):
                    console.print("\n[bold]Root Cause:[/bold]")
                    console.print(result["root_cause_analysis"])
                
                return
            
            # Show fixes
            fixes = result["final_fixes"]
            self.ui.print_success(f"Generated {len(fixes)} fix(es)!")
            
            if result.get("root_cause_analysis"):
                console.print("\n[bold cyan]Root Cause Analysis:[/bold cyan]")
                console.print(result["root_cause_analysis"])
            
            console.print()
            self.ui.show_fix_table(fixes)
            
            # Apply fixes
            if interactive:
                console.print()
                self.apply_fixes_interactive(fixes, result["parsed_error"].language)
            else:
                # Auto-apply in non-interactive mode
                results = self.patcher.apply_fixes(
                    fixes=fixes,
                    language=result["parsed_error"].language,
                    dry_run=False,
                    interactive=False
                )
                
                self.ui.print_success(f"Applied {results['applied']} fix(es)")
        
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                self.ui.print_error(f"Analysis failed: {e}")
    
    def apply_fixes_interactive(self, fixes, language: str):
        """Apply fixes with interactive confirmation"""
        for i, fix in enumerate(fixes, 1):
            console.print(f"\n[bold]Fix {i}/{len(fixes)}:[/bold] {fix.file_path}")
            console.print(f"[yellow]Confidence:[/yellow] {fix.confidence:.0%}")
            console.print(f"[yellow]Explanation:[/yellow] {fix.explanation}\n")
            
            # Show diff
            self.ui.show_code_diff(fix.original_snippet, fix.new_snippet, language)
            
            # Ask for confirmation
            if self.ui.confirm("\nApply this fix?"):
                results = self.patcher.apply_fixes(
                    fixes=[fix],
                    language=language,
                    dry_run=False,
                    interactive=False
                )
                
                if results["applied"] > 0:
                    self.ui.print_success("Fix applied!")
                else:
                    self.ui.print_error("Failed to apply fix")
            else:
                self.ui.print_info("Skipped")
    
    def explain_command(self, log_file: str, json_output: bool = False):
        """Explain error from log file"""
        try:
            # Read log file
            error_log = Path(log_file).read_text()
            
            if not json_output:
                self.ui.print_header("🔍 rootCauseAI - Explain Error")
            
            # Analyze
            runner = AgentRunner(max_retries=1)
            result = runner.run(error_log)
            
            if json_output:
                output = {
                    "status": result["status"],
                    "parsed_error": result.get("parsed_error").dict() if result.get("parsed_error") else None,
                    "root_cause": result.get("root_cause_analysis")
                }
                print(json.dumps(output, indent=2))
            else:
                if result.get("parsed_error"):
                    parsed = result["parsed_error"]
                    console.print(f"\n[bold]Error Type:[/bold] {parsed.error_type}")
                    console.print(f"[bold]Language:[/bold] {parsed.language}")
                    console.print(f"[bold]Category:[/bold] {parsed.category}")
                    console.print(f"[bold]Message:[/bold] {parsed.message}")
                
                if result.get("root_cause_analysis"):
                    console.print(f"\n[bold cyan]Root Cause:[/bold cyan]")
                    console.print(result["root_cause_analysis"])
        
        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}))
            else:
                self.ui.print_error(f"Failed: {e}")
    
    def undo_command(self, fix_id: Optional[str] = None):
        """Undo a fix"""
        self.ui.print_header("↩️  rootCauseAI - Undo Fix")
        
        try:
            if fix_id:
                success, message = self.patcher.undo_fix(fix_id)
            else:
                success, message = self.patcher.undo_last_fix()
            
            if success:
                self.ui.print_success(message)
            else:
                self.ui.print_error(message)
        
        except Exception as e:
            self.ui.print_error(f"Undo failed: {e}")
    
    def history_command(self, count: int = 10):
        """Show fix history"""
        self.ui.print_header("📜 rootCauseAI - Fix History")
        
        try:
            history = self.patcher.applier.history_tracker.get_recent_fixes(count)
            
            if not history:
                self.ui.print_info("No fix history available")
            else:
                self.ui.show_history_table(history)
        
        except Exception as e:
            self.ui.print_error(f"Failed: {e}")
    
    def stats_command(self):
        """Show statistics"""
        self.ui.print_header("📊 rootCauseAI - Statistics")
        
        try:
            stats = self.patcher.applier.history_tracker.get_stats()
            self.ui.show_stats_panel(stats)
        
        except Exception as e:
            self.ui.print_error(f"Failed: {e}")
