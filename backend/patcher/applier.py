"""
Patch Applier
Applies code patches safely to files
"""

import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional

from .fuzzy_matcher import FuzzyMatcher
from .validator import CodeValidator
from .backup_manager import BackupManager
from .history_tracker import HistoryTracker


class PatchApplier:
    """
    Applies code patches with safety checks
    """
    
    def __init__(
        self,
        backup_dir: str = ".fix-error-backup",
        history_file: str = ".fix-error-history.json"
    ):
        """
        Initialize patch applier
        
        Args:
            backup_dir: Directory for backups
            history_file: Path to history file
        """
        self.backup_manager = BackupManager(backup_dir)
        self.history_tracker = HistoryTracker(history_file)
        self.fuzzy_matcher = FuzzyMatcher()
        self.validator = CodeValidator()
    
    def apply_patch(
        self,
        file_path: str,
        original_snippet: str,
        new_snippet: str,
        language: str,
        dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Apply a code patch to a file
        
        Args:
            file_path: Path to file to patch
            original_snippet: Code to replace
            new_snippet: New code
            language: Programming language
            dry_run: If True, don't actually modify file
            
        Returns:
            Tuple of (success, message)
        """
        file_path_obj = Path(file_path)
        
        # Check if file exists
        if not file_path_obj.exists():
            return False, f"File not found: {file_path}"
        
        # Read current content
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception as e:
            return False, f"Failed to read file: {e}"
        
        # Find matching location
        match = self.fuzzy_matcher.match_with_context(
            original_snippet,
            current_content,
            context_lines=2
        )
        
        if not match:
            return False, "Could not find matching code in file (similarity too low)"
        
        start_line, end_line, similarity = match
        
        # Replace code
        lines = current_content.split('\n')
        new_content = '\n'.join(
            lines[:start_line] + 
            [new_snippet] + 
            lines[end_line:]
        )
        
        # Validate new content
        is_valid, error_msg = self.validator.validate_file_after_patch(
            file_path,
            new_content,
            language
        )
        
        if not is_valid:
            return False, f"Validation failed: {error_msg}"
        
        # Dry run - don't actually apply
        if dry_run:
            return True, f"Dry run successful (would modify lines {start_line}-{end_line}, {similarity:.0%} match)"
        
        # Create backup
        try:
            backup_path = self.backup_manager.create_backup(file_path)
        except Exception as e:
            return False, f"Failed to create backup: {e}"
        
        # Apply patch atomically (write to temp, then rename)
        try:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=file_path_obj.parent,
                delete=False
            ) as temp_file:
                temp_file.write(new_content)
                temp_path = temp_file.name
            
            # Atomic rename
            shutil.move(temp_path, file_path)
            
            # Record in history
            fix_id = self.history_tracker.add_fix(
                file_path=file_path,
                original_snippet=original_snippet,
                new_snippet=new_snippet,
                backup_path=backup_path
            )
            
            return True, f"Successfully applied patch (fix ID: {fix_id})"
        
        except Exception as e:
            # Restore from backup on error
            self.backup_manager.restore_backup(backup_path, file_path)
            return False, f"Failed to apply patch: {e}"
    
    def undo_last_fix(self) -> Tuple[bool, str]:
        """
        Undo the most recent fix
        
        Returns:
            Tuple of (success, message)
        """
        recent_fixes = self.history_tracker.get_recent_fixes(count=1)
        
        if not recent_fixes:
            return False, "No fixes to undo"
        
        fix = recent_fixes[0]
        
        if fix.get("reverted", False):
            return False, "Fix already reverted"
        
        # Restore from backup
        success = self.backup_manager.restore_backup(
            fix["backup_path"],
            fix["file_path"]
        )
        
        if success:
            self.history_tracker.mark_reverted(fix["fix_id"])
            return True, f"Successfully undid fix {fix['fix_id']}"
        else:
            return False, "Failed to restore from backup"
    
    def undo_fix(self, fix_id: str) -> Tuple[bool, str]:
        """
        Undo a specific fix
        
        Args:
            fix_id: Fix identifier
            
        Returns:
            Tuple of (success, message)
        """
        fix = self.history_tracker.get_fix(fix_id)
        
        if not fix:
            return False, f"Fix not found: {fix_id}"
        
        if fix.get("reverted", False):
            return False, "Fix already reverted"
        
        success = self.backup_manager.restore_backup(
            fix["backup_path"],
            fix["file_path"]
        )
        
        if success:
            self.history_tracker.mark_reverted(fix_id)
            return True, f"Successfully undid fix {fix_id}"
        else:
            return False, "Failed to restore from backup"
