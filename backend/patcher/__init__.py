"""
Smart Patcher System
Safe code patching with backups, validation, and undo
"""

from .fuzzy_matcher import FuzzyMatcher
from .validator import CodeValidator
from .backup_manager import BackupManager
from .history_tracker import HistoryTracker
from .applier import PatchApplier
from .patcher import SmartPatcher

__all__ = [
    "FuzzyMatcher",
    "CodeValidator",
    "BackupManager",
    "HistoryTracker",
    "PatchApplier",
    "SmartPatcher",
]
