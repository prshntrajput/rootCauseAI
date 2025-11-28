"""
Fuzzy Code Matcher
Handles whitespace and indentation differences when matching code
"""

import difflib
from typing import Optional, Tuple


class FuzzyMatcher:
    """
    Matches code snippets with tolerance for whitespace differences
    """
    
    @staticmethod
    def normalize_whitespace(code: str) -> str:
        """
        Normalize whitespace for comparison
        
        Args:
            code: Code string
            
        Returns:
            Normalized code
        """
        # Remove leading/trailing whitespace from each line
        lines = [line.rstrip() for line in code.split('\n')]
        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return '\n'.join(lines)
    
    @staticmethod
    def dedent_code(code: str) -> str:
        """
        Remove common leading whitespace
        
        Args:
            code: Code string
            
        Returns:
            Dedented code
        """
        import textwrap
        return textwrap.dedent(code)
    
    @staticmethod
    def similarity_ratio(str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        return difflib.SequenceMatcher(None, str1, str2).ratio()
    
    @staticmethod
    def find_best_match(
        target: str,
        file_content: str,
        threshold: float = 0.8
    ) -> Optional[Tuple[int, int, float]]:
        """
        Find best matching location in file
        
        Args:
            target: Code snippet to find
            file_content: File content to search in
            threshold: Minimum similarity ratio (0.8 = 80% match)
            
        Returns:
            Tuple of (start_line, end_line, similarity) or None
        """
        # Normalize target
        target_normalized = FuzzyMatcher.normalize_whitespace(target)
        target_lines = target_normalized.split('\n')
        
        # Split file into lines
        file_lines = file_content.split('\n')
        
        best_match = None
        best_similarity = 0.0
        
        # Sliding window search
        window_size = len(target_lines)
        
        for i in range(len(file_lines) - window_size + 1):
            window = '\n'.join(file_lines[i:i+window_size])
            window_normalized = FuzzyMatcher.normalize_whitespace(window)
            
            similarity = FuzzyMatcher.similarity_ratio(
                target_normalized,
                window_normalized
            )
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = (i, i + window_size, similarity)
        
        return best_match
    
    @staticmethod
    def exact_match(target: str, file_content: str) -> Optional[Tuple[int, int]]:
        """
        Try to find exact match first
        
        Args:
            target: Code to find
            file_content: File content
            
        Returns:
            Tuple of (start_line, end_line) or None
        """
        if target in file_content:
            # Find line numbers
            before_match = file_content[:file_content.index(target)]
            start_line = before_match.count('\n')
            end_line = start_line + target.count('\n') + 1
            return (start_line, end_line)
        
        return None
    
    @staticmethod
    def match_with_context(
        target: str,
        file_content: str,
        context_lines: int = 2
    ) -> Optional[Tuple[int, int, float]]:
        """
        Match code with surrounding context
        
        Args:
            target: Code to match
            file_content: File content
            context_lines: Lines of context to include
            
        Returns:
            Match location or None
        """
        # Try exact match first
        exact = FuzzyMatcher.exact_match(target, file_content)
        if exact:
            return (*exact, 1.0)
        
        # Try fuzzy match
        return FuzzyMatcher.find_best_match(target, file_content, threshold=0.8)
