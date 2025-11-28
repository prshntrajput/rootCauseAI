"""
Git Analyzer
Analyzes recent git changes for context
"""

import subprocess
from typing import Optional, List
from pathlib import Path


class GitAnalyzer:
    """
    Analyzes git repository for recent changes
    """
    
    @staticmethod
    def is_git_repo(directory: str = ".") -> bool:
        """
        Check if directory is a git repository
        
        Args:
            directory: Directory to check
            
        Returns:
            True if git repo, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=directory,
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def get_recent_changes(
        file_path: str,
        max_lines: int = 50,
        commits_back: int = 1
    ) -> Optional[str]:
        """
        Get recent git diff for a file
        
        Args:
            file_path: Path to file
            max_lines: Maximum lines of diff to return
            commits_back: How many commits back to check
            
        Returns:
            Git diff string or None
        """
        if not GitAnalyzer.is_git_repo(Path(file_path).parent):
            return None
        
        try:
            # Get diff from HEAD~N to current
            result = subprocess.run(
                ["git", "diff", f"HEAD~{commits_back}", "--", file_path],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(Path(file_path).parent)
            )
            
            if result.returncode == 0 and result.stdout:
                diff = result.stdout
                
                # Limit lines
                diff_lines = diff.split('\n')[:max_lines]
                return '\n'.join(diff_lines)
        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_file_blame(
        file_path: str,
        line_number: int,
        context_lines: int = 5
    ) -> Optional[dict]:
        """
        Get git blame for specific lines
        
        Args:
            file_path: Path to file
            line_number: Target line number
            context_lines: Lines before and after
            
        Returns:
            Dictionary with blame info or None
        """
        if not GitAnalyzer.is_git_repo(Path(file_path).parent):
            return None
        
        try:
            start_line = max(1, line_number - context_lines)
            end_line = line_number + context_lines
            
            result = subprocess.run(
                ["git", "blame", "-L", f"{start_line},{end_line}", file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {
                    "blame": result.stdout,
                    "start_line": start_line,
                    "end_line": end_line
                }
        
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_recent_commits(
        file_path: str,
        limit: int = 5
    ) -> List[dict]:
        """
        Get recent commits that modified a file
        
        Args:
            file_path: Path to file
            limit: Maximum number of commits
            
        Returns:
            List of commit info dictionaries
        """
        if not GitAnalyzer.is_git_repo(Path(file_path).parent):
            return []
        
        commits = []
        
        try:
            # Format: hash|author|date|message
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--format=%H|%an|%ar|%s", "--", file_path],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(Path(file_path).parent)
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) == 4:
                            commits.append({
                                "hash": parts[0][:8],
                                "author": parts[1],
                                "date": parts[2],
                                "message": parts[3]
                            })
        
        except Exception:
            pass
        
        return commits
