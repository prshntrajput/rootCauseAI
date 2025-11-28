"""
Day 2 Comprehensive Test Suite
Tests all parsers with real error samples
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.parsers import ErrorClassifier
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax


console = Console()


def load_error_sample(file_path: str) -> str:
    """Load error sample from file"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


def test_python_errors():
    """Test Python error parsing"""
    console.print("\n[bold cyan]Test 1: Python Error Parsing[/bold cyan]")
    
    classifier = ErrorClassifier()
    test_files = [
        ("Import Error", "tests/fixtures/python_errors/import_error.txt"),
        ("Type Error", "tests/fixtures/python_errors/type_error.txt"),
        ("Attribute Error", "tests/fixtures/python_errors/attribute_error.txt"),
        ("Syntax Error", "tests/fixtures/python_errors/syntax_error.txt"),
        ("Indentation Error", "tests/fixtures/python_errors/indentation_error.txt"),
    ]
    
    results = []
    for name, file_path in test_files:
        error_log = load_error_sample(file_path)
        if error_log is None:
            results.append((name, "⚠️  File not found", None))
            continue
        
        try:
            parsed = classifier.classify_and_parse(error_log)
            results.append((
                name,
                "✅ Parsed",
                f"{parsed.language} | {parsed.error_type} | {parsed.category}"
            ))
        except Exception as e:
            results.append((name, "❌ Failed", str(e)[:50]))
    
    # Display results
    table = Table(title="Python Error Parsing Results")
    table.add_column("Error Type", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for name, status, details in results:
        table.add_row(name, status, details or "N/A")
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results)


def test_javascript_errors():
    """Test JavaScript error parsing"""
    console.print("\n[bold cyan]Test 2: JavaScript Error Parsing[/bold cyan]")
    
    classifier = ErrorClassifier()
    test_files = [
        ("Reference Error", "tests/fixtures/javascript_errors/reference_error.txt"),
        ("Type Error", "tests/fixtures/javascript_errors/type_error.txt"),
        ("Syntax Error", "tests/fixtures/javascript_errors/syntax_error.txt"),
    ]
    
    results = []
    for name, file_path in test_files:
        error_log = load_error_sample(file_path)
        if error_log is None:
            results.append((name, "⚠️  File not found", None))
            continue
        
        try:
            parsed = classifier.classify_and_parse(error_log)
            results.append((
                name,
                "✅ Parsed",
                f"{parsed.language} | {parsed.error_type} | {len(parsed.stack_frames)} frames"
            ))
        except Exception as e:
            results.append((name, "❌ Failed", str(e)[:50]))
    
    table = Table(title="JavaScript Error Parsing Results")
    table.add_column("Error Type", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for name, status, details in results:
        table.add_row(name, status, details or "N/A")
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results)


def test_typescript_errors():
    """Test TypeScript error parsing"""
    console.print("\n[bold cyan]Test 3: TypeScript Error Parsing[/bold cyan]")
    
    classifier = ErrorClassifier()
    error_log = load_error_sample("tests/fixtures/typescript_errors/type_mismatch.txt")
    
    if error_log is None:
        console.print("⚠️  Test file not found")
        return 0, 1
    
    try:
        parsed = classifier.classify_and_parse(error_log)
        
        console.print(f"✅ Successfully parsed TypeScript error")
        console.print(f"   Language: {parsed.language}")
        console.print(f"   Error Type: {parsed.error_type}")
        console.print(f"   Category: {parsed.category}")
        console.print(f"   Errors found: {len(parsed.stack_frames)}")
        console.print(f"   Confidence: {parsed.confidence:.2f}")
        
        return 1, 1
    except Exception as e:
        console.print(f"❌ Failed to parse: {e}")
        return 0, 1


def test_react_errors():
    """Test React error parsing"""
    console.print("\n[bold cyan]Test 4: React Error Parsing[/bold cyan]")
    
    classifier = ErrorClassifier()
    test_files = [
        ("JSX Syntax Error", "tests/fixtures/react_errors/jsx_syntax.txt"),
        ("Module Not Found", "tests/fixtures/react_errors/module_not_found.txt"),
    ]
    
    results = []
    for name, file_path in test_files:
        error_log = load_error_sample(file_path)
        if error_log is None:
            results.append((name, "⚠️  File not found", None))
            continue
        
        try:
            parsed = classifier.classify_and_parse(error_log)
            results.append((
                name,
                "✅ Parsed",
                f"{parsed.language} | {parsed.framework} | {parsed.category}"
            ))
        except Exception as e:
            results.append((name, "❌ Failed", str(e)[:50]))
    
    table = Table(title="React Error Parsing Results")
    table.add_column("Error Type", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for name, status, details in results:
        table.add_row(name, status, details or "N/A")
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results)


def test_classifier_intelligence():
    """Test classifier's ability to choose correct parser"""
    console.print("\n[bold cyan]Test 5: Classifier Intelligence[/bold cyan]")
    
    classifier = ErrorClassifier()
    
    test_cases = [
        ("Python traceback", """Traceback (most recent call last):
  File "test.py", line 10
    x = 5 +
          ^
SyntaxError: invalid syntax""", "python"),
        
        ("JavaScript error", """TypeError: Cannot read property 'map' of undefined
    at render (/app/component.js:15:20)""", "javascript"),
        
        ("TypeScript error", """src/types.ts(5,10): error TS2322: Type 'string' is not assignable to type 'number'.""", "typescript"),
    ]
    
    table = Table(title="Classifier Intelligence Test")
    table.add_column("Test Case", style="cyan")
    table.add_column("Expected", style="yellow")
    table.add_column("Detected", style="green")
    table.add_column("Confidence", style="magenta")
    table.add_column("Status", style="bold")
    
    passed = 0
    for name, error_log, expected_lang in test_cases:
        try:
            scores = classifier.get_parser_scores(error_log)
            parsed = classifier.classify_and_parse(error_log)
            
            is_correct = parsed.language == expected_lang
            status = "✅" if is_correct else "❌"
            
            table.add_row(
                name,
                expected_lang,
                parsed.language,
                f"{parsed.confidence:.2f}",
                status
            )
            
            if is_correct:
                passed += 1
                
        except Exception as e:
            table.add_row(name, expected_lang, "Error", "0.00", "❌")
    
    console.print(table)
    return passed, len(test_cases)


def test_detailed_parsing():
    """Test detailed parsing of a complex error"""
    console.print("\n[bold cyan]Test 6: Detailed Parsing Example[/bold cyan]")
    
    error_log = """Traceback (most recent call last):
  File "/home/user/project/api/views.py", line 42, in get_user_data
    user = User.objects.get(id=user_id)
  File "/home/user/.venv/lib/python3.12/site-packages/django/db/models/manager.py", line 87, in get
    return self.get_queryset().get(*args, **kwargs)
  File "/home/user/project/models.py", line 156, in get
    raise self.model.DoesNotExist
User.DoesNotExist: User matching query does not exist."""
    
    classifier = ErrorClassifier()
    
    try:
        parsed = classifier.classify_and_parse(error_log)
        
        console.print(Panel.fit(
            f"""[bold]Language:[/bold] {parsed.language}
[bold]Framework:[/bold] {parsed.framework or 'None'}
[bold]Error Type:[/bold] {parsed.error_type}
[bold]Category:[/bold] {parsed.category}
[bold]Confidence:[/bold] {parsed.confidence:.2f}
[bold]Message:[/bold] {parsed.message}
[bold]Stack Frames:[/bold] {len(parsed.stack_frames)}""",
            title="[green]Parsed Error Details[/green]",
            border_style="green"
        ))
        
        # Show stack frames
        if parsed.stack_frames:
            console.print("\n[bold]Stack Trace:[/bold]")
            for i, frame in enumerate(parsed.stack_frames[:3], 1):
                console.print(f"  {i}. {frame.file_path}:{frame.line}")
                if frame.function:
                    console.print(f"     in {frame.function}()")
        
        return 1, 1
        
    except Exception as e:
        console.print(f"❌ Failed: {e}")
        return 0, 1


def main():
    """Run all Day 2 tests"""
    console.print(Panel.fit(
        "[bold green]Day 2: Error Detection & Classification Test Suite[/bold green]",
        border_style="green"
    ))
    
    all_results = []
    
    # Run all tests
    all_results.append(test_python_errors())
    all_results.append(test_javascript_errors())
    all_results.append(test_typescript_errors())
    all_results.append(test_react_errors())
    all_results.append(test_classifier_intelligence())
    all_results.append(test_detailed_parsing())
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Day 2 Test Summary[/bold]")
    console.print("="*60)
    
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    
    console.print(f"\nTotal Tests: {total_tests}")
    console.print(f"Passed: [green]{total_passed}[/green]")
    console.print(f"Failed: [red]{total_tests - total_passed}[/red]")
    console.print(f"Success Rate: [bold]{(total_passed/total_tests*100):.1f}%[/bold]")
    
    if total_passed == total_tests:
        console.print("\n[bold green]🎉 All Day 2 tests passed! Ready for Day 3.[/bold green]")
    else:
        console.print(f"\n[yellow]⚠️  {total_tests - total_passed} test(s) need attention.[/yellow]")


if __name__ == "__main__":
    main()
