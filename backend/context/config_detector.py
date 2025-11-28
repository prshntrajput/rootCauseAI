"""
Config File Detector
Finds relevant configuration files in the project
"""

from pathlib import Path
from typing import List, Dict, Optional


class ConfigDetector:
    """
    Detects and reads relevant configuration files
    """
    
    # Common config files by language/framework
    CONFIG_FILES = {
        "python": [
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "poetry.lock",
            "setup.cfg",
            "tox.ini",
            ".python-version"
        ],
        "javascript": [
            "package.json",
            "package-lock.json",
            "tsconfig.json",
            "jsconfig.json",
            ".babelrc",
            "webpack.config.js",
            "vite.config.js",
            "next.config.js",
            ".eslintrc.js",
            ".prettierrc"
        ],
        "general": [
            ".env.example",
            ".env.sample",
            "docker-compose.yml",
            "Dockerfile",
            ".gitignore",
            "README.md"
        ]
    }
    
    @staticmethod
    def find_config_files(
        project_root: str = ".",
        language: Optional[str] = None
    ) -> List[str]:
        """
        Find relevant config files in project
        
        Args:
            project_root: Root directory of project
            language: Language to find configs for (None for all)
            
        Returns:
            List of found config file paths
        """
        found_files = []
        root_path = Path(project_root)
        
        # Determine which config files to look for
        if language:
            config_files = ConfigDetector.CONFIG_FILES.get(language, [])
            config_files += ConfigDetector.CONFIG_FILES["general"]
        else:
            # All config files
            config_files = []
            for file_list in ConfigDetector.CONFIG_FILES.values():
                config_files.extend(file_list)
        
        # Search for files
        for config_file in config_files:
            file_path = root_path / config_file
            if file_path.exists() and file_path.is_file():
                found_files.append(str(file_path))
        
        return found_files
    
    @staticmethod
    def get_config_content(
        config_files: List[str],
        max_size: int = 5000
    ) -> Dict[str, str]:
        """
        Read content of config files
        
        Args:
            config_files: List of config file paths
            max_size: Maximum characters per file
            
        Returns:
            Dictionary mapping file paths to content
        """
        content_map = {}
        
        for file_path in config_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(max_size)
                    content_map[file_path] = content
            except Exception:
                continue
        
        return content_map
    
    @staticmethod
    def detect_framework(project_root: str = ".") -> Optional[str]:
        """
        Detect framework from config files
        
        Args:
            project_root: Root directory of project
            
        Returns:
            Framework name or None
        """
        root_path = Path(project_root)
        
        # Check Python frameworks
        requirements_file = root_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        return 'django'
                    elif 'flask' in content:
                        return 'flask'
                    elif 'fastapi' in content:
                        return 'fastapi'
            except:
                pass
        
        # Check JavaScript frameworks
        package_json = root_path / "package.json"
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        return 'react'
                    elif 'vue' in deps:
                        return 'vue'
                    elif 'next' in deps:
                        return 'nextjs'
                    elif 'express' in deps:
                        return 'express'
            except:
                pass
        
        return None
