"""
Watch Mode - Continuous Error Monitoring
"""

import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .ui import CliUI, console
from .commands import Commands


class ErrorWatcher(FileSystemEventHandler):
    """Watch for file changes and auto-fix errors"""
    
    def __init__(self, commands: Commands):
        self.commands = commands
        self.ui = CliUI()
    
    def on_modified(self, event):
        """Handle file modification"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only watch Python files
        if file_path.suffix not in ['.py', '.js', '.ts']:
            return
        
        console.print(f"\n[cyan]File changed:[/cyan] {file_path}")
        
        # Try to run the file
        if file_path.suffix == '.py':
            self.check_python_file(file_path)
    
    def check_python_file(self, file_path: Path):
        """Check Python file for errors"""
        try:
            result = subprocess.run(
                ["python", str(file_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                error_log = result.stderr
                console.print("[yellow]Error detected! Analyzing...[/yellow]")
                
                self.commands.analyze_and_fix(
                    error_log,
                    interactive=False,
                    json_output=False
                )
        
        except subprocess.TimeoutExpired:
            console.print("[yellow]Script timeout (might be running server)[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def watch_mode(path: str = ".", commands: Commands = None):
    """Start watch mode"""
    if commands is None:
        commands = Commands()
    
    ui = CliUI()
    ui.print_header("👀 rootCauseAI - Watch Mode")
    
    console.print(f"\n[cyan]Watching:[/cyan] {path}")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
    
    event_handler = ErrorWatcher(commands)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        ui.print_info("Watch mode stopped")
    
    observer.join()
