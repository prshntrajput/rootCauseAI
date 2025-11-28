"""
React Error Parser
Handles React/JSX build and runtime errors
"""

import re
from typing import Optional
from .base_parser import BaseParser, ParsedError, StackFrame


class ReactParser(BaseParser):
    """
    Parser for React errors
    
    Supports:
    - React build errors (Webpack, Vite)
    - JSX syntax errors
    - Component errors
    - Hook errors
    """
    
    def can_parse(self, error_log: str) -> float:
        """Detect if this is a React error"""
        indicators = [
            (r'(jsx|tsx)', 0.2),
            (r'(React|Component|Hook)', 0.2),
            (r'(webpack|vite).*compiled', 0.2),
            (r'Module parse failed', 0.2),
            (r'SyntaxError:.*Unexpected token', 0.2),
        ]
        
        score = 0.0
        for pattern, weight in indicators:
            if re.search(pattern, error_log, re.IGNORECASE):
                score += weight
        
        return min(score, 1.0)
    
    def parse(self, error_log: str) -> ParsedError:
        """Parse React error"""
        frames = self._extract_errors(error_log)
        error_info = self._extract_error_info(error_log)
        
        language = "jsx" if ".jsx" in error_log else "tsx" if ".tsx" in error_log else "javascript"
        
        return ParsedError(
            language=language,
            framework="react",
            error_type=error_info['error_type'],
            message=error_info['message'],
            stack_frames=frames,
            severity="error",
            category=self._categorize_error(error_info['error_type'], error_log),
            confidence=0.88,
            raw_error=error_log[:500]
        )
    
    def _extract_errors(self, error_log: str) -> list[StackFrame]:
        """Extract error locations"""
        frames = []
        
        # Pattern: ./src/Component.jsx:10:5
        pattern = r'(\.?/[^\s:]+\.(jsx|tsx|js|ts)):(\d+):(\d+)'
        
        for line in error_log.split('\n'):
            match = re.search(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(3))
                column = int(match.group(4))
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    column=column
                ))
        
        return frames
    
    def _extract_error_info(self, error_log: str) -> dict:
        """Extract error type and message"""
        # Look for common React error patterns
        if 'Module parse failed' in error_log:
            return {
                'error_type': 'ModuleParseError',
                'message': 'Failed to parse module'
            }
        elif 'SyntaxError' in error_log:
            return {
                'error_type': 'SyntaxError',
                'message': 'JSX syntax error'
            }
        elif 'Cannot find module' in error_log:
            return {
                'error_type': 'ModuleNotFoundError',
                'message': 'Module not found'
            }
        else:
            return {
                'error_type': 'BuildError',
                'message': error_log.split('\n')[0][:200]
            }
    
    def _categorize_error(self, error_type: str, error_log: str) -> str:
        """Categorize React error"""
        if 'Syntax' in error_type:
            return "syntax"
        elif 'Module' in error_type:
            return "import"
        else:
            return "build"
