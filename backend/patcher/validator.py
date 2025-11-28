"""
Code Validator
Validates syntax before applying patches
"""

import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional


class CodeValidator:
    """
    Validates code syntax before applying changes
    """
    
    @staticmethod
    def validate_python(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python code syntax
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Try to parse the code
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_javascript(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate JavaScript code syntax using Node.js
        
        Args:
            code: JavaScript code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if node is available
            result = subprocess.run(
                ["node", "--check", "-"],
                input=code.encode(),
                capture_output=True,
                timeout=2
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr.decode()
        
        except FileNotFoundError:
            # Node.js not installed, skip validation
            return True, "Node.js not available for validation"
        except subprocess.TimeoutExpired:
            return False, "Validation timeout"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_typescript(code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate TypeScript code syntax
        
        Args:
            code: TypeScript code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if tsc is available
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ["tsc", "--noEmit", temp_file],
                    capture_output=True,
                    timeout=3
                )
                
                Path(temp_file).unlink()
                
                if result.returncode == 0:
                    return True, None
                else:
                    return False, result.stdout.decode()
            
            except FileNotFoundError:
                # TypeScript not installed
                Path(temp_file).unlink()
                return True, "TypeScript not available for validation"
        
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_code(code: str, language: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code based on language
        
        Args:
            code: Code to validate
            language: Language name
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if language == "python":
            return CodeValidator.validate_python(code)
        elif language in ["javascript", "jsx"]:
            return CodeValidator.validate_javascript(code)
        elif language in ["typescript", "tsx"]:
            return CodeValidator.validate_typescript(code)
        else:
            # Unknown language, assume valid
            return True, None
    
    @staticmethod
    def validate_file_after_patch(
        file_path: str,
        new_content: str,
        language: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate entire file after patching
        
        Args:
            file_path: Path to file
            new_content: New file content
            language: Programming language
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return CodeValidator.validate_code(new_content, language)
