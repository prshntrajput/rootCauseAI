"""
Main Patcher Module
High-level interface for applying fixes
"""

from typing import List, Dict, Tuple
from pathlib import Path

from backend.graph.state import FixSuggestion
from .applier import PatchApplier
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax


class SmartPatcher:
    """
    High-level interface for applying code fixes safely
    """
    
    def __init__(
        self,
        backup_dir: str = ".fix-error-backup",
        history_file: str = ".fix-error-history.json"
    ):
        """
        Initialize smart patcher
        
        Args:
            backup_dir: Directory for backups
            history_file: Path to history file
        """
        self.applier = PatchApplier(backup_dir, history_file)
        self.console = Console()
    
    def apply_fixes(
        self,
        fixes: List[FixSuggestion],
        language: str,
        dry_run: bool = False,
        interactive: bool = True
    ) -> Dict:
        """
        Apply multiple fixes
        
        Args:
            fixes: List of fix suggestions
            language: Programming language
            dry_run: Preview without applying
            interactive: Ask for confirmation
            
        Returns:
            Dictionary with results
        """
        results = {
            "total": len(fixes),
            "applied": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        self.console.print(f"\n[bold cyan]{'Dry Run' if dry_run else 'Applying'} {len(fixes)} Fix(es)...[/bold cyan]\n")
        
        for i, fix in enumerate(fixes, 1):
            self.console.print(f"[bold]Fix {i}/{len(fixes)}:[/bold] {Path(fix.file_path).name}")
            self.console.print(f"  Confidence: {fix.confidence:.0%}")
            self.console.print(f"  {fix.explanation}\n")
            
            # Show diff
            self._show_diff(fix)
            
            # Interactive confirmation
            if interactive and not dry_run:
                response = self.console.input("\n  [yellow]Apply this fix? (y/n/q):[/yellow] ").lower()
                
                if response == 'q':
                    self.console.print("  [red]Aborted by user[/red]\n")
                    results["skipped"] += len(fixes) - i + 1
                    break
                elif response != 'y':
                    self.console.print("  [yellow]Skipped[/yellow]\n")
                    results["skipped"] += 1
                    results["details"].append({
                        "file": fix.file_path,
                        "status": "skipped",
                        "message": "User declined"
                    })
                    continue
            
            # Apply fix
            success, message = self.applier.apply_patch(
                file_path=fix.file_path,
                original_snippet=fix.original_snippet,
                new_snippet=fix.new_snippet,
                language=language,
                dry_run=dry_run
            )
            
            if success:
                self.console.print(f"  [green]✅ {message}[/green]\n")
                results["applied"] += 1
                results["details"].append({
                    "file": fix.file_path,
                    "status": "applied",
                    "message": message
                })
            else:
                self.console.print(f"  [red]❌ {message}[/red]\n")
                results["failed"] += 1
                results["details"].append({
                    "file": fix.file_path,
                    "status": "failed",
                    "message": message
                })
        
        # Summary
        self._show_summary(results, dry_run)
        
        return results
    
    def _show_diff(self, fix: FixSuggestion):
        """Show code diff"""
        self.console.print("  [red]- Original:[/red]")
        
        # Detect language for syntax highlighting
        lang = "python"  # Default
        if fix.file_path.endswith(('.js', '.jsx')):
            lang = "javascript"
        elif fix.file_path.endswith(('.ts', '.tsx')):
            lang = "typescript"
        
        try:
            self.console.print(Syntax(
                fix.original_snippet,
                lang,
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            ))
        except:
            self.console.print(f"    {fix.original_snippet}")
        
        self.console.print("\n  [green]+ Fixed:[/green]")
        try:
            self.console.print(Syntax(
                fix.new_snippet,
                lang,
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            ))
        except:
            self.console.print(f"    {fix.new_snippet}")
    
    def _show_summary(self, results: Dict, dry_run: bool):
        """Show summary table"""
        self.console.print("\n" + "="*60)
        
        table = Table(title="Fix Application Summary" if not dry_run else "Dry Run Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="yellow")
        
        table.add_row("Total Fixes", str(results["total"]))
        table.add_row("Applied", f"[green]{results['applied']}[/green]")
        table.add_row("Failed", f"[red]{results['failed']}[/red]")
        table.add_row("Skipped", f"[yellow]{results['skipped']}[/yellow]")
        
        self.console.print(table)
        self.console.print("="*60 + "\n")
    
    def undo_last_fix(self) -> Tuple[bool, str]:
        """Undo the most recent fix"""
        return self.applier.undo_last_fix()
    
    def undo_fix(self, fix_id: str) -> Tuple[bool, str]:
        """Undo a specific fix"""
        return self.applier.undo_fix(fix_id)
    
    def show_history(self, count: int = 10):
        """Show fix history"""
        recent_fixes = self.applier.history_tracker.get_recent_fixes(count)
        
        if not recent_fixes:
            self.console.print("[yellow]No fix history available[/yellow]")
            return
        
        table = Table(title=f"Recent Fixes (Last {count})")
        table.add_column("Fix ID", style="cyan")
        table.add_column("File", style="yellow")
        table.add_column("Timestamp", style="green")
        table.add_column("Status", style="magenta")
        
        for fix in recent_fixes:
            status = "Reverted" if fix.get("reverted", False) else "Active"
            status_color = "red" if fix.get("reverted") else "green"
            
            table.add_row(
                fix["fix_id"],
                Path(fix["file_path"]).name,
                fix["timestamp"][:19],
                f"[{status_color}]{status}[/{status_color}]"
            )
        
        self.console.print(table)
    
    def show_stats(self):
        """Show fix statistics"""
        stats = self.applier.history_tracker.get_stats()
        
        panel_content = f"""[bold cyan]Total Fixes:[/bold cyan] {stats['total_fixes']}
[bold green]Active Fixes:[/bold green] {stats['active_fixes']}
[bold red]Reverted:[/bold red] {stats['reverted_count']}
[bold yellow]Files Modified:[/bold yellow] {stats['files_modified']}"""
        
        self.console.print(Panel(
            panel_content,
            title="[bold]Fix Statistics[/bold]",
            border_style="cyan"
        ))
    
    def list_backups(self, file_path: str = None):
        """List available backups"""
        backups = self.applier.backup_manager.list_backups(file_path)
        
        if not backups:
            self.console.print("[yellow]No backups found[/yellow]")
            return
        
        table = Table(title="Available Backups")
        table.add_column("Original File", style="cyan")
        table.add_column("Backup Path", style="yellow")
        table.add_column("Size", style="green")
        table.add_column("Date", style="magenta")
        
        for backup in backups:
            table.add_row(
                backup["original_name"],
                Path(backup["path"]).name,
                f"{backup['size']} bytes",
                backup["modified"].strftime("%Y-%m-%d %H:%M:%S")
            )
        
        self.console.print(table)
