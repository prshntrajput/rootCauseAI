#!/usr/bin/env python3
"""
Minimal working CLI for rootCauseAI
"""

import typer

app = typer.Typer(help="rootCauseAI - AI-powered error fixing")

@app.command()
def version():
    """Show version"""
    print("rootCauseAI v0.1.0")
    print("CLI is working!")

@app.command()
def stats():
    """Show stats"""
    from backend.patcher import SmartPatcher
    patcher = SmartPatcher()
    stats = patcher.applier.history_tracker.get_stats()
    print(f"Total fixes: {stats['total_fixes']}")
    print(f"Active: {stats['active_fixes']}")

@app.command()
def history():
    """Show history"""
    from backend.patcher import SmartPatcher
    patcher = SmartPatcher()
    history = patcher.applier.history_tracker.get_recent_fixes(10)
    print(f"Found {len(history)} fixes")

if __name__ == "__main__":
    app()
