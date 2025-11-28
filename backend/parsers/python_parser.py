"""
Python Error Parser
Handles Python tracebacks and exceptions
"""

import re
from typing import Optional
from .base_parser import BaseParser, ParsedError, StackFrame


class PythonParser(BaseParser):
    """
    Parser for Python tracebacks and exceptions
    
    Supports:
    - Standard tracebacks
    - Syntax errors
    - Import errors
    - Runtime exceptions
    - Framework-specific errors (Django, Flask, FastAPI)
    """
    
    def can_parse(self, error_log: str) -> float:
        """Detect if this is a Python error"""
        indicators = [
            (r'Traceback \(most recent call last\)', 0.4),
            (r'File ".*\.py", line \d+', 0.3),
            (r'(Error|Exception):', 0.2),
            (r'(raise|def|class|import)\s+', 0.1),
        ]
        
        score = 0.0
        for pattern, weight in indicators:
            if re.search(pattern, error_log):
                score += weight
        
        return min(score, 1.0)
    
    def parse(self, error_log: str) -> ParsedError:
        """Parse Python traceback"""
        frames = self._extract_stack_frames(error_log)
        error_info = self._extract_error_info(error_log)
        category = self._categorize_error(error_info['error_type'], error_log)
        framework = self._detect_framework(error_log)
        
        return ParsedError(
            language="python",
            framework=framework,
            error_type=error_info['error_type'],
            message=error_info['message'],
            stack_frames=frames,
            severity="error",
            category=category,
            confidence=0.95,
            raw_error=error_log[:500]  # Keep first 500 chars
        )
    
    def _extract_stack_frames(self, error_log: str) -> list[StackFrame]:
        """Extract stack frames from traceback"""
        frames = []
        
        # Pattern: File "path/file.py", line 42, in function_name
        frame_pattern = r'File "([^"]+)", line (\d+)(?:, in (.+))?'
        
        # Also capture the code snippet (next line after File line)
        lines = error_log.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(frame_pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                function = match.group(3).strip() if match.group(3) else None
                
                # Try to get code snippet (usually on next line)
                code_snippet = None
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith('File'):
                        code_snippet = next_line
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    function=function,
                    code_snippet=code_snippet
                ))
        
        return frames
    
    def _extract_error_info(self, error_log: str) -> dict:
        """Extract error type and message"""
        # Pattern: ErrorType: error message
        error_pattern = r'(\w+(?:Error|Exception|Warning)): (.+?)(?:\n|$)'
        
        match = re.search(error_pattern, error_log)
        if match:
            return {
                'error_type': match.group(1),
                'message': match.group(2).strip()
            }
        
        # Fallback: try to get last non-empty line
        lines = [l.strip() for l in error_log.split('\n') if l.strip()]
        if lines:
            last_line = lines[-1]
            if ':' in last_line:
                parts = last_line.split(':', 1)
                return {
                    'error_type': parts[0].strip(),
                    'message': parts[1].strip()
                }
        
        return {
            'error_type': 'UnknownError',
            'message': error_log.split('\n')[-1][:200]
        }
    
    def _categorize_error(self, error_type: str, error_log: str) -> str:
        """Categorize the error"""
        syntax_errors = ['SyntaxError', 'IndentationError', 'TabError']
        import_errors = ['ImportError', 'ModuleNotFoundError']
        type_errors = ['TypeError', 'AttributeError', 'NameError']
        
        if error_type in syntax_errors:
            return "syntax"
        elif error_type in import_errors:
            return "import"
        elif error_type in type_errors:
            return "type"
        else:
            return "runtime"
    
    def _detect_framework(self, error_log: str) -> Optional[str]:
        """Detect Python framework from traceback"""
        frameworks = {
            'django': r'django[/\\]',
            'flask': r'flask[/\\]',
            'fastapi': r'fastapi[/\\]',
            'pytest': r'pytest|_pytest',
            'sqlalchemy': r'sqlalchemy[/\\]',
        }
        
        for framework, pattern in frameworks.items():
            if re.search(pattern, error_log, re.IGNORECASE):
                return framework
        
        return None
