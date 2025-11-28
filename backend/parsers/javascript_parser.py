"""
JavaScript/Node.js Error Parser
Handles JavaScript and Node.js runtime errors
"""

import re
from typing import Optional
from .base_parser import BaseParser, ParsedError, StackFrame


class JavaScriptParser(BaseParser):
    """
    Parser for JavaScript and Node.js errors
    
    Supports:
    - Node.js stack traces
    - Browser console errors
    - Runtime errors (TypeError, ReferenceError, etc.)
    - Async/Promise errors
    """
    
    def can_parse(self, error_log: str) -> float:
        """Detect if this is a JavaScript/Node.js error"""
        indicators = [
            (r'(TypeError|ReferenceError|SyntaxError|RangeError):', 0.3),
            (r'at .+\(.*\.js:\d+:\d+\)', 0.3),
            (r'at .*\.js:\d+:\d+', 0.2),
            (r'node:internal|node_modules', 0.2),
        ]
        
        score = 0.0
        for pattern, weight in indicators:
            if re.search(pattern, error_log):
                score += weight
        
        return min(score, 1.0)
    
    def parse(self, error_log: str) -> ParsedError:
        """Parse JavaScript error"""
        frames = self._extract_stack_frames(error_log)
        error_info = self._extract_error_info(error_log)
        category = self._categorize_error(error_info['error_type'])
        framework = self._detect_framework(error_log)
        
        return ParsedError(
            language="javascript",
            framework=framework,
            error_type=error_info['error_type'],
            message=error_info['message'],
            stack_frames=frames,
            severity="error",
            category=category,
            confidence=0.90,
            raw_error=error_log[:500]
        )
    
    def _extract_stack_frames(self, error_log: str) -> list[StackFrame]:
        """Extract stack frames from JavaScript error"""
        frames = []
        
        # Pattern 1: at functionName (file.js:10:5)
        pattern1 = r'at\s+(?:(.+?)\s+)?\(([^)]+):(\d+):(\d+)\)'
        
        # Pattern 2: at file.js:10:5
        pattern2 = r'at\s+([^(]+):(\d+):(\d+)'
        
        for line in error_log.split('\n'):
            # Try pattern 1 first
            match = re.search(pattern1, line)
            if match:
                function = match.group(1) or 'anonymous'
                file_path = match.group(2)
                line_num = int(match.group(3))
                column = int(match.group(4))
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    column=column,
                    function=function
                ))
                continue
            
            # Try pattern 2
            match = re.search(pattern2, line)
            if match:
                file_path = match.group(1).strip()
                line_num = int(match.group(2))
                column = int(match.group(3))
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    column=column
                ))
        
        return frames
    
    def _extract_error_info(self, error_log: str) -> dict:
        """Extract error type and message"""
        # Pattern: ErrorType: message
        error_pattern = r'^(\w+Error): (.+?)$'
        
        for line in error_log.split('\n'):
            match = re.match(error_pattern, line.strip())
            if match:
                return {
                    'error_type': match.group(1),
                    'message': match.group(2).strip()
                }
        
        return {
            'error_type': 'JavaScriptError',
            'message': error_log.split('\n')[0][:200]
        }
    
    def _categorize_error(self, error_type: str) -> str:
        """Categorize JavaScript error"""
        if 'SyntaxError' in error_type:
            return "syntax"
        elif 'TypeError' in error_type or 'ReferenceError' in error_type:
            return "type"
        elif 'RangeError' in error_type:
            return "runtime"
        else:
            return "runtime"
    
    def _detect_framework(self, error_log: str) -> Optional[str]:
        """Detect JavaScript framework"""
        frameworks = {
            'express': r'express[/\\]',
            'react': r'react-dom|react[/\\]',
            'vue': r'vue[/\\]',
            'next': r'next[/\\]',
            'nest': r'@nestjs',
        }
        
        for framework, pattern in frameworks.items():
            if re.search(pattern, error_log, re.IGNORECASE):
                return framework
        
        return None
