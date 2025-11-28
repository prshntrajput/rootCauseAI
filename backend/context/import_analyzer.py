"""
Import Chain Analyzer
Analyzes import statements and resolves dependencies
"""

import ast
import re
from pathlib import Path
from typing import List, Set, Optional


class ImportAnalyzer:
    """
    Analyzes import statements in Python and JavaScript/TypeScript files
    to build dependency chains
    """
    
    @staticmethod
    def get_python_imports(file_path: str) -> List[str]:
        """
        Extract all imported modules from Python file
        
        Args:
            file_path: Path to Python file
            
        Returns:
            List of imported module names
        """
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read(), filename=file_path)
                except SyntaxError:
                    # If syntax error, try to extract imports with regex
                    return ImportAnalyzer._extract_python_imports_regex(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                    # Also capture relative imports
                    if node.level > 0:  # Relative import
                        imports.append('.' * node.level + (node.module or ''))
        
        except Exception as e:
            # Fallback to regex if AST parsing fails
            return ImportAnalyzer._extract_python_imports_regex(file_path)
        
        return imports
    
    @staticmethod
    def _extract_python_imports_regex(file_path: str) -> List[str]:
        """Fallback: Extract Python imports using regex"""
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern: import module or from module import ...
            import_pattern = r'^\s*(?:from\s+([\w.]+)\s+)?import\s+([\w\s,]+)'
            
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                if match.group(1):  # from X import Y
                    imports.append(match.group(1))
                else:  # import X
                    modules = match.group(2).split(',')
                    imports.extend([m.strip().split()[0] for m in modules])
        
        except Exception:
            pass
        
        return imports
    
    @staticmethod
    def get_js_imports(file_path: str) -> List[str]:
        """
        Extract imported modules from JavaScript/TypeScript file
        
        Args:
            file_path: Path to JS/TS file
            
        Returns:
            List of imported module paths
        """
        imports = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern 1: import ... from 'module'
            es6_pattern = r'import\s+(?:[\w\s{},*]+\s+from\s+)?[\'"]([^\'"]+)[\'"]'
            
            # Pattern 2: require('module')
            require_pattern = r'require\([\'"]([^\'"]+)[\'"]\)'
            
            # Pattern 3: import('module') - dynamic import
            dynamic_pattern = r'import\([\'"]([^\'"]+)[\'"]\)'
            
            for pattern in [es6_pattern, require_pattern, dynamic_pattern]:
                matches = re.findall(pattern, content)
                imports.extend(matches)
        
        except Exception:
            pass
        
        return imports
    
    @staticmethod
    def resolve_python_import(current_file: str, import_name: str) -> Optional[str]:
        """
        Resolve Python import to file path
        
        Args:
            current_file: Path to current file
            import_name: Import statement (e.g., 'utils.helper')
            
        Returns:
            Resolved file path or None
        """
        current_dir = Path(current_file).parent
        
        # Handle relative imports
        if import_name.startswith('.'):
            # Count leading dots
            level = len(import_name) - len(import_name.lstrip('.'))
            module = import_name.lstrip('.')
            
            # Go up directories
            target_dir = current_dir
            for _ in range(level - 1):
                target_dir = target_dir.parent
            
            # Try to resolve module
            if module:
                module_path = target_dir / module.replace('.', '/')
            else:
                module_path = target_dir
        else:
            # Absolute import - try from current directory first
            module_path = current_dir / import_name.replace('.', '/')
        
        # Try different extensions
        for ext in ['.py', '/__init__.py', '']:
            test_path = Path(str(module_path) + ext)
            if test_path.exists():
                return str(test_path)
        
        return None
    
    @staticmethod
    def resolve_js_import(current_file: str, import_path: str) -> Optional[str]:
        """
        Resolve JavaScript/TypeScript import to file path
        
        Args:
            current_file: Path to current file
            import_path: Import path (e.g., './utils/helper')
            
        Returns:
            Resolved file path or None
        """
        # Skip node_modules and absolute imports
        if not import_path.startswith('.'):
            return None
        
        current_dir = Path(current_file).parent
        target_path = current_dir / import_path
        
        # Try different extensions
        extensions = ['.js', '.ts', '.jsx', '.tsx', '/index.js', '/index.ts', '']
        
        for ext in extensions:
            test_path = Path(str(target_path) + ext)
            if test_path.exists():
                return str(test_path)
        
        return None
    
    @staticmethod
    def build_import_chain(
        file_path: str,
        max_depth: int = 2,
        visited: Optional[Set[str]] = None
    ) -> Set[str]:
        """
        Build import dependency chain recursively
        
        Args:
            file_path: Starting file path
            max_depth: Maximum recursion depth
            visited: Set of already visited files (for cycle detection)
            
        Returns:
            Set of all files in import chain
        """
        if visited is None:
            visited = set()
        
        # Normalize path
        file_path = str(Path(file_path).resolve())
        
        if file_path in visited or max_depth <= 0:
            return visited
        
        visited.add(file_path)
        
        # Determine file type
        if file_path.endswith('.py'):
            imports = ImportAnalyzer.get_python_imports(file_path)
            
            for imp in imports:
                resolved = ImportAnalyzer.resolve_python_import(file_path, imp)
                if resolved and resolved not in visited:
                    ImportAnalyzer.build_import_chain(resolved, max_depth - 1, visited)
        
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            imports = ImportAnalyzer.get_js_imports(file_path)
            
            for imp in imports:
                resolved = ImportAnalyzer.resolve_js_import(file_path, imp)
                if resolved and resolved not in visited:
                    ImportAnalyzer.build_import_chain(resolved, max_depth - 1, visited)
        
        return visited
