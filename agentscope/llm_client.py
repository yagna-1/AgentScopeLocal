"""
Universal LLM Client
Supports calling any LLM provider (OpenAI, Anthropic, Ollama, etc.)
Used for Time Travel feature to re-run prompts with modifications.
"""
from typing import Dict, List, Any, Optional
import os


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
            self.clients['openai'] = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except ImportError:
            pass
        
        # Anthropic
        try:
            from anthropic import Anthropic
            self.clients['anthropic'] = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        except ImportError:
            pass
        
        # Ollama (via OpenAI-compatible API)
        try:
            from openai import OpenAI
            self.clients['ollama'] = OpenAI(
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
        return provider.lower() in self.clients


# Singleton instance
llm_client = UniversalLLMClient()
