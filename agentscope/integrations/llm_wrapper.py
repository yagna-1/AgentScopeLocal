"""
AgentScope LLM Wrapper

Unified interface for all LLM providers with automatic tracing.
"""
from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass

from opentelemetry import trace

from ..llm_client import UniversalLLMClient
from ..performance_tracker import PerformanceTracker
from ..streaming_tracker import StreamingTracker
from ..resource_monitor import ResourceMonitor


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    text: str
    usage: Dict[str, int]
    metrics: Dict[str, float]
    raw_response: Any = None


class LLMWrapper:
    """
    High-level wrapper for LLM calls with automatic tracing.
    
    Usage:
        from agentscope import llm
        
        response = llm.chat("ollama/qwen2.5:0.5b", "What is AI?")
        print(response.text)
    """
    
    def __init__(self):
        self.client = UniversalLLMClient()
    
    def chat(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Make an LLM call with automatic tracing.
        
        Args:
            model: Model identifier (e.g., "ollama/qwen2.5:0.5b", "gpt-4", "claude-3-sonnet")
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMResponse with text,usage, and metrics
        """
        # Parse model string
        if "/" in model:
            provider, model_name = model.split("/", 1)
        else:
            # Auto-detect provider
            provider = self._detect_provider(model)
            model_name = model
        
        # Get tracer
        tracer = trace.get_tracer(__name__)
        
        # Create span
        with tracer.start_as_current_span(f"{provider}_call") as span:
            # Set attributes
            span.set_attribute("gen_ai.system", provider)
            span.set_attribute("gen_ai.request.model", model_name)
            span.set_attribute("gen_ai.prompt", prompt)
            span.set_attribute("gen_ai.request.temperature", temperature)
            span.set_attribute("gen_ai.request.max_tokens", max_tokens)
            
            # Resource monitoring
            ResourceMonitor.capture(span)
            
            # Convert prompt to messages format
            messages = [{"role": "user", "content": prompt}]
            
            if stream:
                return self._chat_streaming(
                    span, provider, model_name, messages,
                    temperature, max_tokens, **kwargs
                )
            else:
                return self._chat_sync(
                    span, provider, model_name, messages,
                    temperature, max_tokens, **kwargs
                )
    
    def _chat_sync(
        self, span, provider: str, model: str, messages: list,
        temperature: float, max_tokens: int, **kwargs
    ) -> LLMResponse:
        """Synchronous (non-streaming) LLM call."""
        # Performance tracking
        tracker = PerformanceTracker(span)
        
        # Make the call
        response = self.client.call(
            provider=provider,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Extract response text
        response_text = response.get("content", "")
        
        # Track performance
        usage = response.get("usage", {})
        tracker.mark_first_token()
        total_tokens = usage.get("total_tokens", usage.get("completion_tokens", 0))
        tracker.set_tokens(total_tokens)
        tracker.finalize()
        
        # Set span attributes
        span.set_attribute("gen_ai.completion", response_text)
        span.set_attribute("gen_ai.usage.prompt_tokens", usage.get("prompt_tokens", 0))
        span.set_attribute("gen_ai.usage.completion_tokens", usage.get("completion_tokens", 0))
        span.set_attribute("gen_ai.usage.total_tokens", usage.get("total_tokens", 0))
        
        # Build response object
        metrics = {
            "ttft_ms": span.attributes.get("llm.ttft_ms", 0),
            "tokens_per_second": span.attributes.get("llm.tokens_per_second", 0),
            "generation_time_ms": span.attributes.get("llm.generation_time_ms", 0),
        }
        
        return LLMResponse(
            text=response_text,
            usage=usage,
            metrics=metrics,
            raw_response=response
        )
    
    def _chat_streaming(
        self, span, provider: str, model: str, messages: list,
        temperature: float, max_tokens: int, **kwargs
    ) -> LLMResponse:
        """Streaming LLM call with live output."""
        from ..core.session import Session
        
        # Streaming tracker
        tracker = StreamingTracker(span)
        
        # Get terminal UI if active
        session = Session.get_instance()
        terminal_ui = session.terminal_ui if session else None
        
        # Make streaming call
        stream = self.client.call_streaming(
            provider=provider,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Collect response
        full_text = ""
        
        for chunk in stream:
            chunk_text = chunk.get("content", "")
            if chunk_text:
                full_text += chunk_text
                tracker.record_chunk(chunk_text)
                
                # Print to terminal if UI is active
                if terminal_ui:
                    terminal_ui.print_streaming_chunk(chunk_text)
        
        # Finalize tracking
        tracker.finalize()
        
        # Print newline after streaming
        if terminal_ui:
            terminal_ui.console.print()
        
        # Set span attributes
        span.set_attribute("gen_ai.completion", full_text)
        
        # Build response
        metrics = {
            "streaming_ttft_ms": span.attributes.get("llm.streaming.ttft_ms", 0),
            "streaming_chunks": span.attributes.get("llm.streaming.chunk_count", 0),
            "tokens_per_second": span.attributes.get("llm.tokens_per_second", 0),
        }
        
        return LLMResponse(
            text=full_text,
            usage={},  # Streaming doesn't always return usage
            metrics=metrics,
            raw_response={}
        )
    
    def _detect_provider(self, model: str) -> str:
        """Auto-detect provider from model name."""
        model_lower = model.lower()
        
        if model_lower.startswith("gpt-"):
            return "openai"
        elif "claude" in model_lower:
            return "anthropic"
        else:
            return "ollama"  # Default to local


# Singleton instance
llm = LLMWrapper()
