"""Unit tests for trace decorator."""
import pytest
from agentscope.core.decorators import trace_function, span


def test_trace_decorator():
    """Test @trace decorator wraps function."""
    @trace_function
    def sample_function():
        return "test_result"
    
    result = sample_function()
    assert result == "test_result"


def test_trace_decorator_with_name():
    """Test @trace decorator with custom name."""
    @trace_function(name="custom_span")
    def sample_function():
        return "test_result"
    
    result = sample_function()
    assert result == "test_result"


def test_span_context_manager():
    """Test manual span creation."""
    with span("test_operation") as s:
        s.set_attribute("test_key", "test_value")
        # Should not raise
        pass
