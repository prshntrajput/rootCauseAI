"""
Groq Provider Implementation - Fixed for SDK 0.9.0
Uses Groq's ultra-fast inference API
"""

from typing import Dict, Any, Optional
import json


class GroqProvider:
    """
    Provider implementation for Groq's LLM API
    Supports: llama-3.3-70b-versatile, mixtral-8x7b-32768, etc.
    """
    
    def __init__(self, api_key: str, model: str):
        """Initialize Groq provider"""
        if not api_key:
            raise ValueError(f"GroqProvider requires an API key")
        
        self.api_key = api_key
        self.model = model
        self._validate_setup()
    
    def _validate_setup(self) -> None:
        """Initialize Groq client with minimal parameters"""
        try:
            # Import here to avoid issues
            from groq import Groq
            
            # Create client with only the API key
            # This avoids the 'proxies' parameter issue
            self.client = Groq(
                api_key=self.api_key
            )
            
        except TypeError as e:
            # If still failing, try environment variable method
            import os
            os.environ['GROQ_API_KEY'] = self.api_key
            from groq import Groq
            try:
                self.client = Groq()
            except:
                raise ValueError(f"Could not initialize Groq client: {e}")
        except Exception as e:
            raise ValueError(f"Failed to initialize Groq: {e}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """
        Generate text response using Groq
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            temperature: Randomness level
            max_tokens: Maximum output tokens
            
        Returns:
            LLMResponse with generated content
        """
        try:
            # Import here
            from .base_provider import LLMResponse
            
            # Create chat completion
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95
            )
            
            # Extract response data
            choice = response.choices[0]
            
            return LLMResponse(
                content=choice.message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                finish_reason=choice.finish_reason,
                raw_response=None
            )
            
        except Exception as e:
            raise Exception(f"Groq generation failed: {str(e)}")
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using Groq
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            schema: Optional JSON schema
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Add JSON instruction
            json_instruction = "\n\nRespond with valid JSON only. No markdown formatting."
            if schema:
                json_instruction += f"\n\nSchema:\n{json.dumps(schema, indent=2)}"
            
            full_user_prompt = f"{user_prompt}{json_instruction}"
            
            # Create chat completion with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": full_user_prompt
                    }
                ],
                temperature=0.1,  # Lower for structured output
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to clean up response
                content = content.strip()
                if content.startswith("```"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                
                return json.loads(content.strip())
                
        except Exception as e:
            raise Exception(f"Groq JSON generation failed: {str(e)}")
    
    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return "groq"
    
    def __repr__(self) -> str:
        return f"GroqProvider(model='{self.model}')"
