"""
Context Builder
Orchestrates all context gathering components
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from pathlib import Path

from backend.parsers.base_parser import ParsedError
from .file_reader import FileReader
from .import_analyzer import ImportAnalyzer
from .git_analyzer import GitAnalyzer
from .config_detector import ConfigDetector
from .token_manager import TokenManager


class FileContext(BaseModel):
    """Represents context from a single file"""
    
    file_path: str = Field(description="Path to the file")
    start_line: int = Field(description="Starting line number")
    end_line: int = Field(description="Ending line number")
    content: str = Field(description="File content")
    is_primary: bool = Field(default=False, description="Is this the primary error file")
    git_diff: Optional[str] = Field(default=None, description="Recent git changes")
    recent_commits: Optional[List[dict]] = Field(default=None, description="Recent commits")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/main.py",
                "start_line": 10,
                "end_line": 30,
                "content": "def calculate():\n    ...",
                "is_primary": True
            }
        }


class CodeContext(BaseModel):
    """Complete code context for error analysis"""
    
    primary_files: List[FileContext] = Field(
        default_factory=list,
        description="Files where error occurred"
    )
    related_files: List[FileContext] = Field(
        default_factory=list,
        description="Related files (imports, dependencies)"
    )
    config_files: List[FileContext] = Field(
        default_factory=list,
        description="Configuration files"
    )
    total_tokens: int = Field(description="Total tokens used")
    framework: Optional[str] = Field(default=None, description="Detected framework")
    
    class Config:
        json_schema_extra = {
            "example": {
                "primary_files": [],
                "related_files": [],
                "config_files": [],
                "total_tokens": 1500,
                "framework": "fastapi"
            }
        }


class ContextBuilder:
    """
    Intelligent context builder that gathers all relevant
    information for error analysis
    """
    
    def __init__(self, max_tokens: int = 8000, project_root: str = "."):
        """
        Initialize context builder
        
        Args:
            max_tokens: Maximum token budget
            project_root: Root directory of project
        """
        self.max_tokens = max_tokens
        self.project_root = project_root
        self.token_manager = TokenManager(max_tokens)
    
    def build(self, parsed_error: ParsedError) -> CodeContext:
        """
        Build complete code context for error
        
        Args:
            parsed_error: Parsed error information
            
        Returns:
            CodeContext with all gathered information
        """
        self.token_manager.reset()
        
        primary_files = []
        related_files = []
        config_files = []
        
        # 1. Gather primary files (where error occurred)
        primary_files = self._gather_primary_files(parsed_error)
        
        # 2. Gather related files (imports, dependencies)
        if parsed_error.stack_frames and self.token_manager.get_remaining() > 2000:
            related_files = self._gather_related_files(parsed_error)
        
        # 3. Gather config files
        if self.token_manager.get_remaining() > 1000:
            config_files = self._gather_config_files(parsed_error.language)
        
        # 4. Detect framework
        framework = parsed_error.framework or ConfigDetector.detect_framework(self.project_root)
        
        return CodeContext(
            primary_files=primary_files,
            related_files=related_files,
            config_files=config_files,
            total_tokens=self.token_manager.current_tokens,
            framework=framework
        )
    
    def _gather_primary_files(self, parsed_error: ParsedError) -> List[FileContext]:
        """Gather files where error occurred"""
        primary_files = []
        
        # Get top 3 stack frames (most relevant)
        for frame in parsed_error.stack_frames[:3]:
            if not FileReader.file_exists(frame.file_path):
                continue
            
            try:
                # Get code around error line
                context_data = FileReader.get_lines_around(
                    frame.file_path,
                    frame.line,
                    context_lines=15  # ±15 lines
                )
                
                content = context_data["content"]
                
                # Check if we can add this file
                if not self.token_manager.can_add(content):
                    # Try with fewer lines
                    context_data = FileReader.get_lines_around(
                        frame.file_path,
                        frame.line,
                        context_lines=8
                    )
                    content = context_data["content"]
                    
                    if not self.token_manager.can_add(content):
                        continue  # Skip if still too large
                
                # Get git information
                git_diff = None
                recent_commits = None
                
                if GitAnalyzer.is_git_repo(Path(frame.file_path).parent):
                    git_diff = GitAnalyzer.get_recent_changes(frame.file_path, max_lines=30)
                    recent_commits = GitAnalyzer.get_recent_commits(frame.file_path, limit=3)
                
                # Create file context
                file_context = FileContext(
                    file_path=frame.file_path,
                    start_line=context_data["start_line"],
                    end_line=context_data["end_line"],
                    content=content,
                    is_primary=True,
                    git_diff=git_diff,
                    recent_commits=recent_commits
                )
                
                # Add to token budget
                self.token_manager.add(content, label=f"primary:{frame.file_path}")
                if git_diff:
                    self.token_manager.add(git_diff, label=f"git_diff:{frame.file_path}")
                
                primary_files.append(file_context)
                
            except Exception as e:
                # Skip files that can't be read
                continue
        
        return primary_files
    
    def _gather_related_files(self, parsed_error: ParsedError) -> List[FileContext]:
        """Gather related files through import analysis"""
        related_files = []
        
        if not parsed_error.stack_frames:
            return related_files
        
        # Analyze imports from primary file
        main_file = parsed_error.stack_frames[0].file_path
        
        if not FileReader.file_exists(main_file):
            return related_files
        
        try:
            # Build import chain (depth=1 to avoid too many files)
            import_chain = ImportAnalyzer.build_import_chain(
                main_file,
                max_depth=1
            )
            
            # Remove main file from chain
            import_chain.discard(main_file)
            
            # Add related files (limit to 3)
            for related_path in list(import_chain)[:3]:
                if not FileReader.file_exists(related_path):
                    continue
                
                try:
                    # Read file content (limit to first 50 lines or 2000 chars)
                    content = FileReader.read_file(related_path, end_line=50)
                    
                    # Truncate if too long
                    if len(content) > 2000:
                        content = content[:2000] + "\n... (truncated)"
                    
                    if not self.token_manager.can_add(content):
                        break  # Stop if budget exceeded
                    
                    file_context = FileContext(
                        file_path=related_path,
                        start_line=1,
                        end_line=min(50, len(content.split('\n'))),
                        content=content,
                        is_primary=False
                    )
                    
                    self.token_manager.add(content, label=f"related:{related_path}")
                    related_files.append(file_context)
                    
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return related_files
    
    def _gather_config_files(self, language: str) -> List[FileContext]:
        """Gather relevant configuration files"""
        config_files = []
        
        # Find config files
        found_configs = ConfigDetector.find_config_files(
            self.project_root,
            language=language
        )
        
        # Prioritize important configs
        priority_configs = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "tsconfig.json"
        ]
        
        # Sort by priority
        found_configs.sort(
            key=lambda x: (
                Path(x).name not in priority_configs,
                Path(x).name
            )
        )
        
        # Read config files
        for config_path in found_configs[:3]:  # Max 3 config files
            try:
                content = FileReader.read_file(config_path)
                
                # Limit config file size
                if len(content) > 1500:
                    content = content[:1500] + "\n... (truncated)"
                
                if not self.token_manager.can_add(content):
                    break
                
                file_context = FileContext(
                    file_path=config_path,
                    start_line=1,
                    end_line=len(content.split('\n')),
                    content=content,
                    is_primary=False
                )
                
                self.token_manager.add(content, label=f"config:{config_path}")
                config_files.append(file_context)
                
            except Exception:
                continue
        
        return config_files
    
    def get_token_summary(self) -> dict:
        """Get token usage summary"""
        return self.token_manager.get_summary()
