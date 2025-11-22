"""
AgentScope Decorator Utilities

Provides @trace decorator for automatic span creation.
"""
import functools
from typing import Callable, Optional

from opentelemetry import trace


def trace_function(name: Optional[str] = None):
    """
    Decorator to automatically create a span for a function.
    
    Usage:
        @trace
        def my_function(arg1, arg2):
            return result
        
        @trace(name="custom_span_name")
        def another_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        span_name = name if name else func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            
            with tracer.start_as_current_span(span_name) as span:
                # Optionally capture function arguments
                # span.set_attribute("function.args", str(args))
                # span.set_attribute("function.kwargs", str(kwargs))
                
                result = func(*args, **kwargs)
                
                return result
        
        return wrapper
    
    # Support both @trace and @trace(name="...")
    if callable(name):
        # Called as @trace (without parentheses)
        func = name
        name = None
        return decorator(func)
    else:
        # Called as @trace(name="...") (with parentheses)
        return decorator


class SpanContext:
    """
    Context manager for manual spans.
    
    Usage:
        with ag.span("operation_name") as span:
            span.set_attribute("key", "value")
            # Do work...
    """
    def __init__(self, name: str):
        self.name = name
        self.span = None
    
    def __enter__(self):
        tracer = trace.get_tracer(__name__)
        self.span = tracer.start_as_current_span(self.name).__enter__()
        return self._wrap_span(self.span)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)
    
    def _wrap_span(self, span):
        """Wrap span with convenience methods."""
        class SpanWrapper:
            def __init__(self, span):
                self._span = span
            
            def set_attribute(self, key: str, value):
                """Set a span attribute."""
                self._span.set_attribute(key, value)
                return self
            
            def set_metric(self, key: str, value: float):
                """Set a numeric metric."""
                self._span.set_attribute(f"metric.{key}", value)
                return self
        
        return SpanWrapper(span)


def span(name: str):
    """
    Create a manual span context.
    
    Usage:
        with ag.span("custom_operation") as span:
            span.set_attribute("user_id", "123")
            result = do_work()
            span.set_metric("result_count", len(result))
    """
    return SpanContext(name)
