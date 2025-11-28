"""
TypeScript Error Parser
Handles TypeScript compiler errors (tsc)
"""

import re
from typing import Optional
from .base_parser import BaseParser, ParsedError, StackFrame


class TypeScriptParser(BaseParser):
    """
    Parser for TypeScript compiler errors
    
    Supports:
    - tsc compilation errors
    - Type mismatch errors
    - Interface/type errors
    """
    
    def can_parse(self, error_log: str) -> float:
        """Detect if this is a TypeScript error"""
        indicators = [
            (r'\.ts\(\d+,\d+\):', 0.4),
            (r'error TS\d+:', 0.4),
            (r'Type .+ is not assignable to type', 0.2),
        ]
        
        score = 0.0
        for pattern, weight in indicators:
            if re.search(pattern, error_log):
                score += weight
        
        return min(score, 1.0)
    
    def parse(self, error_log: str) -> ParsedError:
        """Parse TypeScript error"""
        frames = self._extract_errors(error_log)
        
        # Get first error for main info
        if frames:
            first_frame = frames[0]
            error_type = "TypeScriptError"
            message = first_frame.code_snippet or "Type error"
        else:
            error_type = "TypeScriptError"
            message = error_log[:200]
        
        return ParsedError(
            language="typescript",
            framework=None,
            error_type=error_type,
            message=message,
            stack_frames=frames,
            severity="error",
            category="type",
            confidence=0.92,
            raw_error=error_log[:500]
        )
    
    def _extract_errors(self, error_log: str) -> list[StackFrame]:
        """Extract TypeScript errors"""
        frames = []
        
        # Pattern: file.ts(line,col): error TS####: message
        pattern = r'([^\s]+\.tsx?)\((\d+),(\d+)\): error (TS\d+): (.+)'
        
        for line in error_log.split('\n'):
            match = re.search(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                column = int(match.group(3))
                error_code = match.group(4)
                message = match.group(5)
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    column=column,
                    function=None,
                    code_snippet=f"{error_code}: {message}"
                ))
        
        return frames
