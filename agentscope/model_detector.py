"""
Universal LLM Provider Detection
Identifies the provider and model from OpenTelemetry span attributes or API endpoints.
"""
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class ModelDetector:
    """Detects LLM provider and normalizes model information"""
    
    # Provider detection patterns
    PROVIDER_PATTERNS = {
        'ollama': [
            r'localhost:11434',
            r'127\.0\.0\.1:11434',
            r'/ollama',
        ],
        'lm_studio': [
            r'localhost:1234',
            r'/lm-studio',
        ],
        'openai': [
            r'api\.openai\.com',
            r'/openai/',
        ],
        'azure_openai': [
            r'\.openai\.azure\.com',
            r'/openai/deployments/',
        ],
        'anthropic': [
            r'api\.anthropic\.com',
        ],
        'localai': [
            r'/localai',
            r'localhost:8080',
        ],
    }
    
    def detect_provider(self, attributes: Dict[str, Any]) -> str:
        """
        Detect LLM provider from span attributes.
        
        Priority:
        1. gen_ai.system attribute (official OTel convention)
        2. URL pattern matching
        3. Model name inference
        """
        # Check official attribute
        if 'gen_ai.system' in attributes:
            return attributes['gen_ai.system'].lower()
        
        # Check for base URL or endpoint
        url_fields = ['server.address', 'url.full', 'http.url', 'base_url']
        for field in url_fields:
            if field in attributes:
                provider = self._detect_from_url(attributes[field])
                if provider:
                    return provider
        
        # Infer from model name
        if 'gen_ai.request.model' in attributes:
            model = attributes['gen_ai.request.model']
            return self._infer_from_model_name(model)
        
        return 'unknown'
    
    def _detect_from_url(self, url: str) -> Optional[str]:
        """Detect provider from URL patterns"""
        url_lower = url.lower()
        
        for provider, patterns in self.PROVIDER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return provider
        
        return None
    
    def _infer_from_model_name(self, model: str) -> str:
        """Infer provider from model name patterns"""
        model_lower = model.lower()
        
        if model_lower.startswith('gpt-'):
            return 'openai'
        elif 'claude' in model_lower:
            return 'anthropic'
        elif any(x in model_lower for x in ['llama', 'mistral', 'mixtral', 'phi']):
            return 'ollama'  # Common local models
        elif 'gemini' in model_lower or 'palm' in model_lower:
            return 'google'
        
        return 'unknown'
    
    def normalize_model_name(self, model: str, provider: str) -> str:
        """
        Normalize model name for consistent display.
        Example: 'gpt-4-0613' -> 'GPT-4'
        """
        if provider == 'openai':
            if 'gpt-4' in model:
                return 'GPT-4'
            elif 'gpt-3.5' in model:
                return 'GPT-3.5'
            elif 'gpt-4o' in model:
                return 'GPT-4o'
            elif 'o1' in model or 'o3' in model:
                return model.upper()
        
        elif provider == 'anthropic':
            if 'claude-3-opus' in model:
                return 'Claude 3 Opus'
            elif 'claude-3-sonnet' in model:
                return 'Claude 3 Sonnet'
            elif 'claude-3-haiku' in model:
                return 'Claude 3 Haiku'
        
        elif provider == 'ollama':
            # Keep original name for local models
            return model
        
        return model
    
    def extract_cost_info(self, attributes: Dict[str, Any], provider: str) -> Dict[str, float]:
        """Extract token usage and calculate cost (if applicable)"""
        usage = {}
        
        # Extract token counts
        if 'gen_ai.usage.prompt_tokens' in attributes:
            usage['prompt_tokens'] = int(attributes['gen_ai.usage.prompt_tokens'])
        
        if 'gen_ai.usage.completion_tokens' in attributes:
            usage['completion_tokens'] = int(attributes['gen_ai.usage.completion_tokens'])
        
        if 'gen_ai.usage.total_tokens' in attributes:
            usage['total_tokens'] = int(attributes['gen_ai.usage.total_tokens'])
        
        # Add reasoning tokens for o1/o3 models
        if 'gen_ai.usage.reasoning_tokens' in attributes:
            usage['reasoning_tokens'] = int(attributes['gen_ai.usage.reasoning_tokens'])
        
        # Calculate cost (only for paid providers)
        if provider in ['openai', 'anthropic', 'google']:
            from .model_registry import ModelRegistry
            registry = ModelRegistry()
            model = attributes.get('gen_ai.request.model', '')
            pricing = registry.get_pricing(model, provider)
            
            if pricing and 'prompt_tokens' in usage and 'completion_tokens' in usage:
                cost = (
                    usage['prompt_tokens'] * pricing['input_cost_per_1k'] / 1000 +
                    usage['completion_tokens'] * pricing['output_cost_per_1k'] / 1000
                )
                usage['estimated_cost_usd'] = round(cost, 6)
        
        return usage


# Singleton instance
detector = ModelDetector()
