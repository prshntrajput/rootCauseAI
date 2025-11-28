"""
File Reader with Encoding Detection
Safely reads files with automatic encoding detection
"""

from pathlib import Path
from typing import Optional, Dict
import chardet


class FileReader:
    """
    Smart file reader that handles encoding issues
    and provides line-based reading
    """
    
    @staticmethod
    def detect_encoding(file_path: str) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to file
            
        Returns:
            Detected encoding name (e.g., 'utf-8', 'ascii')
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'  # Default fallback
    
    @staticmethod
    def read_file(
        file_path: str,
        start_line: int = 1,
        end_line: Optional[int] = None,
        encoding: Optional[str] = None
    ) -> str:
        """
        Read file content with optional line range
        
        Args:
            file_path: Path to file
            start_line: Starting line (1-indexed)
            end_line: Ending line (inclusive), None for all
            encoding: File encoding, auto-detected if None
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If file can't be read
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")
        
        # Auto-detect encoding if not provided
        if encoding is None:
            encoding = FileReader.detect_encoding(file_path)
        
        try:
            with open(path, 'r', encoding=encoding, errors='replace') as f:
                lines = f.readlines()
            
            # Handle line range
            if start_line < 1:
                start_line = 1
            
            if end_line is None:
                end_line = len(lines)
            else:
                end_line = min(end_line, len(lines))
            
            # Extract requested lines (convert to 0-indexed)
            selected_lines = lines[start_line-1:end_line]
            return ''.join(selected_lines)
            
        except UnicodeDecodeError:
            # Fallback to latin-1 which accepts all byte values
            with open(path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                selected_lines = lines[start_line-1:end_line if end_line else len(lines)]
                return ''.join(selected_lines)
    
    @staticmethod
    def get_lines_around(
        file_path: str,
        target_line: int,
        context_lines: int = 10,
        encoding: Optional[str] = None
    ) -> Dict:
        """
        Get lines around a target line (for context)
        
        Args:
            file_path: Path to file
            target_line: Line number to center on
            context_lines: Number of lines before and after
            encoding: File encoding
            
        Returns:
            Dictionary with file info and content
        """
        start_line = max(1, target_line - context_lines)
        end_line = target_line + context_lines
        
        content = FileReader.read_file(file_path, start_line, end_line, encoding)
        
        # Count actual lines in content
        actual_lines = content.count('\n')
        actual_end = start_line + actual_lines
        
        return {
            "file_path": file_path,
            "start_line": start_line,
            "end_line": actual_end,
            "target_line": target_line,
            "content": content,
            "total_lines": len(content.split('\n'))
        }
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if file exists"""
        return Path(file_path).exists() and Path(file_path).is_file()
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        return Path(file_path).stat().st_size if FileReader.file_exists(file_path) else 0
