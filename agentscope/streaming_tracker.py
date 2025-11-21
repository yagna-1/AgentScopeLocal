"""
Streaming response tracking utilities for LLM calls.

This module provides tools to track streaming LLM responses, including
chunk-by-chunk timing, streaming TTFT, inter-chunk latency, and per-token metrics.
"""
import time
from typing import Optional, List


class StreamingTracker:
    """
    Track streaming LLM response metrics.
    
    Usage:
        with tracer.start_as_current_span("llm_call") as span:
            tracker = StreamingTracker(span)
            
            for chunk in stream:
                tracker.record_chunk(chunk_text, token_count)
            
            tracker.finalize()
    """
    
    def __init__(self, span):
        """
        Initialize streaming tracker.
        
        Args:
            span: OpenTelemetry span to attach metrics to
        """
        self.span = span
        self.start_time = time.time()
        self.first_chunk_time: Optional[float] = None
        self.chunk_times: List[float] = []
        self.chunks: List[str] = []
        self.total_tokens = 0
        self.end_time: Optional[float] = None
    
    def record_chunk(self, chunk_text: str, token_count: Optional[int] = None):
        """
        Record a streaming chunk.
        
        Args:
            chunk_text: Text content of the chunk
            token_count: Optional number of tokens in this chunk
        """
        current_time = time.time()
        
        # First chunk = Streaming TTFT
        if self.first_chunk_time is None:
            self.first_chunk_time = current_time
            ttft_ms = (current_time - self.start_time) * 1000
            self.span.set_attribute("llm.streaming.ttft_ms", round(ttft_ms, 2))
        
        # Record chunk timing
        self.chunk_times.append(current_time)
        self.chunks.append(chunk_text)
        
        # Track tokens if provided
        if token_count is not None:
            self.total_tokens += token_count
        else:
            # Rough estimate: ~4 chars per token for English
            estimated_tokens = max(1, len(chunk_text) // 4)
            self.total_tokens += estimated_tokens
    
    def finalize(self):
        """
        Calculate and record final streaming metrics.
        
        Records:
            - llm.streaming.enabled: Boolean flag for streaming
            - llm.streaming.chunk_count: Number of chunks received
            - llm.streaming.total_time_ms: Total streaming duration
            - llm.streaming.avg_inter_chunk_ms: Average time between chunks
            - llm.streaming.per_token_ms: Average milliseconds per token
            - llm.tokens_per_second: Overall throughput
        """
        self.end_time = time.time()
        total_time_ms = (self.end_time - self.start_time) * 1000
        
        # Mark as streaming
        self.span.set_attribute("llm.streaming.enabled", True)
        self.span.set_attribute("llm.streaming.chunk_count", len(self.chunks))
        self.span.set_attribute("llm.streaming.total_time_ms", round(total_time_ms, 2))
        
        # Calculate inter-chunk latency
        if len(self.chunk_times) > 1:
            inter_chunk_latencies = [
                (self.chunk_times[i] - self.chunk_times[i-1]) * 1000
                for i in range(1, len(self.chunk_times))
            ]
            avg_inter_chunk = sum(inter_chunk_latencies) / len(inter_chunk_latencies)
            self.span.set_attribute("llm.streaming.avg_inter_chunk_ms", round(avg_inter_chunk, 2))
            
            # Store min/max for analysis
            self.span.set_attribute("llm.streaming.min_inter_chunk_ms", round(min(inter_chunk_latencies), 2))
            self.span.set_attribute("llm.streaming.max_inter_chunk_ms", round(max(inter_chunk_latencies), 2))
        
        # Per-token latency
        if self.total_tokens > 0:
            per_token_ms = total_time_ms / self.total_tokens
            self.span.set_attribute("llm.streaming.per_token_ms", round(per_token_ms, 2))
            
            # Also set completion tokens for consistency
            self.span.set_attribute("gen_ai.usage.completion_tokens", self.total_tokens)
        
        # Overall tokens per second
        if total_time_ms > 0 and self.total_tokens > 0:
            tps = (self.total_tokens / total_time_ms) * 1000
            self.span.set_attribute("llm.tokens_per_second", round(tps, 2))
            
            # Also set generation time for consistency with non-streaming
            self.span.set_attribute("llm.generation_time_ms", round(total_time_ms, 2))
    
    def get_metrics(self) -> dict:
        """
        Get current streaming metrics as a dictionary.
        
        Returns:
            Dictionary containing streaming metrics
        """
        metrics = {
            'streaming_enabled': True,
            'chunk_count': len(self.chunks),
            'total_tokens': self.total_tokens,
        }
        
        if self.first_chunk_time:
            metrics['ttft_ms'] = round((self.first_chunk_time - self.start_time) * 1000, 2)
        
        if self.end_time:
            total_time_ms = (self.end_time - self.start_time) * 1000
            metrics['total_time_ms'] = round(total_time_ms, 2)
            
            if self.total_tokens > 0:
                metrics['tokens_per_second'] = round((self.total_tokens / total_time_ms) * 1000, 2)
                metrics['per_token_ms'] = round(total_time_ms / self.total_tokens, 2)
        
        if len(self.chunk_times) > 1:
            inter_chunk_latencies = [
                (self.chunk_times[i] - self.chunk_times[i-1]) * 1000
                for i in range(1, len(self.chunk_times))
            ]
            metrics['avg_inter_chunk_ms'] = round(sum(inter_chunk_latencies) / len(inter_chunk_latencies), 2)
        
        return metrics
