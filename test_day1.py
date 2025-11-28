"""
Day 1 Test Suite
Tests multi-LLM architecture and provider switching
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings
from backend.llm import LLMProviderFactory
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def test_configuration():
    """Test 1: Configuration loading"""
    console.print("\n[bold cyan]Test 1: Configuration System[/bold cyan]")
    
    try:
        console.print(f"✅ Config loaded successfully")
        console.print(f"   Default provider: [yellow]{settings.default_provider}[/yellow]")
        console.print(f"   Gemini model: [yellow]{settings.gemini_model}[/yellow]")
        console.print(f"   Groq model: [yellow]{settings.groq_model}[/yellow]")
        console.print(f"   Max retries: [yellow]{settings.max_retries}[/yellow]")
        console.print(f"   Confidence threshold: [yellow]{settings.confidence_threshold}[/yellow]")
        
        # Validate API keys
        is_valid, error_msg = settings.validate_api_keys()
        if not is_valid:
            console.print(f"⚠️  [yellow]{error_msg}[/yellow]")
            return False
        else:
            console.print(f"✅ API keys validated")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Configuration failed: {e}")
        return False


def test_provider_creation():
    """Test 2: Provider factory"""
    console.print("\n[bold cyan]Test 2: Provider Creation[/bold cyan]")
    
    try:
        # List available providers
        providers = LLMProviderFactory.list_providers()
        console.print(f"✅ Available providers: {', '.join(providers)}")
        
        # Test creating providers
        for provider_name in providers:
            try:
                provider = LLMProviderFactory.create(provider_name)
                console.print(f"✅ Created {provider}")
            except ValueError as e:
                console.print(f"⚠️  Skipped {provider_name}: {e}")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Provider creation failed: {e}")
        return False


def test_gemini_generation():
    """Test 3: Gemini text generation"""
    console.print("\n[bold cyan]Test 3: Gemini Generation[/bold cyan]")
    
    try:
        provider = LLMProviderFactory.create("gemini")
        console.print(f"✅ Initialized {provider}")
        
        # Test simple generation
        system_prompt = "You are a helpful coding assistant."
        user_prompt = "In one sentence, what is a Python traceback?"
        
        console.print("📤 Sending request to Gemini...")
        response = provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        console.print(Panel(
            response.content,
            title="[green]Gemini Response[/green]",
            border_style="green"
        ))
        console.print(f"   Model: {response.model}")
        console.print(f"   Tokens used: {response.tokens_used}")
        console.print(f"   Finish reason: {response.finish_reason}")
        
        return True
        
    except ValueError as e:
        console.print(f"⚠️  Skipped: {e}")
        return None  # Skip if not configured
    except Exception as e:
        console.print(f"❌ Gemini test failed: {e}")
        return False


def test_groq_generation():
    """Test 4: Groq text generation"""
    console.print("\n[bold cyan]Test 4: Groq Generation[/bold cyan]")
    
    try:
        provider = LLMProviderFactory.create("groq")
        console.print(f"✅ Initialized {provider}")
        
        # Test simple generation
        system_prompt = "You are a helpful coding assistant."
        user_prompt = "In one sentence, what causes a JavaScript TypeError?"
        
        console.print("📤 Sending request to Groq...")
        response = provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        console.print(Panel(
            response.content,
            title="[green]Groq Response[/green]",
            border_style="green"
        ))
        console.print(f"   Model: {response.model}")
        console.print(f"   Tokens used: {response.tokens_used}")
        console.print(f"   Finish reason: {response.finish_reason}")
        
        return True
        
    except ValueError as e:
        console.print(f"⚠️  Skipped: {e}")
        return None  # Skip if not configured
    except Exception as e:
        console.print(f"❌ Groq test failed: {e}")
        return False


def test_json_generation():
    """Test 5: JSON structured output"""
    console.print("\n[bold cyan]Test 5: JSON Generation[/bold cyan]")
    
    try:
        provider = LLMProviderFactory.create(settings.default_provider)
        console.print(f"✅ Using {provider} for JSON test")
        
        system_prompt = "You are a JSON generator."
        user_prompt = "Generate a JSON object with error information: type='ImportError', severity='high', fixable=true"
        
        schema = {
            "type": "string",
            "severity": "string",
            "fixable": "boolean"
        }
        
        console.print("📤 Requesting JSON response...")
        response_json = provider.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema=schema
        )
        
        console.print(Panel(
            str(response_json),
            title="[green]JSON Response[/green]",
            border_style="green"
        ))
        
        # Validate JSON structure
        if isinstance(response_json, dict):
            console.print("✅ Valid JSON received")
            return True
        else:
            console.print("❌ Response is not a valid dictionary")
            return False
        
    except ValueError as e:
        console.print(f"⚠️  Skipped: {e}")
        return None
    except Exception as e:
        console.print(f"❌ JSON test failed: {e}")
        return False


def test_provider_switching():
    """Test 6: Switch between providers"""
    console.print("\n[bold cyan]Test 6: Provider Switching[/bold cyan]")
    
    results = Table(title="Provider Switching Test")
    results.add_column("Provider", style="cyan")
    results.add_column("Status", style="green")
    results.add_column("Response Preview", style="yellow")
    
    test_prompt = "What is an error?"
    
    for provider_name in ["gemini", "groq"]:
        try:
            provider = LLMProviderFactory.create(provider_name)
            response = provider.generate(
                system_prompt="You are helpful.",
                user_prompt=test_prompt,
                temperature=0.2,
                max_tokens=50
            )
            
            preview = response.content[:50] + "..."
            results.add_row(provider_name, "✅ Success", preview)
            
        except ValueError:
            results.add_row(provider_name, "⚠️  Not configured", "N/A")
        except Exception as e:
            results.add_row(provider_name, f"❌ Failed", str(e)[:30])
    
    console.print(results)
    return True


def main():
    """Run all Day 1 tests"""
    console.print(Panel.fit(
        "[bold green]Day 1: Multi-LLM Architecture Test Suite[/bold green]",
        border_style="green"
    ))
    
    tests = [
        ("Configuration", test_configuration),
        ("Provider Creation", test_provider_creation),
        ("Gemini Generation", test_gemini_generation),
        ("Groq Generation", test_groq_generation),
        ("JSON Generation", test_json_generation),
        ("Provider Switching", test_provider_switching),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for test_name, result in results:
        if result is True:
            console.print(f"✅ {test_name}")
        elif result is False:
            console.print(f"❌ {test_name}")
        else:
            console.print(f"⚠️  {test_name} (skipped)")
    
    console.print(f"\nTotal: {len(tests)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0:
        console.print("\n[bold green]🎉 All tests passed! Day 1 complete.[/bold green]")
    else:
        console.print(f"\n[bold red]❌ {failed} test(s) failed.[/bold red]")


if __name__ == "__main__":
    main()
