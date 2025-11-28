"""
Abstract Base Class for LLM Providers
Defines the interface that all LLM providers must implement
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Standardized response from any LLM provider"""
    
    content: str = Field(description="Generated text content")
    model: str = Field(description="Model name used")
    tokens_used: int = Field(description="Total tokens consumed")
    finish_reason: str = Field(description="Why generation stopped")
    raw_response: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Raw API response for debugging"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "The error is caused by...",
                "model": "gemini-2.0-flash-exp",
                "tokens_used": 245,
                "finish_reason": "stop"
            }
        }


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    Ensures consistent interface across different LLM APIs
    """
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize the LLM provider
        
        Args:
            api_key: API authentication key
            model: Model identifier/name
        """
        if not api_key:
            raise ValueError(f"{self.__class__.__name__} requires an API key")
        
        self.api_key = api_key
        self.model = model
        self._validate_setup()
    
    @abstractmethod
    def _validate_setup(self) -> None:
        """
        Validate provider-specific setup
        Override to check API key format, model availability, etc.
        """
        pass
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """
        Generate text response from the LLM
        
        Args:
            system_prompt: System instructions (sets behavior/role)
            user_prompt: User's actual query/request
            temperature: Randomness (0.0=deterministic, 1.0=creative)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse with generated content and metadata
            
        Raises:
            Exception: If API call fails
        """
        pass
    
    @abstractmethod
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response from the LLM
        
        Args:
            system_prompt: System instructions
            user_prompt: User's query
            schema: Optional JSON schema for validation
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            Exception: If API call fails or response is not valid JSON
        """
        pass
    
    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return self.__class__.__name__.replace("Provider", "").lower()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model}')"
