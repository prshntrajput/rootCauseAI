"""
Backup Manager
Manages file backups before applying changes
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


class BackupManager:
    """
    Manages backups of files before modification
    """
    
    def __init__(self, backup_dir: str = ".fix-error-backup"):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """
        Create a backup of a file
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        source = Path(file_path)
        
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create timestamp-based backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.name}.{timestamp}.bak"
        
        # Create subdirectory structure matching original
        relative_path = source.relative_to(".") if source.is_relative_to(".") else source
        backup_subdir = self.backup_dir / relative_path.parent
        backup_subdir.mkdir(parents=True, exist_ok=True)
        
        backup_path = backup_subdir / backup_name
        
        # Copy file
        shutil.copy2(source, backup_path)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, original_path: str) -> bool:
        """
        Restore a file from backup
        
        Args:
            backup_path: Path to backup file
            original_path: Original file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup = Path(backup_path)
            original = Path(original_path)
            
            if not backup.exists():
                return False
            
            # Create parent directory if needed
            original.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore file
            shutil.copy2(backup, original)
            
            return True
        
        except Exception:
            return False
    
    def get_latest_backup(self, file_path: str) -> Optional[str]:
        """
        Get the most recent backup for a file
        
        Args:
            file_path: Original file path
            
        Returns:
            Path to latest backup or None
        """
        source = Path(file_path)
        filename = source.name
        
        # Search for backups
        backups = list(self.backup_dir.rglob(f"{filename}.*.bak"))
        
        if not backups:
            return None
        
        # Sort by modification time, get newest
        latest = max(backups, key=lambda p: p.stat().st_mtime)
        
        return str(latest)
    
    def list_backups(self, file_path: Optional[str] = None) -> list[dict]:
        """
        List all backups
        
        Args:
            file_path: Optional file path to filter by
            
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        if file_path:
            filename = Path(file_path).name
            backup_files = list(self.backup_dir.rglob(f"{filename}.*.bak"))
        else:
            backup_files = list(self.backup_dir.rglob("*.bak"))
        
        for backup in backup_files:
            stat = backup.stat()
            backups.append({
                "path": str(backup),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "original_name": backup.name.rsplit('.', 2)[0]
            })
        
        return sorted(backups, key=lambda x: x["modified"], reverse=True)
    
    def clear_old_backups(self, days: int = 7):
        """
        Clear backups older than specified days
        
        Args:
            days: Age threshold in days
        """
        from datetime import timedelta
        
        threshold = datetime.now() - timedelta(days=days)
        
        for backup in self.backup_dir.rglob("*.bak"):
            if datetime.fromtimestamp(backup.stat().st_mtime) < threshold:
                backup.unlink()
