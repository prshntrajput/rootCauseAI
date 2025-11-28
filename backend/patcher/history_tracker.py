"""
History Tracker
Tracks all applied fixes for undo and audit
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class HistoryTracker:
    """
    Tracks history of applied fixes
    """
    
    def __init__(self, history_file: str = ".fix-error-history.json"):
        """
        Initialize history tracker
        
        Args:
            history_file: Path to history file
        """
        self.history_file = Path(history_file)
        self._ensure_history_file()
    
    def _ensure_history_file(self):
        """Create history file if it doesn't exist"""
        if not self.history_file.exists():
            self._save_history([])
    
    def _load_history(self) -> List[Dict]:
        """Load history from file"""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _save_history(self, history: List[Dict]):
        """Save history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    
    def add_fix(
        self,
        file_path: str,
        original_snippet: str,
        new_snippet: str,
        backup_path: str,
        fix_id: Optional[str] = None
    ) -> str:
        """
        Add a fix to history
        
        Args:
            file_path: File that was modified
            original_snippet: Original code
            new_snippet: New code
            backup_path: Path to backup
            fix_id: Optional fix identifier
            
        Returns:
            Fix ID
        """
        history = self._load_history()
        
        if fix_id is None:
            fix_id = f"fix_{len(history) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        entry = {
            "fix_id": fix_id,
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "original_snippet": original_snippet,
            "new_snippet": new_snippet,
            "backup_path": backup_path,
            "reverted": False
        }
        
        history.append(entry)
        self._save_history(history)
        
        return fix_id
    
    def get_fix(self, fix_id: str) -> Optional[Dict]:
        """Get a specific fix by ID"""
        history = self._load_history()
        
        for entry in history:
            if entry["fix_id"] == fix_id:
                return entry
        
        return None
    
    def get_recent_fixes(self, count: int = 10) -> List[Dict]:
        """Get most recent fixes"""
        history = self._load_history()
        return history[-count:][::-1]  # Reverse to get newest first
    
    def mark_reverted(self, fix_id: str) -> bool:
        """Mark a fix as reverted"""
        history = self._load_history()
        
        for entry in history:
            if entry["fix_id"] == fix_id:
                entry["reverted"] = True
                self._save_history(history)
                return True
        
        return False
    
    def get_stats(self) -> Dict:
        """Get statistics about fixes"""
        history = self._load_history()
        
        return {
            "total_fixes": len(history),
            "reverted_count": sum(1 for h in history if h.get("reverted", False)),
            "active_fixes": sum(1 for h in history if not h.get("reverted", False)),
            "files_modified": len(set(h["file_path"] for h in history))
        }
    
    def clear_history(self):
        """Clear all history"""
        self._save_history([])
