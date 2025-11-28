"""
Factory Pattern for LLM Provider Creation
Simplifies switching between different LLM providers
"""

from typing import Optional
from .base_provider import BaseLLMProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from backend.config import settings


class LLMProviderFactory:
    """
    Factory class to create LLM provider instances
    Supports dynamic provider selection and configuration
    """
    
    # Registry of available providers
    _providers = {
        "gemini": GeminiProvider,
        "groq": GroqProvider,
    }
    
    @classmethod
    def create(cls, provider: Optional[str] = None) -> BaseLLMProvider:
        """
        Create an LLM provider instance
        
        Args:
            provider: Provider name ("gemini" or "groq")
                     If None, uses default from settings
        
        Returns:
            Configured LLM provider instance
            
        Raises:
            ValueError: If provider is unknown or not configured
        """
        # Use default provider if not specified
        provider_name = (provider or settings.default_provider).lower()
        
        # Validate provider exists
        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider '{provider_name}'. "
                f"Available providers: {available}"
            )
        
        # Get provider configuration
        try:
            config = settings.get_provider_config(provider_name)
        except Exception as e:
            raise ValueError(f"Failed to get config for {provider_name}: {e}")
        
        # Validate API key is present
        if not config["api_key"] or config["api_key"].startswith("YOUR_"):
            raise ValueError(
                f"{provider_name.upper()} API key is not configured. "
                f"Please set it in .fix-error-config.yaml or .env file"
            )
        
        # Create and return provider instance
        provider_class = cls._providers[provider_name]
        
        try:
            return provider_class(
                api_key=config["api_key"],
                model=config["model"]
            )
        except Exception as e:
            raise ValueError(f"Failed to create {provider_name} provider: {e}")
    
    @classmethod
    def list_providers(cls) -> list[str]:
        """Get list of available provider names"""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Register a new provider (for extensibility)
        
        Args:
            name: Provider identifier
            provider_class: Class implementing BaseLLMProvider
        """
        if not issubclass(provider_class, BaseLLMProvider):
            raise TypeError(f"{provider_class} must inherit from BaseLLMProvider")
        
        cls._providers[name.lower()] = provider_class
