"""
Linter Error Parser
Handles ESLint, Prettier, and other linting errors
"""

import re
from .base_parser import BaseParser, ParsedError, StackFrame


class LinterParser(BaseParser):
    """
    Parser for linting errors (ESLint, Prettier, etc.)
    """
    
    def can_parse(self, error_log: str) -> float:
        """Detect if this is a linting error"""
        indicators = [
            (r'eslint', 0.4),
            (r'prettier', 0.4),
            (r'\d+:\d+\s+(error|warning)', 0.2),
        ]
        
        score = 0.0
        for pattern, weight in indicators:
            if re.search(pattern, error_log, re.IGNORECASE):
                score += weight
        
        return min(score, 1.0)
    
    def parse(self, error_log: str) -> ParsedError:
        """Parse linting error"""
        frames = self._extract_lint_errors(error_log)
        
        return ParsedError(
            language="javascript",
            framework=None,
            error_type="LintError",
            message="Linting errors found",
            stack_frames=frames,
            severity="warning",
            category="linting",
            confidence=0.95,
            raw_error=error_log[:500]
        )
    
    def _extract_lint_errors(self, error_log: str) -> list[StackFrame]:
        """Extract linting errors"""
        frames = []
        
        # Pattern: file.js:10:5: error/warning - message
        pattern = r'([^\s:]+):(\d+):(\d+):\s+(error|warning)\s+-\s+(.+)'
        
        for line in error_log.split('\n'):
            match = re.search(pattern, line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                column = int(match.group(3))
                severity = match.group(4)
                message = match.group(5)
                
                frames.append(StackFrame(
                    file_path=file_path,
                    line=line_num,
                    column=column,
                    code_snippet=message
                ))
        
        return frames
