"""
Test script for extension backend integration
"""

import requests
import json
from rich.console import Console

console = Console()

# Backend URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    console.print("\n[cyan]Test 1: Health Check[/cyan]")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"   ✅ Backend running: {data}")
            return True
        else:
            console.print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        console.print(f"   ❌ Cannot connect to backend: {e}")
        console.print(f"   💡 Start backend with: python backend/server.py")
        return False


def test_analyze():
    """Test error analysis"""
    console.print("\n[cyan]Test 2: Error Analysis[/cyan]")
    
    error_log = """Traceback (most recent call last):
  File "test.py", line 5, in main
    result = x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze",
            json={
                "error_log": error_log,
                "project_root": ".",
                "provider": "gemini",
                "max_retries": 2
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"   ✅ Analysis complete")
            console.print(f"      Status: {data['status']}")
            console.print(f"      Fixes: {len(data.get('fixes', []))}")
            console.print(f"      Time: {data['execution_time']:.2f}s")
            console.print(f"      Tokens: {data['tokens_used']}")
            
            if data.get('fixes'):
                console.print(f"\n   First fix:")
                fix = data['fixes'][0]
                console.print(f"      File: {fix['file_path']}")
                console.print(f"      Confidence: {fix['confidence']:.0%}")
            
            return True
        else:
            console.print(f"   ❌ Analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return False


def test_history():
    """Test history endpoint"""
    console.print("\n[cyan]Test 3: History Endpoint[/cyan]")
    
    try:
        response = requests.get(f"{BASE_URL}/history?count=5")
        
        if response.status_code == 200:
            data = response.json()
            console.print(f"   ✅ History retrieved: {data['total']} fixes")
            return True
        else:
            console.print(f"   ❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return False


def test_stats():
    """Test stats endpoint"""
    console.print("\n[cyan]Test 4: Statistics Endpoint[/cyan]")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            console.print(f"   ✅ Stats retrieved:")
            console.print(f"      Total fixes: {stats['total_fixes']}")
            console.print(f"      Active: {stats['active_fixes']}")
            console.print(f"      Reverted: {stats['reverted_count']}")
            console.print(f"      Files modified: {stats['files_modified']}")
            return True
        else:
            console.print(f"   ❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        console.print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    console.print("[bold green]rootCauseAI Backend Integration Tests[/bold green]")
    console.print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    
    if results[0][1]:  # Only continue if backend is running
        results.append(("Error Analysis", test_analyze()))
        results.append(("History", test_history()))
        results.append(("Statistics", test_stats()))
    
    # Summary
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        console.print(f"{status} {name}")
    
    console.print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        console.print("\n[bold green]🎉 All backend tests passed![/bold green]")
    else:
        console.print("\n[yellow]⚠️  Some tests failed[/yellow]")


if __name__ == "__main__":
    main()
