"""
Interactive Configuration Setup
"""

from pathlib import Path
from rich.prompt import Prompt, Confirm
from .ui import CliUI, console
import yaml


class ConfigCLI:
    """Interactive configuration setup"""
    
    def __init__(self):
        self.ui = CliUI()
        self.config_file = Path(".fix-error-config.yaml")
    
    def setup(self):
        """Interactive configuration setup"""
        self.ui.print_header("⚙️  rootCauseAI - Configuration")
        
        console.print("\n[cyan]Let's set up your rootCauseAI configuration![/cyan]\n")
        
        # Get API keys
        console.print("[bold]1. API Keys[/bold]")
        gemini_key = Prompt.ask(
            "Gemini API Key (from https://aistudio.google.com/app/apikey)",
            password=True
        )
        
        groq_key = Prompt.ask(
            "Groq API Key (from https://console.groq.com/keys) [optional]",
            password=True,
            default=""
        )
        
        # Get provider
        console.print("\n[bold]2. Default LLM Provider[/bold]")
        provider = Prompt.ask(
            "Choose provider",
            choices=["gemini", "groq"],
            default="gemini"
        )
        
        # Get settings
        console.print("\n[bold]3. Agent Settings[/bold]")
        max_retries = int(Prompt.ask("Max retry attempts", default="2"))
        
        # Create config
        config = {
            "gemini_api_key": gemini_key,
            "groq_api_key": groq_key or "YOUR_GROQ_API_KEY",
            "default_provider": provider,
            "gemini_model": "gemini-2.0-flash-exp",
            "groq_model": "llama-3.3-70b-versatile",
            "max_retries": max_retries,
            "confidence_threshold": 0.7,
            "max_context_tokens": 8000,
            "temperature": 0.3
        }
        
        # Save config
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        self.ui.print_success(f"Configuration saved to {self.config_file}")
        
        console.print("\n[cyan]You're all set! Try running:[/cyan]")
        console.print("[yellow]  fix-error run 'python buggy_script.py'[/yellow]\n")
