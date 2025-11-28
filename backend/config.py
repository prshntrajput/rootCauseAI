"""
Configuration Management System
Loads settings from YAML file or environment variables
"""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, Optional
import yaml
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # API Keys
    gemini_api_key: str = Field(default="", description="Gemini API key from Google AI Studio")
    groq_api_key: str = Field(default="", description="Groq API key from Groq Console")
    
    # LLM Configuration
    default_provider: Literal["gemini", "groq"] = Field(
        default="gemini",
        description="Default LLM provider to use"
    )
    gemini_model: str = Field(
        default="gemini-2.0-flash",
        description="Gemini model name"
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model name"
    )
    
    # Agent Configuration
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for failed operations"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score to accept a fix"
    )
    max_context_tokens: int = Field(
        default=8000,
        ge=1000,
        le=100000,
        description="Maximum tokens to include in context"
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="LLM temperature (0=deterministic, 1=creative)"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @classmethod
    def from_yaml(cls, config_path: str = ".fix-error-config.yaml") -> "Settings":
        """
        Load settings from YAML file, falling back to environment variables
        
        Args:
            config_path: Path to YAML config file
            
        Returns:
            Settings instance
        """
        # First, try to load from YAML
        if Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    yaml_data = yaml.safe_load(f) or {}
                    # Create settings from YAML data
                    return cls(**yaml_data)
            except Exception as e:
                print(f"⚠️  Warning: Could not load {config_path}: {e}")
                print("   Falling back to environment variables...")
        
        # Fall back to environment variables
        return cls()
    
    def validate_api_keys(self) -> tuple[bool, str]:
        """
        Validate that required API keys are present
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.default_provider == "gemini":
            if not self.gemini_api_key or self.gemini_api_key == "YOUR_GEMINI_API_KEY":
                return False, "Gemini API key is not set. Get one from https://aistudio.google.com/app/apikey"
        
        elif self.default_provider == "groq":
            if not self.groq_api_key or self.groq_api_key == "YOUR_GROQ_API_KEY":
                return False, "Groq API key is not set. Get one from https://console.groq.com/keys"
        
        return True, ""
    
    def get_provider_config(self, provider: Optional[str] = None) -> dict:
        """
        Get configuration for a specific provider
        
        Args:
            provider: Provider name (defaults to default_provider)
            
        Returns:
            Dictionary with api_key and model
        """
        provider = provider or self.default_provider
        
        if provider == "gemini":
            return {
                "api_key": self.gemini_api_key,
                "model": self.gemini_model
            }
        elif provider == "groq":
            return {
                "api_key": self.groq_api_key,
                "model": self.groq_model
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")


# Global settings instance
settings = Settings.from_yaml()
