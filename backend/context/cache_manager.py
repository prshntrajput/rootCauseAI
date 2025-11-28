"""
Cache Manager
Caches context for repeated errors to improve performance
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta


class CacheManager:
    """
    Manages cache for error contexts to avoid re-processing
    """
    
    def __init__(self, cache_dir: str = ".fix-error-cache"):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache settings
        self.cache_ttl_hours = 24  # Cache expires after 24 hours
    
    def _generate_key(self, error_log: str, file_path: str) -> str:
        """
        Generate cache key from error and file
        
        Args:
            error_log: Error log text
            file_path: Path to error file
            
        Returns:
            Cache key (hash)
        """
        # Combine error signature with file path
        combined = f"{error_log[:500]}:{file_path}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached context
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None if expired/not found
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(data.get("timestamp", ""))
            if datetime.now() - cached_time > timedelta(hours=self.cache_ttl_hours):
                # Cache expired, delete it
                cache_file.unlink()
                return None
            
            return data.get("context")
            
        except Exception:
            return None
    
    def set(self, cache_key: str, context_data: Dict):
        """
        Store context in cache
        
        Args:
            cache_key: Cache key
            context_data: Context data to cache
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "context": context_data
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception:
            pass  # Silently fail if can't cache
    
    def clear(self):
        """Clear all cached data"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception:
            pass
    
    def clear_expired(self):
        """Clear only expired cache entries"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(data.get("timestamp", ""))
                    if datetime.now() - cached_time > timedelta(hours=self.cache_ttl_hours):
                        cache_file.unlink()
                        
                except Exception:
                    continue
        except Exception:
            pass
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_files = len(list(self.cache_dir.glob("*.json")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))
        
        return {
            "cache_dir": str(self.cache_dir),
            "total_entries": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
