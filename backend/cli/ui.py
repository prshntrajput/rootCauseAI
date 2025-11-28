"""
CLI UI Components
Beautiful terminal interface with Rich
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
from rich.prompt import Confirm, Prompt
from rich.tree import Tree
from typing import List, Optional
import time

console = Console()


class CliUI:
    """Rich terminal UI components"""
    
    @staticmethod
    def print_header(text: str):
        """Print header banner"""
        console.print(Panel.fit(
            f"[bold cyan]{text}[/bold cyan]",
            border_style="cyan"
        ))
    
    @staticmethod
    def print_success(text: str):
        """Print success message"""
        console.print(f"[green]✅ {text}[/green]")
    
    @staticmethod
    def print_error(text: str):
        """Print error message"""
        console.print(f"[red]❌ {text}[/red]")
    
    @staticmethod
    def print_warning(text: str):
        """Print warning message"""
        console.print(f"[yellow]⚠️  {text}[/yellow]")
    
    @staticmethod
    def print_info(text: str):
        """Print info message"""
        console.print(f"[blue]ℹ️  {text}[/blue]")
    
    @staticmethod
    def show_progress(description: str, total: Optional[int] = None):
        """Show progress bar"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        )
    
    @staticmethod
    def show_code_diff(original: str, fixed: str, language: str = "python"):
        """Show code diff with syntax highlighting"""
        console.print("\n[red]- Original:[/red]")
        console.print(Syntax(original, language, theme="monokai", line_numbers=True))
        
        console.print("\n[green]+ Fixed:[/green]")
        console.print(Syntax(fixed, language, theme="monokai", line_numbers=True))
    
    @staticmethod
    def confirm(question: str, default: bool = True) -> bool:
        """Ask for confirmation"""
        return Confirm.ask(question, default=default)
    
    @staticmethod
    def prompt(question: str, default: str = "") -> str:
        """Ask for input"""
        return Prompt.ask(question, default=default)
    
    @staticmethod
    def show_fix_table(fixes: List[dict]):
        """Show fixes in a table"""
        table = Table(title="Generated Fixes", show_header=True, header_style="bold cyan")
        
        table.add_column("#", style="dim", width=3)
        table.add_column("File", style="cyan")
        table.add_column("Confidence", style="yellow", justify="right")
        table.add_column("Explanation", style="white")
        
        for i, fix in enumerate(fixes, 1):
            confidence = f"{fix.confidence * 100:.0f}%"
            table.add_row(
                str(i),
                fix.file_path,
                confidence,
                fix.explanation[:50] + "..." if len(fix.explanation) > 50 else fix.explanation
            )
        
        console.print(table)
    
    @staticmethod
    def show_stats_panel(stats: dict):
        """Show statistics panel"""
        content = f"""[bold cyan]Total Fixes:[/bold cyan] {stats['total_fixes']}
[bold green]Active Fixes:[/bold green] {stats['active_fixes']}
[bold red]Reverted:[/bold red] {stats['reverted_count']}
[bold yellow]Files Modified:[/bold yellow] {stats['files_modified']}"""
        
        console.print(Panel(
            content,
            title="[bold]Statistics[/bold]",
            border_style="cyan"
        ))
    
    @staticmethod
    def show_history_table(history: List[dict]):
        """Show fix history table"""
        table = Table(title="Fix History", show_header=True, header_style="bold cyan")
        
        table.add_column("Fix ID", style="cyan")
        table.add_column("File", style="yellow")
        table.add_column("Timestamp", style="green")
        table.add_column("Status", style="magenta")
        
        for fix in history:
            status = "🔴 Reverted" if fix.get('reverted') else "✅ Active"
            table.add_row(
                fix['fix_id'],
                fix['file_path'],
                fix['timestamp'][:19],
                status
            )
        
        console.print(table)
    
    @staticmethod
    def animate_thinking():
        """Show thinking animation"""
        with console.status("[cyan]Analyzing...", spinner="dots"):
            time.sleep(1)
