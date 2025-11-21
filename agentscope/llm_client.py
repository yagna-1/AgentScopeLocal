"""
Universal LLM Client
Supports calling any LLM provider (OpenAI, Anthropic, Ollama, etc.)
Used for Time Travel feature to re-run prompts with modifications.
"""
from typing import Dict, List, Any, Optional
import os
import requests


class UniversalLLMClient:
    """Universal client that can call any LLM provider"""
    
    def __init__(self):
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize available clients"""
        # OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:  # Only initialize if API key is present
                self.clients['openai'] = OpenAI(api_key=api_key)
        except ImportError:
            pass
        
        # Anthropic
        try:
            from anthropic import Anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:  # Only initialize if API key is present
                self.clients['anthropic'] = Anthropic(api_key=api_key)
        except ImportError:
            pass
        
        # Ollama (via OpenAI-compatible API - kept for backward compatibility)
        # NOTE: This is not actively used since we have native Ollama support
        # but keeping it here in case users want to use the OpenAI-compatible endpoint
        try:
            from openai import OpenAI
            self.clients['ollama_openai'] = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"  # Ollama doesn't need a real key
            )
        except ImportError:
            pass
    
    def call(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Universal call method that routes to the appropriate provider.
        
        Args:
            provider: Provider name (openai, anthropic, ollama, etc.)
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Dict with 'content', 'usage', and 'model' fields
        """
        provider_lower = provider.lower()
        
        if provider_lower in ['openai', 'ollama', 'lm_studio']:
            return self._call_openai_compatible(provider_lower, model, messages, temperature, max_tokens, **kwargs)
        elif provider_lower == 'anthropic':
            return self._call_anthropic(model, messages, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _call_openai_compatible(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Call OpenAI or OpenAI-compatible APIs (Ollama, LM Studio)"""
        # Special handling for Ollama - use native API
        if provider == 'ollama':
            return self._call_ollama_native(model, messages, temperature, max_tokens, **kwargs)
        
        if provider not in self.clients:
            raise RuntimeError(f"{provider} client not initialized. Check API key or installation.")
        
        client = self.clients[provider]
        
        # Prepare parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
        
        # Add any extra parameters
        params.update(kwargs)
        
        # Make the call
        response = client.chat.completions.create(**params)
        
        # Extract and normalize response
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }
    
    def _call_ollama_native(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Call Ollama using its native HTTP API"""
        
        # Convert messages to prompt  (simple concatenation for now)
        # Ollama's /api/generate endpoint expects a single prompt string,
        # not a list of messages like OpenAI.
        # For a more robust solution, consider using /api/chat for Ollama.
        # For now, we'll concatenate for /api/generate.
        prompt_parts = []
        for msg in messages:
            if msg['role'] == 'system':
                prompt_parts.append(f"System: {msg['content']}")
            elif msg['role'] == 'user':
                prompt_parts.append(f"User: {msg['content']}")
            elif msg['role'] == 'assistant':
                prompt_parts.append(f"Assistant: {msg['content']}")
        prompt = "\n".join(prompt_parts)
        
        # Build request
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            data["options"]["num_predict"] = max_tokens
        
        # Add any extra parameters that map to Ollama options
        # This is a basic mapping; a more comprehensive one might be needed
        for k, v in kwargs.items():
            if k == 'top_p':
                data['options']['top_p'] = v
            elif k == 'num_ctx':
                data['options']['num_ctx'] = v
            # Add other Ollama-specific options as needed
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            completion = result.get("response", "")
            prompt_tokens = result.get("prompt_eval_count", 0)
            completion_tokens = result.get("eval_count", 0)
            
            return {
                "content": completion,
                "model": model,
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                "finish_reason": "stop", # Ollama /api/generate doesn't explicitly return this
            }
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama not running. Start with: ollama serve")
        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {str(e)}")
    
    def _call_anthropic(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        if 'anthropic' not in self.clients:
            raise RuntimeError("Anthropic client not initialized. Check ANTHROPIC_API_KEY.")
        
        client = self.clients['anthropic']
        
        # Anthropic requires max_tokens
        if not max_tokens:
            max_tokens = 1024
        
        # Prepare parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add any extra parameters
        params.update(kwargs)
        
        # Make the call
        response = client.messages.create(**params)
        
        # Extract and normalize response
        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            "finish_reason": response.stop_reason,
        }
    
    def is_available(self, provider: str) -> bool:
        """Check if a provider client is available"""
        provider_lower = provider.lower()
        
        # Ollama has special handling via native API
        if provider_lower == 'ollama':
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                return response.status_code == 200
            except:
                return False
        
        return provider_lower in self.clients


# Singleton instance
llm_client = UniversalLLMClient()
