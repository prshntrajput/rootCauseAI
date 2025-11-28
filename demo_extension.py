"""
Extension Demo - Shows backend API in action
"""

from rich.console import Console
from rich.panel import Panel
import time

console = Console()

console.print(Panel.fit(
    "[bold green]rootCauseAI Extension Backend Demo[/bold green]",
    border_style="green"
))

# Start backend message
console.print("\n[cyan]Step 1: Start Backend Server[/cyan]")
console.print("   Run in terminal: [yellow]python backend/server.py[/yellow]")
console.print("   Server URL: [yellow]http://localhost:8000[/yellow]")

console.print("\n[cyan]Step 2: Test Backend[/cyan]")
console.print("   Run: [yellow]python test_extension.py[/yellow]")

console.print("\n[cyan]Step 3: Install Extension[/cyan]")
console.print("   cd extension")
console.print("   npm install")
console.print("   npm run compile")

console.print("\n[cyan]Step 4: Launch Extension[/cyan]")
console.print("   1. Open VSCode in extension folder")
console.print("   2. Press F5")
console.print("   3. Extension Development Host opens")

console.print("\n[cyan]Step 5: Use Extension[/cyan]")
console.print("   1. Open Command Palette (Ctrl+Shift+P)")
console.print("   2. Type: rootCauseAI")
console.print("   3. Select: Fix Error in Terminal")
console.print("   4. Paste error log")
console.print("   5. Review and apply fixes!")

console.print("\n[bold green]✅ Extension Backend is ready![/bold green]")
console.print("\n[yellow]📖 Full guide: QUICKSTART.md[/yellow]\n")
