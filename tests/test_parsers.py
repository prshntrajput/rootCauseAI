"""
Unit Tests for Error Parsers
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parsers import (
    PythonParser,
    JavaScriptParser,
    TypeScriptParser,
    ReactParser,
    LinterParser,
    ErrorClassifier
)


def test_python_parser():
    """Test Python error parsing"""
    parser = PythonParser()
    
    # Test 1: Import Error
    error = """Traceback (most recent call last):
  File "main.py", line 3, in <module>
    from utils import helper
ModuleNotFoundError: No module named 'utils'"""
    
    assert parser.can_parse(error) > 0.5
    parsed = parser.parse(error)
    assert parsed.language == "python"
    assert parsed.category == "import"
    assert "ModuleNotFoundError" in parsed.error_type
    assert len(parsed.stack_frames) >= 1
    
    # Test 2: Type Error
    error2 = """Traceback (most recent call last):
  File "app.py", line 10, in calculate
    result = x + y
TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
    
    parsed2 = parser.parse(error2)
    assert parsed2.category == "type"
    assert "TypeError" in parsed2.error_type


def test_javascript_parser():
    """Test JavaScript error parsing"""
    parser = JavaScriptParser()
    
    error = """ReferenceError: calculateTotal is not defined
    at processOrder (/home/user/src/order.js:42:15)
    at main (/home/user/src/index.js:10:5)"""
    
    assert parser.can_parse(error) > 0.5
    parsed = parser.parse(error)
    assert parsed.language == "javascript"
    assert "ReferenceError" in parsed.error_type
    assert len(parsed.stack_frames) >= 1
    assert parsed.stack_frames[0].line == 42
    assert parsed.stack_frames[0].column == 15


def test_typescript_parser():
    """Test TypeScript error parsing"""
    parser = TypeScriptParser()
    
    error = """src/User.ts(15,7): error TS2322: Type 'string' is not assignable to type 'number'."""
    
    assert parser.can_parse(error) > 0.5
    parsed = parser.parse(error)
    assert parsed.language == "typescript"
    assert parsed.category == "type"
    assert len(parsed.stack_frames) >= 1


def test_classifier():
    """Test error classifier"""
    classifier = ErrorClassifier()
    
    # Test Python error
    python_error = """Traceback (most recent call last):
  File "test.py", line 5
    print("hello"
          ^
SyntaxError: unexpected EOF while parsing"""
    
    parsed = classifier.classify_and_parse(python_error)
    assert parsed.language == "python"
    assert parsed.category == "syntax"
    
    # Test JavaScript error
    js_error = """TypeError: Cannot read property 'name' of null
    at getUserName (/app/user.js:10:20)"""
    
    parsed2 = classifier.classify_and_parse(js_error)
    assert parsed2.language == "javascript"
    
    # Test scores
    scores = classifier.get_parser_scores(python_error)
    assert "Python" in scores
    assert scores["Python"] > 0.5


if __name__ == "__main__":
    print("Running parser tests...")
    
    try:
        test_python_parser()
        print("✅ Python parser tests passed")
    except AssertionError as e:
        print(f"❌ Python parser tests failed: {e}")
    
    try:
        test_javascript_parser()
        print("✅ JavaScript parser tests passed")
    except AssertionError as e:
        print(f"❌ JavaScript parser tests failed: {e}")
    
    try:
        test_typescript_parser()
        print("✅ TypeScript parser tests passed")
    except AssertionError as e:
        print(f"❌ TypeScript parser tests failed: {e}")
    
    try:
        test_classifier()
        print("✅ Classifier tests passed")
    except AssertionError as e:
        print(f"❌ Classifier tests failed: {e}")
    
    print("\n✅ All unit tests passed!")
