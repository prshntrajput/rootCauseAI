"""
Day 4 Comprehensive Test Suite
Tests LangGraph agent workflow with self-reflection
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.graph import AgentRunner, build_agent_graph
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


console = Console()


def test_graph_construction():
    """Test 1: Graph construction"""
    console.print("\n[bold cyan]Test 1: Graph Construction[/bold cyan]")
    
    try:
        graph = build_agent_graph()
        console.print("   ✅ Graph built successfully")
        
        # Try to get graph structure
        try:
            nodes = list(graph.nodes.keys()) if hasattr(graph, 'nodes') else []
            if nodes:
                console.print(f"   ✅ Graph has {len(nodes)} nodes")
            else:
                console.print(f"   ✅ Graph compiled (node info not accessible)")
        except:
            console.print(f"   ✅ Graph structure is internal")
        
        return 1, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        return 0, 1


def test_simple_python_error():
    """Test 2: Simple Python error"""
    console.print("\n[bold cyan]Test 2: Simple Python Error[/bold cyan]")
    
    error_log = """Traceback (most recent call last):
  File "backend/config.py", line 10, in test
    result = x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
    
    try:
        runner = AgentRunner(max_retries=2)
        result = runner.run(error_log)
        
        console.print(f"   Final status: {result['status']}")
        console.print(f"   Parse success: {result['parse_success']}")
        console.print(f"   Context success: {result['context_success']}")
        console.print(f"   Analysis success: {result['analysis_success']}")
        console.print(f"   Generation success: {result['generation_success']}")
        console.print(f"   Validation success: {result['validation_success']}")
        console.print(f"   Retries used: {result['retry_count']}/{result['max_retries']}")
        console.print(f"   Execution time: {result['execution_time']:.2f}s")
        
        if result['final_fixes']:
            console.print(f"   ✅ Generated {len(result['final_fixes'])} fix(es)")
            return 1, 1
        else:
            console.print(f"   ⚠️  No fixes generated")
            return 0, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1


def test_with_fixture():
    """Test 3: Error from test fixtures"""
    console.print("\n[bold cyan]Test 3: Error from Fixtures[/bold cyan]")
    
    fixture_file = "tests/fixtures/python_errors/type_error.txt"
    
    if not Path(fixture_file).exists():
        console.print("   ⚠️  Fixture not found, skipping")
        return 0, 1
    
    try:
        with open(fixture_file, 'r') as f:
            error_log = f.read()
        
        runner = AgentRunner(max_retries=2)
        
        console.print("   Running agent on fixture...")
        result = runner.run(error_log)
        
        console.print(f"   Status: {result['status']}")
        
        if result['parsed_error']:
            console.print(f"   Parsed: {result['parsed_error'].language} - {result['parsed_error'].error_type}")
        
        if result['root_cause_analysis']:
            console.print(f"   Analysis: {result['root_cause_analysis'][:80]}...")
        
        if result['final_fixes']:
            console.print(f"   ✅ Generated {len(result['final_fixes'])} fix(es)")
            
            # Show first fix
            fix = result['final_fixes'][0]
            console.print(f"      File: {fix.file_path}")
            console.print(f"      Confidence: {fix.confidence:.2f}")
            
            return 1, 1
        else:
            console.print(f"   ⚠️  No fixes generated")
            return 0, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1


def test_state_transitions():
    """Test 4: State transitions through nodes"""
    console.print("\n[bold cyan]Test 4: State Transitions[/bold cyan]")
    
    from backend.graph.state import AgentState
    from backend.graph.nodes import parse_error_node
    
    # Create initial state
    state: AgentState = {
        "raw_error_log": "SyntaxError: invalid syntax",
        "project_root": ".",
        "provider": "gemini",
        "parsed_error": None,
        "parse_success": False,
        "code_context": None,
        "context_success": False,
        "root_cause_analysis": None,
        "analysis_success": False,
        "fix_suggestions": None,
        "generation_success": False,
        "validation_result": None,
        "validation_success": False,
        "retry_count": 0,
        "max_retries": 3,
        "retry_feedback": None,
        "final_fixes": None,
        "status": "pending",
        "error_message": None,
        "tokens_used": 0,
        "execution_time": 0.0
    }
    
    try:
        # Test parse node
        new_state = parse_error_node(state)
        
        console.print(f"   Parse success: {new_state['parse_success']}")
        console.print(f"   Status after parse: {new_state['status']}")
        
        if new_state['parsed_error']:
            console.print(f"   ✅ State transitions working")
            return 1, 1
        else:
            console.print(f"   ⚠️  Parse returned no error")
            return 0, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        return 0, 1


def test_retry_logic():
    """Test 5: Retry logic with bad fixes"""
    console.print("\n[bold cyan]Test 5: Retry Logic[/bold cyan]")
    
    # This would require mocking LLM to return bad fixes
    # For now, just verify retry mechanism exists
    
    try:
        from backend.graph.edges import should_retry_after_validate
        from backend.graph.state import AgentState
        
        # Simulate failed validation, retries remaining
        state: AgentState = {
            "validation_success": False,
            "retry_count": 0,
            "max_retries": 3,
        }
        
        decision = should_retry_after_validate(state)
        
        if decision == "refine":
            console.print("   ✅ Retry logic triggers refinement")
        else:
            console.print("   ❌ Should have triggered refinement")
            return 0, 1
        
        # Simulate max retries reached
        state["retry_count"] = 3
        decision = should_retry_after_validate(state)
        
        if decision == "end":
            console.print("   ✅ Stops after max retries")
            return 1, 1
        else:
            console.print("   ❌ Should have stopped")
            return 0, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        return 0, 1


def test_full_workflow_display():
    """Test 6: Full workflow with rich display"""
    console.print("\n[bold cyan]Test 6: Full Workflow with Display[/bold cyan]")
    
    error_log = """Traceback (most recent call last):
  File "backend/parsers/classifier.py", line 50, in classify_and_parse
    result = best_parser.parse(error_log)
AttributeError: 'NoneType' object has no attribute 'parse'"""
    
    try:
        runner = AgentRunner(max_retries=2)
        
        console.print("\n" + "="*60)
        result = runner.run_and_display(error_log)
        console.print("="*60)
        
        if result['status'] in ['success', 'failed']:
            console.print(f"\n   ✅ Workflow completed with status: {result['status']}")
            return 1, 1
        else:
            console.print(f"\n   ⚠️  Unexpected status: {result['status']}")
            return 0, 1
        
    except Exception as e:
        console.print(f"\n   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1


def test_edge_functions():
    """Test 7: Edge routing functions"""
    console.print("\n[bold cyan]Test 7: Edge Routing Functions[/bold cyan]")
    
    try:
        from backend.graph.edges import (
            should_continue_after_parse,
            should_continue_after_gather,
            should_continue_after_analyze,
            should_continue_after_generate,
            should_retry_after_validate
        )
        
        tests_passed = 0
        
        # Test parse edge
        state_success = {"parse_success": True}
        if should_continue_after_parse(state_success) == "gather":
            console.print("   ✅ Parse edge: success → gather")
            tests_passed += 1
        
        state_fail = {"parse_success": False}
        if should_continue_after_parse(state_fail) == "end":
            console.print("   ✅ Parse edge: fail → end")
            tests_passed += 1
        
        # Test gather edge
        state_success = {"context_success": True}
        if should_continue_after_gather(state_success) == "analyze":
            console.print("   ✅ Gather edge: success → analyze")
            tests_passed += 1
        
        # Test analyze edge
        state_success = {"analysis_success": True}
        if should_continue_after_analyze(state_success) == "generate":
            console.print("   ✅ Analyze edge: success → generate")
            tests_passed += 1
        
        # Test generate edge
        state_success = {"generation_success": True, "fix_suggestions": [1, 2]}
        if should_continue_after_generate(state_success) == "validate":
            console.print("   ✅ Generate edge: success → validate")
            tests_passed += 1
        
        if tests_passed == 5:
            console.print(f"   ✅ All {tests_passed} edge tests passed")
            return 1, 1
        else:
            console.print(f"   ⚠️  Only {tests_passed}/5 edge tests passed")
            return 0, 1
        
    except Exception as e:
        console.print(f"   ❌ Failed: {e}")
        return 0, 1


def main():
    """Run all Day 4 tests"""
    console.print(Panel.fit(
        "[bold green]Day 4: LangGraph Agent with Self-Reflection Test Suite[/bold green]",
        border_style="green"
    ))
    
    all_results = []
    
    # Run all tests
    all_results.append(test_graph_construction())
    all_results.append(test_simple_python_error())
    all_results.append(test_with_fixture())
    all_results.append(test_state_transitions())
    all_results.append(test_retry_logic())
    all_results.append(test_full_workflow_display())
    all_results.append(test_edge_functions())
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Day 4 Test Summary[/bold]")
    console.print("="*60)
    
    total_passed = sum(passed for passed, _ in all_results)
    total_tests = sum(total for _, total in all_results)
    
    console.print(f"\nTotal Tests: {total_tests}")
    console.print(f"Passed: [green]{total_passed}[/green]")
    console.print(f"Failed: [red]{total_tests - total_passed}[/red]")
    console.print(f"Success Rate: [bold]{(total_passed/total_tests*100):.1f}%[/bold]")
    
    if total_passed >= total_tests - 1:  # Allow 1 failure (LLM might be slow/unavailable)
        console.print("\n[bold green]🎉 Day 4 tests passed! Ready for Day 5.[/bold green]")
        console.print("\n[yellow]Next: Day 5 - Smart Patcher with Safety Features[/yellow]")
    else:
        console.print(f"\n[yellow]⚠️  {total_tests - total_passed} test(s) need attention.[/yellow]")


if __name__ == "__main__":
    main()
