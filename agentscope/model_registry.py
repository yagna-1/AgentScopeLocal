"""
Model Registry
Stores metadata about known LLM models including embedding dimensions,
token limits, and pricing information.
"""
from typing import Dict, Optional, Any


class ModelRegistry:
    """Registry of known LLM models and their metadata"""
    
    # Embedding dimensions for different models
    EMBEDDING_DIMS = {
        # OpenAI
        'text-embedding-3-small': 1536,
        'text-embedding-3-large': 3072,
        'text-embedding-ada-002': 1536,
        
        # Open source models (common in local setups)
        'bge-base': 768,
        'bge-large': 1024,
        'bge-small': 384,
        'all-minilm-l6-v2': 384,
        'all-minilm-l12-v2': 384,
        'all-mpnet-base-v2': 768,
        'gte-small': 384,
        'gte-base': 768,
        'gte-large': 1024,
        'e5-small': 384,
        'e5-base': 768,
        'e5-large': 1024,
        
        # Sentence transformers
        'sentence-transformers/all-minilm-l6-v2': 384,
        'sentence-transformers/all-mpnet-base-v2': 768,
    }
    
    # Token limits for LLMs
    TOKEN_LIMITS = {
        # OpenAI
        'gpt-4': 8192,
        'gpt-4-32k': 32768,
        'gpt-4-turbo': 128000,
        'gpt-4o': 128000,
        'gpt-3.5-turbo': 16385,
        'o1-preview': 128000,
        'o1-mini': 128000,
        
        # Anthropic
        'claude-3-opus': 200000,
        'claude-3-sonnet': 200000,
        'claude-3-haiku': 200000,
        'claude-2': 100000,
        
        # Common local models
        'llama-2-7b': 4096,
        'llama-2-13b': 4096,
        'llama-2-70b': 4096,
        'llama-3-8b': 8192,
        'llama-3-70b': 8192,
        'mistral-7b': 8192,
        'mixtral-8x7b': 32768,
        'phi-2': 2048,
        'phi-3': 4096,
    }
    
    # Pricing (USD per 1K tokens)
    PRICING = {
        # OpenAI GPT-4
        'gpt-4': {'input_cost_per_1k': 0.03, 'output_cost_per_1k': 0.06},
        'gpt-4-32k': {'input_cost_per_1k': 0.06, 'output_cost_per_1k': 0.12},
        'gpt-4-turbo': {'input_cost_per_1k': 0.01, 'output_cost_per_1k': 0.03},
        'gpt-4o': {'input_cost_per_1k': 0.005, 'output_cost_per_1k': 0.015},
        
        # OpenAI GPT-3.5
        'gpt-3.5-turbo': {'input_cost_per_1k': 0.0005, 'output_cost_per_1k': 0.0015},
        
        # Anthropic Claude
        'claude-3-opus': {'input_cost_per_1k': 0.015, 'output_cost_per_1k': 0.075},
        'claude-3-sonnet': {'input_cost_per_1k': 0.003, 'output_cost_per_1k': 0.015},
        'claude-3-haiku': {'input_cost_per_1k': 0.00025, 'output_cost_per_1k': 0.00125},
    }
    
    def get_embedding_dim(self, model_name: str) -> int:
        """
        Get embedding dimension for a model.
        Returns default of 1536 if unknown.
        """
        # Direct lookup
        if model_name in self.EMBEDDING_DIMS:
            return self.EMBEDDING_DIMS[model_name]
        
        # Fuzzy match
        model_lower = model_name.lower()
        for key, dim in self.EMBEDDING_DIMS.items():
            if key in model_lower or model_lower in key:
                return dim
        
        # Default to OpenAI standard
        return 1536
    
    def get_token_limit(self, model_name: str) -> Optional[int]:
        """Get context window size for a model"""
        # Direct lookup
        if model_name in self.TOKEN_LIMITS:
            return self.TOKEN_LIMITS[model_name]
        
        # Fuzzy match
        model_lower = model_name.lower()
        for key, limit in self.TOKEN_LIMITS.items():
            if key in model_lower:
                return limit
        
        return None
    
    def get_pricing(self, model_name: str, provider: str) -> Optional[Dict[str, float]]:
        """Get pricing information for a model"""
        # Local providers are free
        if provider in ['ollama', 'lm_studio', 'llama_cpp', 'localai']:
            return None
        
        # Direct lookup
        if model_name in self.PRICING:
            return self.PRICING[model_name]
        
        # Fuzzy match
        model_lower = model_name.lower()
        for key, pricing in self.PRICING.items():
            if key in model_lower:
                return pricing
        
        return None
    
    def get_model_family(self, model_name: str) -> str:
        """Categorize model into family (GPT, Claude, Llama, etc.)"""
        model_lower = model_name.lower()
        
        if 'gpt' in model_lower:
            return 'GPT'
        elif 'claude' in model_lower:
            return 'Claude'
        elif 'llama' in model_lower:
            return 'Llama'
        elif 'mistral' in model_lower or 'mixtral' in model_lower:
            return 'Mistral'
        elif 'phi' in model_lower:
            return 'Phi'
        elif 'gemini' in model_lower:
            return 'Gemini'
        
        return 'Other'
    
    def register_custom_model(
        self,
        name: str,
        embedding_dim: Optional[int] = None,
        token_limit: Optional[int] = None,
        pricing: Optional[Dict[str, float]] = None
    ):
        """
        Register a custom model at runtime.
        Useful for proprietary or newly released models.
        """
        if embedding_dim:
            self.EMBEDDING_DIMS[name] = embedding_dim
        
        if token_limit:
            self.TOKEN_LIMITS[name] = token_limit
        
        if pricing:
            self.PRICING[name] = pricing


# Singleton instance
registry = ModelRegistry()
