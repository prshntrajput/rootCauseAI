"""
Gemini Provider Implementation
Uses Google's Generative AI SDK for Gemini models
"""

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold
from .base_provider import BaseLLMProvider, LLMResponse
from typing import Dict, Any, Optional
import json


class GeminiProvider(BaseLLMProvider):
    """
    Provider implementation for Google's Gemini models
    Supports: gemini-2.0-flash-exp, gemini-1.5-pro, etc.
    """
    
    def _validate_setup(self) -> None:
        """Configure Gemini API"""
        try:
            genai.configure(api_key=self.api_key)
            # Create model instance
            self.client = genai.GenerativeModel(
                model_name=self.model,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {e}")
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """
        Generate text response using Gemini
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            temperature: Randomness level
            max_tokens: Maximum output tokens
            
        Returns:
            LLMResponse with generated content
        """
        try:
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Configure generation
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.95,
                top_k=40,
            )
            
            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract metadata
            try:
                tokens_used = response.usage_metadata.total_token_count
            except:
                tokens_used = 0
            
            try:
                finish_reason = str(response.candidates[0].finish_reason.name)
            except:
                finish_reason = "unknown"
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                tokens_used=tokens_used,
                finish_reason=finish_reason,
                raw_response=None  # Don't store large raw responses
            )
            
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")
    
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using Gemini
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            schema: Optional JSON schema
            
        Returns:
            Parsed JSON dictionary
        """
        try:
            # Add JSON instruction to prompt
            json_instruction = "\n\nYou must respond with valid JSON only. No markdown, no explanations."
            if schema:
                json_instruction += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"
            
            full_prompt = f"{system_prompt}\n\n{user_prompt}{json_instruction}"
            
            # Configure for JSON output
            generation_config = GenerationConfig(
                temperature=0.1,  # Lower temperature for structured output
                max_output_tokens=2000,
                response_mime_type="application/json"
            )
            
            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Parse JSON
            try:
                return json.loads(response.text)
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                text = response.text.strip()
                if text.startswith("```"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                
                return json.loads(text.strip())
                
        except Exception as e:
            raise Exception(f"Gemini JSON generation failed: {str(e)}")
