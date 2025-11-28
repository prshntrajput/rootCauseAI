"""
Token Budget Manager
Ensures context doesn't exceed LLM token limits
"""


class TokenManager:
    """
    Manages token budget to stay within LLM limits
    """
    
    def __init__(self, max_tokens: int = 8000):
        """
        Initialize token manager
        
        Args:
            max_tokens: Maximum tokens allowed
        """
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.items = []
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens in text
        
        Rule of thumb:
        - English: ~1 token per 4 characters
        - Code: ~1 token per 3 characters (more symbols)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Use conservative estimate for code
        return len(text) // 3
    
    def can_add(self, text: str, priority: int = 0) -> bool:
        """
        Check if text can be added within budget
        
        Args:
            text: Text to check
            priority: Priority level (higher = more important)
            
        Returns:
            True if can be added, False otherwise
        """
        estimated = self.estimate_tokens(text)
        return (self.current_tokens + estimated) <= self.max_tokens
    
    def add(self, text: str, label: str = "unknown") -> bool:
        """
        Add text to budget
        
        Args:
            text: Text to add
            label: Label for tracking
            
        Returns:
            True if added, False if exceeds budget
        """
        estimated = self.estimate_tokens(text)
        
        if (self.current_tokens + estimated) <= self.max_tokens:
            self.current_tokens += estimated
            self.items.append({
                "label": label,
                "tokens": estimated,
                "length": len(text)
            })
            return True
        
        return False
    
    def get_remaining(self) -> int:
        """Get remaining token budget"""
        return max(0, self.max_tokens - self.current_tokens)
    
    def get_usage_percentage(self) -> float:
        """Get budget usage as percentage"""
        return (self.current_tokens / self.max_tokens) * 100
    
    def reset(self):
        """Reset token counter"""
        self.current_tokens = 0
        self.items = []
    
    def get_summary(self) -> dict:
        """Get usage summary"""
        return {
            "max_tokens": self.max_tokens,
            "used_tokens": self.current_tokens,
            "remaining_tokens": self.get_remaining(),
            "usage_percentage": self.get_usage_percentage(),
            "items_count": len(self.items),
            "items": self.items
        }
