"""
Day 5 Comprehensive Test Suite
Tests smart patcher with safety features
"""

import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent))

from backend.patcher import (
    FuzzyMatcher,
    CodeValidator,
    BackupManager,
    HistoryTracker,
    PatchApplier,
    SmartPatcher
)
from backend.graph.state import FixSuggestion
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def test_fuzzy_matcher():
    """Test 1: Fuzzy code matching"""
    console.print("\n[bold cyan]Test 1: Fuzzy Matcher[/bold cyan]")
    
    matcher = FuzzyMatcher()
    
    # Test normalization
    code1 = "  def hello():\n    print('hi')\n"
    code2 = "def hello():\n  print('hi')"
    
    norm1 = matcher.normalize_whitespace(code1)
    norm2 = matcher.normalize_whitespace(code2)
    
    console.print(f"   Normalized comparison: {norm1 == norm2}")
    
    # Test similarity
    similarity = matcher.similarity_ratio(code1, code2)
    console.print(f"   Similarity: {similarity:.2f}")
    
    # Test matching in file
    file_content = """
def main():
    x = 5
    y = 10
    result = x + y
    print(result)
"""
    
    target = "    result = x + y"
    match = matcher.find_best_match(target, file_content, threshold=0.7)
    
    if match:
        start, end, sim = match
        console.print(f"   ✅ Found match at lines {start}-{end} ({sim:.0%} similar)")
        return 1, 1
    else:
        console.print(f"   ❌ No match found")
        return 0, 1


def test_code_validator():
    """Test 2: Code validation"""
    console.print("\n[bold cyan]Test 2: Code Validator[/bold cyan]")
    
    validator = CodeValidator()
    
    tests_passed = 0
    
    # Test valid Python
    valid_python = "def hello():\n    print('world')"
    is_valid, error = validator.validate_python(valid_python)
    if is_valid:
        console.print("   ✅ Valid Python code accepted")
        tests_passed += 1
    else:
        console.print(f"   ❌ Valid Python rejected: {error}")
    
    # Test invalid Python
    invalid_python = "def hello(\n    print('world')"
    is_valid, error = validator.validate_python(invalid_python)
    if not is_valid:
        console.print("   ✅ Invalid Python rejected")
        tests_passed += 1
    else:
        console.print("   ❌ Invalid Python accepted")
    
    # Test complete snippets
    snippet = "x = 5 + 3"
    is_valid, error = validator.validate_python(snippet)
    if is_valid:
        console.print("   ✅ Simple statement validated")
        tests_passed += 1
    else:
        console.print(f"   ❌ Simple statement failed: {error}")
    
    console.print(f"\n   Passed {tests_passed}/3 validation tests")
    return tests_passed == 3, 1


def test_backup_manager():
    """Test 3: Backup management"""
    console.print("\n[bold cyan]Test 3: Backup Manager[/bold cyan]")
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("original content")
        
        backup_dir = Path(temp_dir) / ".backups"
        manager = BackupManager(str(backup_dir))
        
        # Test backup creation
        backup_path = manager.create_backup(str(test_file))
        
        if Path(backup_path).exists():
            console.print(f"   ✅ Backup created: {Path(backup_path).name}")
        else:
            console.print("   ❌ Backup creation failed")
            return 0, 1
        
        # Modify original file
        test_file.write_text("modified content")
        
        # Test restore
        success = manager.restore_backup(backup_path, str(test_file))
        
        if success and test_file.read_text() == "original content":
            console.print("   ✅ Backup restored successfully")
        else:
            console.print("   ❌ Restore failed")
            return 0, 1
        
        # Test listing backups
        backups = manager.list_backups(str(test_file))
        
        if len(backups) >= 1:
            console.print(f"   ✅ Found {len(backups)} backup(s)")
            return 1, 1
        else:
            console.print("   ❌ Backup listing failed")
            return 0, 1


def test_history_tracker():
    """Test 4: History tracking"""
    console.print("\n[bold cyan]Test 4: History Tracker[/bold cyan]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        history_file = Path(temp_dir) / "history.json"
        tracker = HistoryTracker(str(history_file))
        
        # Add a fix
        fix_id = tracker.add_fix(
            file_path="test.py",
            original_snippet="x = 1",
            new_snippet="x = 2",
            backup_path="/tmp/backup.py"
        )
        
        console.print(f"   ✅ Fix added: {fix_id}")
        
        # Retrieve fix
        fix = tracker.get_fix(fix_id)
        
        if fix and fix["new_snippet"] == "x = 2":
            console.print("   ✅ Fix retrieved correctly")
        else:
            console.print("   ❌ Fix retrieval failed")
            return 0, 1
        
        # Get stats
        stats = tracker.get_stats()
        
        if stats["total_fixes"] == 1:
            console.print(f"   ✅ Stats: {stats['total_fixes']} fix(es)")
        else:
            console.print("   ❌ Stats incorrect")
            return 0, 1
        
        # Mark as reverted
        tracker.mark_reverted(fix_id)
        stats = tracker.get_stats()
        
        if stats["reverted_count"] == 1:
            console.print("   ✅ Revert tracking works")
            return 1, 1
        else:
            console.print("   ❌ Revert tracking failed")
            return 0, 1


def test_patch_applier():
    """Test 5: Patch application"""
    console.print("\n[bold cyan]Test 5: Patch Applier[/bold cyan]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        test_file = Path(temp_dir) / "test.py"
        test_file.write_text("""def calculate():
    x = 5
    y = "10"
    result = x + y
    return result
""")
        
        backup_dir = Path(temp_dir) / ".backups"
        history_file = Path(temp_dir) / "history.json"
        
        applier = PatchApplier(str(backup_dir), str(history_file))
        
        # Apply a fix
        success, message = applier.apply_patch(
            file_path=str(test_file),
            original_snippet='    result = x + y',
            new_snippet='    result = x + int(y)',
            language="python",
            dry_run=False
        )
        
        if success:
            console.print(f"   ✅ Patch applied: {message}")
        else:
            console.print(f"   ❌ Patch failed: {message}")
            return 0, 1
        
        # Verify file was modified
        content = test_file.read_text()
        
        if "int(y)" in content:
            console.print("   ✅ File modified correctly")
        else:
            console.print("   ❌ File not modified")
            return 0, 1
        
        # Test undo
        success, message = applier.undo_last_fix()
        
        if success:
            console.print(f"   ✅ Undo successful: {message}")
        else:
            console.print(f"   ❌ Undo failed: {message}")
            return 0, 1
        
        # Verify file was restored
        content = test_file.read_text()
        
        if "x + y" in content and "int(y)" not in content:
            console.print("   ✅ File restored correctly")
            return 1, 1
        else:
            console.print("   ❌ File not restored")
            return 0, 1


def test_dry_run():
    """Test 6: Dry run mode"""
    console.print("\n[bold cyan]Test 6: Dry Run Mode[/bold cyan]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.py"
        original_content = "x = 5 + 10"
        test_file.write_text(original_content)
        
        backup_dir = Path(temp_dir) / ".backups"
        history_file = Path(temp_dir) / "history.json"
        
        applier = PatchApplier(str(backup_dir), str(history_file))
        
        # Dry run
        success, message = applier.apply_patch(
            file_path=str(test_file),
            original_snippet="x = 5 + 10",
            new_snippet="x = 5 + int('10')",
            language="python",
            dry_run=True
        )
        
        if success:
            console.print(f"   ✅ Dry run passed: {message}")
        else:
            console.print(f"   ❌ Dry run failed: {message}")
            return 0, 1
        
        # Verify file was NOT modified
        if test_file.read_text() == original_content:
            console.print("   ✅ File not modified (as expected)")
            return 1, 1
        else:
            console.print("   ❌ File was modified (should not happen)")
            return 0, 1


def test_smart_patcher():
    """Test 7: Smart Patcher integration"""
    console.print("\n[bold cyan]Test 7: Smart Patcher (Full Integration)[/bold cyan]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "example.py"
        test_file.write_text("""def process_data():
    count = "5"
    total = count + 10
    return total
""")
        
        backup_dir = Path(temp_dir) / ".backups"
        history_file = Path(temp_dir) / "history.json"
        
        patcher = SmartPatcher(str(backup_dir), str(history_file))
        
        # Create fix suggestion
        fix = FixSuggestion(
            file_path=str(test_file),
            original_snippet='    total = count + 10',
            new_snippet='    total = int(count) + 10',
            explanation="Convert string to int before addition",
            confidence=0.95,
            line_number=3
        )
        
        # Apply fix (non-interactive)
        results = patcher.apply_fixes(
            fixes=[fix],
            language="python",
            dry_run=False,
            interactive=False
        )
        
        if results["applied"] == 1:
            console.print(f"   ✅ Fix applied via SmartPatcher")
        else:
            console.print(f"   ❌ Fix not applied")
            return 0, 1
        
        # Check history
        patcher.show_history(count=5)
        
        # Check stats
        patcher.show_stats()
        
        console.print("\n   ✅ SmartPatcher integration successful")
        return 1, 1


def test_multiple_fixes():
    """Test 8: Multiple fixes in one file"""
    console.print("\n[bold cyan]Test 8: Multiple Fixes[/bold cyan]")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "multi.py"
        test_file.write_text("""def process():
    x = "5"
    y = "10"
    result1 = x + 1
    result2 = y + 2
    return result1, result2
""")
        
        backup_dir = Path(temp_dir) / ".backups"
        history_file = Path(temp_dir) / "history.json"
        
        patcher = SmartPatcher(str(backup_dir), str(history_file))
        
        fixes = [
            FixSuggestion(
                file_path=str(test_file),
                original_snippet='    result1 = x + 1',
                new_snippet='    result1 = int(x) + 1',
                explanation="Fix type error",
                confidence=0.90
            ),
            FixSuggestion(
                file_path=str(test_file),
                original_snippet='    result2 = y + 2',
                new_snippet='    result2 = int(y) + 2',
                explanation="Fix type error",
                confidence=0.90
            )
        ]
        
        results = patcher.apply_fixes(
            fixes=fixes,
            language="python",
            dry_run=False,
            interactive=False
        )
        
        if results["applied"] == 2:
            console.print(f"   ✅ Applied {results['applied']} fixes")
            return 1, 1
        else:
            console.print(f"   ⚠️  Applied {results['applied']}/2 fixes")
            return 0, 1


def main():
    """Run all Day 5 tests"""
    console.print(Panel.fit(
        "[bold green]Day 5: Smart Patcher with Safety Features Test Suite[/bold green]",
        border_style="green"
    ))
    
    all_results = []
    
    # Run all tests
    all_results.append(test_fuzzy_matcher())
    all_results.append(test_code_validator())
    all_results.append(test_backup_manager())
    all_results.append(test_history_tracker())
    all_results.append(test_patch_applier())
    all_results.append(test_dry_run())
    all_results.append(test_smart_patcher())
    all_results.append(test_multiple_fixes())
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Day 5 Test Summary[/bold]")
    console.print("="*60)
    
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    
    console.print(f"\nTotal Tests: {total_tests}")
    console.print(f"Passed: [green]{total_passed}[/green]")
    console.print(f"Failed: [red]{total_tests - total_passed}[/red]")
    console.print(f"Success Rate: [bold]{(total_passed/total_tests*100):.1f}%[/bold]")
    
    if total_passed == total_tests:
        console.print("\n[bold green]🎉 All Day 5 tests passed! Ready for Day 6.[/bold green]")
        console.print("\n[yellow]Next: Day 6 - VSCode Extension (Primary Interface)[/yellow]")
    else:
        console.print(f"\n[yellow]⚠️  {total_tests - total_passed} test(s) need attention.[/yellow]")


if __name__ == "__main__":
    main()
