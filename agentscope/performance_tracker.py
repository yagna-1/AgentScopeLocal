"""
Performance tracking utilities for LLM calls.

This module provides tools to track Time to First Token (TTFT),
tokens per second (TPS), and total generation time for LLM inference.
"""
import time
from typing import Optional


class PerformanceTracker:
    """
    Track performance metrics for LLM calls.
    
    Usage:
        with tracer.start_as_current_span("llm_call") as span:
            tracker = PerformanceTracker(span)
            
            # ... make LLM call ...
            
            tracker.mark_first_token()  # When first token arrives
            tracker.increment_tokens(count)  # For each token
            
            tracker.finalize()  # At the end
    """
    
    def __init__(self, span):
        """
        Initialize performance tracker.
        
        Args:
            span: OpenTelemetry span to attach metrics to
        """
        self.span = span
        self.start_time = time.time()
        self.first_token_time: Optional[float] = None
        self.tokens_generated = 0
        self.end_time: Optional[float] = None
    
    def mark_first_token(self):
        """
        Mark when the first token was received.
        Calculates and records Time to First Token (TTFT).
        """
        if self.first_token_time is None:
            self.first_token_time = time.time()
            ttft_ms = (self.first_token_time - self.start_time) * 1000
            self.span.set_attribute("llm.ttft_ms", round(ttft_ms, 2))
    
    def increment_tokens(self, count: int = 1):
        """
        Track token generation.
        
        Args:
            count: Number of tokens generated (default 1)
        """
        self.tokens_generated += count
    
    def set_tokens(self, count: int):
        """
        Set total token count (for non-streaming responses).
        
        Args:
            count: Total number of tokens generated
        """
        self.tokens_generated = count
    
    def finalize(self):
        """
        Calculate and record final performance metrics.
        
        Records:
            - llm.generation_time_ms: Total time from start to finish
            - llm.tokens_per_second: Throughput (tokens/second)
        """
        self.end_time = time.time()
        generation_time_ms = (self.end_time - self.start_time) * 1000
        
        self.span.set_attribute("llm.generation_time_ms", round(generation_time_ms, 2))
        
        # Calculate tokens per second
        if self.tokens_generated > 0 and generation_time_ms > 0:
            tps = (self.tokens_generated / generation_time_ms) * 1000
            self.span.set_attribute("llm.tokens_per_second", round(tps, 2))
    
    def get_metrics(self) -> dict:
        """
        Get current metrics as a dictionary.
        
        Returns:
            Dictionary containing performance metrics
        """
        metrics = {}
        
        if self.first_token_time:
            metrics['ttft_ms'] = round((self.first_token_time - self.start_time) * 1000, 2)
        
        if self.end_time:
            generation_time_ms = (self.end_time - self.start_time) * 1000
            metrics['generation_time_ms'] = round(generation_time_ms, 2)
            
            if self.tokens_generated > 0:
                metrics['tokens_per_second'] = round(
                    (self.tokens_generated / generation_time_ms) * 1000, 2
                )
        
        metrics['tokens_generated'] = self.tokens_generated
        
        return metrics
