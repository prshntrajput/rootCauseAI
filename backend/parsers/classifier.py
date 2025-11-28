"""
Error Classifier
Auto-detects error type and routes to appropriate parser
"""

from typing import List, Optional
from .base_parser import BaseParser, ParsedError
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser
from .typescript_parser import TypeScriptParser
from .react_parser import ReactParser
from .linter_parser import LinterParser


class ErrorClassifier:
    """
    Intelligent error classifier that automatically detects
    error type and uses the best parser
    """
    
    def __init__(self):
        """Initialize all available parsers"""
        self.parsers: List[BaseParser] = [
            PythonParser(),
            TypeScriptParser(),  # Check TS before JS (TS is more specific)
            ReactParser(),
            JavaScriptParser(),
            LinterParser(),
        ]
    
    def classify_and_parse(self, error_log: str) -> ParsedError:
        """
        Classify error type and parse it
        
        Args:
            error_log: Raw error log text
            
        Returns:
            ParsedError with structured data
            
        Raises:
            ValueError: If no parser can handle the error
        """
        if not error_log or not error_log.strip():
            raise ValueError("Error log is empty")
        
        # Find best parser based on confidence scores
        best_parser = None
        best_confidence = 0.0
        parser_scores = {}
        
        for parser in self.parsers:
            confidence = parser.can_parse(error_log)
            parser_name = parser.get_parser_name()
            parser_scores[parser_name] = confidence
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_parser = parser
        
        # Require minimum confidence threshold
        if best_parser is None or best_confidence < 0.3:
            # Log what we tried
            scores_str = ", ".join([f"{name}: {score:.2f}" for name, score in parser_scores.items()])
            raise ValueError(
                f"Could not classify error type (best score: {best_confidence:.2f}). "
                f"Parser scores: {scores_str}"
            )
        
        # Parse with best parser
        try:
            parsed_error = best_parser.parse(error_log)
            # Update confidence with classifier's score
            parsed_error.confidence = best_confidence
            return parsed_error
        except Exception as e:
            raise ValueError(f"Failed to parse with {best_parser.get_parser_name()}: {e}")
    
    def get_parser_scores(self, error_log: str) -> dict[str, float]:
        """
        Get confidence scores from all parsers (for debugging)
        
        Args:
            error_log: Raw error log text
            
        Returns:
            Dictionary mapping parser names to confidence scores
        """
        scores = {}
        for parser in self.parsers:
            parser_name = parser.get_parser_name()
            confidence = parser.can_parse(error_log)
            scores[parser_name] = confidence
        
        return scores
    
    def list_parsers(self) -> List[str]:
        """Get list of available parser names"""
        return [parser.get_parser_name() for parser in self.parsers]
