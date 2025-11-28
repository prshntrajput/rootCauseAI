"""
Complete Working CLI for rootCauseAI
All commands included and fully functional
"""

import typer
from typing import Optional
from pathlib import Path
import sys

app = typer.Typer(
    name="rootCauseAI",
    help="🤖 AI-powered error fixing for developers"
)


@app.command()
def run(
    command: str,
    provider: str = "gemini",
    max_retries: int = 2,
    interactive: bool = True,
    json_output: bool = False
):
    """
    🚀 Run a command and auto-fix errors
    
    Example: fix-error run "python script.py"
    """
    from backend.cli.commands import Commands
    commands = Commands()
    
    commands.run_command(
        command=command,
        provider=provider,
        max_retries=max_retries,
        interactive=interactive,
        json_output=json_output
    )


@app.command()
def fix(
    error_log: str = None,
    file: str = None,
    provider: str = "gemini",
    max_retries: int = 2,
    interactive: bool = True,
    json_output: bool = False
):
    """
    🔧 Analyze and fix an error
    
    Examples:
        fix-error fix "TypeError: ..."
        fix-error fix --file error.log
    """
    from backend.cli.commands import Commands
    commands = Commands()
    
    # Get error log
    if file:
        error_text = Path(file).read_text()
    elif error_log:
        error_text = error_log
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            error_text = sys.stdin.read()
        else:
            print("❌ Please provide error log as argument, file, or stdin")
            raise typer.Exit(1)
    
    if not error_text.strip():
        print("❌ Empty error log")
        raise typer.Exit(1)
    
    # Analyze and fix
    commands.analyze_and_fix(
        error_log=error_text,
        provider=provider,
        max_retries=max_retries,
        interactive=interactive,
        json_output=json_output
    )


@app.command()
def explain(
    error_log: str = None,
    file: str = None,
    json_output: bool = False
):
    """
    🔍 Explain an error without fixing
    
    Example: fix-error explain --file error.log
    """
    from backend.cli.commands import Commands
    commands = Commands()
    
    # Get error log
    if file:
        error_text = file
    elif error_log:
        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(error_log)
            error_text = f.name
    else:
        if not sys.stdin.isatty():
            import tempfile
            content = sys.stdin.read()
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(content)
                error_text = f.name
        else:
            print("❌ Please provide error log")
            raise typer.Exit(1)
    
    commands.explain_command(error_text, json_output=json_output)


@app.command()
def undo(fix_id: str = None):
    """
    ↩️  Undo a fix
    
    Examples:
        fix-error undo              # Undo last fix
        fix-error undo fix_1_xxx    # Undo specific fix
    """
    from backend.cli.commands import Commands
    commands = Commands()
    commands.undo_command(fix_id)


@app.command()
def history(count: int = 10):
    """
    📜 Show fix history
    
    Example: fix-error history --count 20
    """
    from backend.cli.commands import Commands
    commands = Commands()
    commands.history_command(count)


@app.command()
def stats():
    """
    📊 Show statistics
    
    Example: fix-error stats
    """
    from backend.cli.commands import Commands
    commands = Commands()
    commands.stats_command()


@app.command()
def watch(path: str = "."):
    """
    👀 Watch mode - auto-fix errors on file changes
    
    Examples:
        fix-error watch
        fix-error watch ./src
    """
    from backend.cli.commands import Commands
    from backend.cli.watch import watch_mode
    
    commands = Commands()
    watch_mode(path, commands)


@app.command()
def config():
    """
    ⚙️  Interactive configuration setup
    
    Example: fix-error config
    """
    from backend.cli.config_cli import ConfigCLI
    config_cli = ConfigCLI()
    config_cli.setup()


@app.command()
def version():
    """
    📦 Show version information
    """
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]rootCauseAI v0.1.0[/bold cyan]",
        border_style="cyan"
    ))
    console.print("\n[cyan]An AI-powered error fixing tool for developers[/cyan]")
    console.print("[yellow]Built with LangGraph, Gemini, and Groq[/yellow]\n")
    
    # Show config status
    config_file = Path(".fix-error-config.yaml")
    if config_file.exists():
        console.print("[green]✅ Configuration found[/green]")
    else:
        console.print("[yellow]⚠️  No configuration found. Run: fix-error config[/yellow]")


def main():
    """Entry point for CLI"""
    app()


if __name__ == "__main__":
    main()
