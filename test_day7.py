"""
Day 7 Test Suite
Tests CLI functionality
"""

import sys
from pathlib import Path
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def test_cli_installation():
    """Test 1: CLI installation"""
    console.print("\n[bold cyan]Test 1: CLI Installation[/bold cyan]")
    
    try:
        result = subprocess.run(
            ["fix-error", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "rootCauseAI" in result.stdout:
            console.print("   ✅ CLI installed and working")
            return 1, 1
        else:
            console.print("   ❌ CLI not working properly")
            return 0, 1
    except FileNotFoundError:
        console.print("   ❌ CLI not installed")
        console.print("   💡 Run: pip install -e .")
        return 0, 1
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_cli_commands():
    """Test 2: CLI commands available"""
    console.print("\n[bold cyan]Test 2: CLI Commands[/bold cyan]")
    
    commands = [
        "run", "fix", "explain", "undo", 
        "history", "stats", "watch", "config", "version"
    ]
    
    try:
        result = subprocess.run(
            ["fix-error", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        missing = []
        for cmd in commands:
            if cmd not in result.stdout:
                missing.append(cmd)
        
        if not missing:
            console.print(f"   ✅ All {len(commands)} commands available")
            return 1, 1
        else:
            console.print(f"   ❌ Missing commands: {', '.join(missing)}")
            return 0, 1
    
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_version_command():
    """Test 3: Version command"""
    console.print("\n[bold cyan]Test 3: Version Command[/bold cyan]")
    
    try:
        result = subprocess.run(
            ["fix-error", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "rootCauseAI" in result.stdout:
            console.print("   ✅ Version command works")
            console.print(f"   Output preview: {result.stdout[:100]}")
            return 1, 1
        else:
            console.print("   ❌ Version command failed")
            return 0, 1
    
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_stats_command():
    """Test 4: Stats command"""
    console.print("\n[bold cyan]Test 4: Stats Command[/bold cyan]")
    
    try:
        result = subprocess.run(
            ["fix-error", "stats"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            console.print("   ✅ Stats command works")
            return 1, 1
        else:
            console.print("   ❌ Stats command failed")
            return 0, 1
    
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_history_command():
    """Test 5: History command"""
    console.print("\n[bold cyan]Test 5: History Command[/bold cyan]")
    
    try:
        result = subprocess.run(
            ["fix-error", "history"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            console.print("   ✅ History command works")
            return 1, 1
        else:
            console.print("   ❌ History command failed")
            return 0, 1
    
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_json_output():
    """Test 6: JSON output mode"""
    console.print("\n[bold cyan]Test 6: JSON Output[/bold cyan]")
    
    # Create test error file
    test_file = Path("test_error.txt")
    test_file.write_text("SyntaxError: invalid syntax")
    
    try:
        result = subprocess.run(
            ["fix-error", "explain", "--file", str(test_file), "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up
        test_file.unlink()
        
        if result.returncode == 0:
            import json
            try:
                data = json.loads(result.stdout)
                console.print("   ✅ JSON output works")
                console.print(f"   Keys: {list(data.keys())}")
                return 1, 1
            except json.JSONDecodeError:
                console.print("   ⚠️  Command succeeded but output not valid JSON")
                return 0, 1
        else:
            console.print("   ❌ JSON output failed")
            return 0, 1
    
    except Exception as e:
        test_file.unlink(missing_ok=True)
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_ui_components():
    """Test 7: UI components"""
    console.print("\n[bold cyan]Test 7: UI Components[/bold cyan]")
    
    try:
        from backend.cli.ui import CliUI
        
        ui = CliUI()
        
        # Test different UI methods
        console.print("   Testing UI components:")
        ui.print_success("Success message")
        ui.print_error("Error message")
        ui.print_warning("Warning message")
        ui.print_info("Info message")
        
        # Test table
        fixes = [
            type('Fix', (), {
                'file_path': 'test.py',
                'confidence': 0.95,
                'explanation': 'Test fix'
            })()
        ]
        ui.show_fix_table(fixes)
        
        console.print("   ✅ UI components working")
        return 1, 1
    
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def test_integration():
    """Test 8: End-to-end integration"""
    console.print("\n[bold cyan]Test 8: Integration Test[/bold cyan]")
    
    # Create a buggy Python file
    buggy_file = Path("test_buggy.py")
    buggy_file.write_text("""
def add(a, b):
    return a + b

result = add("5", 10)
print(result)
""")
    
    try:
        # Try to run it and capture error
        result = subprocess.run(
            ["python", str(buggy_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error = result.stderr
            console.print(f"   ✅ Captured error: {error[:50]}...")
            
            # Save error to file
            error_file = Path("test_error_log.txt")
            error_file.write_text(error)
            
            # Try to explain it
            explain_result = subprocess.run(
                ["fix-error", "explain", "--file", str(error_file), "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up
            buggy_file.unlink()
            error_file.unlink()
            
            if explain_result.returncode == 0:
                console.print("   ✅ Full pipeline works!")
                return 1, 1
            else:
                console.print("   ⚠️  Explain command had issues")
                return 0, 1
        else:
            buggy_file.unlink()
            console.print("   ⚠️  Test script didn't produce error")
            return 0, 1
    
    except Exception as e:
        buggy_file.unlink(missing_ok=True)
        console.print(f"   ❌ Error: {e}")
        return 0, 1


def main():
    """Run all Day 7 tests"""
    console.print(Panel.fit(
        "[bold green]Day 7: CLI with Beautiful Terminal UX Test Suite[/bold green]",
        border_style="green"
    ))
    
    all_results = []
    
    # Run tests
    all_results.append(test_cli_installation())
    
    # Only continue if CLI is installed
    if all_results[0][0]:
        all_results.append(test_cli_commands())
        all_results.append(test_version_command())
        all_results.append(test_stats_command())
        all_results.append(test_history_command())
        all_results.append(test_json_output())
        all_results.append(test_ui_components())
        all_results.append(test_integration())
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Day 7 Test Summary[/bold]")
    console.print("="*60)
    
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    
    console.print(f"\nTotal Tests: {total_tests}")
    console.print(f"Passed: [green]{total_passed}[/green]")
    console.print(f"Failed: [red]{total_tests - total_passed}[/red]")
    console.print(f"Success Rate: [bold]{(total_passed/total_tests*100):.1f}%[/bold]")
    
    if total_passed == total_tests:
        console.print("\n[bold green]🎉 All Day 7 tests passed! Ready for Day 8.[/bold green]")
        console.print("\n[yellow]Next: Day 8 - Analytics & Telemetry[/yellow]")
    else:
        console.print(f"\n[yellow]⚠️  {total_tests - total_passed} test(s) need attention.[/yellow]")
        if total_passed == 0:
            console.print("\n[cyan]💡 Hint: Run 'pip install -e .' to install the CLI[/cyan]")


if __name__ == "__main__":
    main()
