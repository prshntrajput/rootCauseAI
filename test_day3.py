"""
Day 3 Comprehensive Test Suite
Tests context gathering system
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.parsers import ErrorClassifier
from backend.context import (
    FileReader,
    ImportAnalyzer,
    GitAnalyzer,
    ConfigDetector,
    TokenManager,
    ContextBuilder,
    CacheManager
)
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax


console = Console()


def test_file_reader():
    """Test 1: File reading with encoding detection"""
    console.print("\n[bold cyan]Test 1: File Reader[/bold cyan]")
    
    # Test reading test files
    test_files = [
        "backend/config.py",
        "backend/parsers/base_parser.py",
        "test_day2.py"
    ]
    
    results = []
    for file_path in test_files:
        if not Path(file_path).exists():
            results.append((file_path, "⚠️  Not found", 0))
            continue
        
        try:
            # Test encoding detection
            encoding = FileReader.detect_encoding(file_path)
            
            # Test reading file
            content = FileReader.read_file(file_path, end_line=10)
            
            # Test reading lines around
            context = FileReader.get_lines_around(file_path, target_line=5, context_lines=3)
            
            results.append((
                Path(file_path).name,
                "✅ Read",
                len(content)
            ))
            
        except Exception as e:
            results.append((file_path, f"❌ {str(e)[:30]}", 0))
    
    table = Table(title="File Reader Test Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Bytes Read", style="yellow")
    
    for name, status, size in results:
        table.add_row(name, status, str(size))
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results)


def test_import_analyzer():
    """Test 2: Import analysis"""
    console.print("\n[bold cyan]Test 2: Import Analyzer[/bold cyan]")
    
    results = []
    
    # Test Python imports
    py_file = "backend/parsers/classifier.py"
    if Path(py_file).exists():
        try:
            imports = ImportAnalyzer.get_python_imports(py_file)
            results.append(("Python imports", "✅ Found", len(imports)))
            
            # Show some imports
            if imports:
                console.print(f"   Found {len(imports)} imports: {', '.join(imports[:3])}...")
        except Exception as e:
            results.append(("Python imports", f"❌ {str(e)[:20]}", 0))
    
    # Test import chain
    if Path(py_file).exists():
        try:
            chain = ImportAnalyzer.build_import_chain(py_file, max_depth=1)
            results.append(("Import chain", "✅ Built", len(chain)))
            console.print(f"   Import chain size: {len(chain)} files")
        except Exception as e:
            results.append(("Import chain", f"❌ {str(e)[:20]}", 0))
    
    table = Table(title="Import Analyzer Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Count", style="yellow")
    
    for test, status, count in results:
        table.add_row(test, status, str(count))
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results)


def test_git_analyzer():
    """Test 3: Git analysis"""
    console.print("\n[bold cyan]Test 3: Git Analyzer[/bold cyan]")
    
    results = []
    
    # Test if git repo
    is_repo = GitAnalyzer.is_git_repo()
    results.append(("Git repo detection", "✅ Detected" if is_repo else "⚠️  Not a repo", 0))
    
    if is_repo:
        # Test getting recent changes
        test_file = "backend/config.py"
        if Path(test_file).exists():
            try:
                diff = GitAnalyzer.get_recent_changes(test_file)
                if diff:
                    results.append(("Git diff", "✅ Retrieved", len(diff)))
                    console.print(f"   Diff size: {len(diff)} chars")
                else:
                    results.append(("Git diff", "⚠️  No changes", 0))
            except Exception as e:
                results.append(("Git diff", f"❌ {str(e)[:20]}", 0))
        
        # Test recent commits
        if Path(test_file).exists():
            try:
                commits = GitAnalyzer.get_recent_commits(test_file, limit=3)
                results.append(("Recent commits", "✅ Found", len(commits)))
                
                if commits:
                    console.print(f"   Latest commit: {commits[0]['message'][:50]}...")
            except Exception as e:
                results.append(("Recent commits", f"❌ {str(e)[:20]}", 0))
    
    table = Table(title="Git Analyzer Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="yellow")
    
    for test, status, detail in results:
        table.add_row(test, status, str(detail) if detail else "N/A")
    
    console.print(table)
    
    passed = sum(1 for _, status, _ in results if "✅" in status)
    return passed, len(results) if results else 1


def test_config_detector():
    """Test 4: Config file detection"""
    console.print("\n[bold cyan]Test 4: Config Detector[/bold cyan]")
    
    # Find config files
    py_configs = ConfigDetector.find_config_files(language="python")
    js_configs = ConfigDetector.find_config_files(language="javascript")
    
    console.print(f"   Python configs found: {len(py_configs)}")
    for config in py_configs:
        console.print(f"      - {Path(config).name}")
    
    console.print(f"   JavaScript configs found: {len(js_configs)}")
    for config in js_configs:
        console.print(f"      - {Path(config).name}")
    
    # Detect framework
    framework = ConfigDetector.detect_framework()
    if framework:
        console.print(f"   Detected framework: [yellow]{framework}[/yellow]")
    
    passed = 1 if (py_configs or js_configs) else 0
    return passed, 1


def test_token_manager():
    """Test 5: Token budget management"""
    console.print("\n[bold cyan]Test 5: Token Manager[/bold cyan]")
    
    manager = TokenManager(max_tokens=1000)
    
    # Test adding text
    text1 = "a" * 300  # ~100 tokens
    text2 = "b" * 300  # ~100 tokens
    text3 = "c" * 3000  # ~1000 tokens (should exceed)
    
    added1 = manager.add(text1, "test1")
    added2 = manager.add(text2, "test2")
    added3 = manager.add(text3, "test3")
    
    summary = manager.get_summary()
    
    console.print(f"   Max tokens: {summary['max_tokens']}")
    console.print(f"   Used tokens: {summary['used_tokens']}")
    console.print(f"   Remaining: {summary['remaining_tokens']}")
    console.print(f"   Usage: {summary['usage_percentage']:.1f}%")
    console.print(f"   Items added: {summary['items_count']}")
    
    # Verify
    assert added1 == True, "Should add first text"
    assert added2 == True, "Should add second text"
    assert added3 == False, "Should reject third text (exceeds budget)"
    
    console.print("   ✅ All token management tests passed")
    
    return 1, 1


def test_context_builder():
    """Test 6: Context builder integration"""
    console.print("\n[bold cyan]Test 6: Context Builder (Full Integration)[/bold cyan]")
    
    # Create a sample error
    error_log = """Traceback (most recent call last):
  File "backend/parsers/classifier.py", line 42, in classify_and_parse
    parsed = best_parser.parse(error_log)
  File "backend/parsers/python_parser.py", line 28, in parse
    frames = self._extract_stack_frames(error_log)
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
    
    try:
        # Parse error
        classifier = ErrorClassifier()
        parsed_error = classifier.classify_and_parse(error_log)
        
        console.print(f"   ✅ Parsed error: {parsed_error.error_type}")
        
        # Build context
        builder = ContextBuilder(max_tokens=8000)
        context = builder.build(parsed_error)
        
        console.print(f"   ✅ Built context:")
        console.print(f"      - Primary files: {len(context.primary_files)}")
        console.print(f"      - Related files: {len(context.related_files)}")
        console.print(f"      - Config files: {len(context.config_files)}")
        console.print(f"      - Total tokens: {context.total_tokens}")
        console.print(f"      - Framework: {context.framework or 'None'}")
        
        # Show token usage
        token_summary = builder.get_token_summary()
        console.print(f"      - Token usage: {token_summary['usage_percentage']:.1f}%")
        
        # Verify we have context
        assert len(context.primary_files) > 0, "Should have primary files"
        
        # Show first file preview
        if context.primary_files:
            first_file = context.primary_files[0]
            console.print(f"\n   📄 Preview of {Path(first_file.file_path).name}:")
            preview = first_file.content[:200]
            console.print(f"      {preview}...")
        
        return 1, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        return 0, 1


def test_cache_manager():
    """Test 7: Cache management"""
    console.print("\n[bold cyan]Test 7: Cache Manager[/bold cyan]")
    
    cache = CacheManager(cache_dir=".test-cache")
    
    # Test setting cache
    test_key = "test_error_123"
    test_data = {"error": "test", "context": "sample"}
    
    cache.set(test_key, test_data)
    console.print("   ✅ Cache entry created")
    
    # Test getting cache
    retrieved = cache.get(test_key)
    if retrieved == test_data:
        console.print("   ✅ Cache retrieved successfully")
    else:
        console.print("   ❌ Cache retrieval failed")
    
    # Test stats
    stats = cache.get_cache_stats()
    console.print(f"   Cache stats:")
    console.print(f"      - Entries: {stats['total_entries']}")
    console.print(f"      - Size: {stats['total_size_bytes']} bytes")
    
    # Clear test cache
    cache.clear()
    console.print("   ✅ Cache cleared")
    
    return 1, 1


def test_full_workflow():
    """Test 8: Complete workflow with real error"""
    console.print("\n[bold cyan]Test 8: Complete Workflow Test[/bold cyan]")
    
    # Use a Python error from fixtures
    error_file = "tests/fixtures/python_errors/type_error.txt"
    
    if not Path(error_file).exists():
        console.print("   ⚠️  Test fixture not found, skipping")
        return 0, 1
    
    try:
        # Load error
        with open(error_file, 'r') as f:
            error_log = f.read()
        
        console.print("   📋 Step 1: Parse error")
        classifier = ErrorClassifier()
        parsed_error = classifier.classify_and_parse(error_log)
        console.print(f"      ✅ Detected: {parsed_error.language} - {parsed_error.error_type}")
        
        console.print("   📋 Step 2: Build context")
        builder = ContextBuilder(max_tokens=8000)
        context = builder.build(parsed_error)
        console.print(f"      ✅ Context built with {context.total_tokens} tokens")
        
        console.print("   📋 Step 3: Cache context")
        cache = CacheManager(cache_dir=".test-cache")
        cache_key = "workflow_test"
        cache.set(cache_key, context.dict())
        console.print(f"      ✅ Context cached")
        
        console.print("   📋 Step 4: Retrieve from cache")
        cached_data = cache.get(cache_key)
        if cached_data:
            console.print(f"      ✅ Retrieved from cache")
        
        # Cleanup
        cache.clear()
        
        console.print("\n   [bold green]✅ Complete workflow successful![/bold green]")
        
        return 1, 1
        
    except Exception as e:
        console.print(f"   ❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1


def main():
    """Run all Day 3 tests"""
    console.print(Panel.fit(
        "[bold green]Day 3: Intelligent Context Gathering Test Suite[/bold green]",
        border_style="green"
    ))
    
    all_results = []
    
    # Run all tests
    all_results.append(test_file_reader())
    all_results.append(test_import_analyzer())
    all_results.append(test_git_analyzer())
    all_results.append(test_config_detector())
    all_results.append(test_token_manager())
    all_results.append(test_context_builder())
    all_results.append(test_cache_manager())
    all_results.append(test_full_workflow())
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Day 3 Test Summary[/bold]")
    console.print("="*60)
    
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    
    console.print(f"\nTotal Tests: {total_tests}")
    console.print(f"Passed: [green]{total_passed}[/green]")
    console.print(f"Failed: [red]{total_tests - total_passed}[/red]")
    console.print(f"Success Rate: [bold]{(total_passed/total_tests*100):.1f}%[/bold]")
    
    if total_passed == total_tests:
        console.print("\n[bold green]🎉 All Day 3 tests passed! Ready for Day 4.[/bold green]")
        console.print("\n[yellow]Next: Day 4 - LangGraph Agent with Self-Reflection[/yellow]")
    else:
        console.print(f"\n[yellow]⚠️  {total_tests - total_passed} test(s) need attention.[/yellow]")


if __name__ == "__main__":
    main()
