"""Integration test for full workflow."""
import pytest
import agentscope as ag


def test_basic_workflow(temp_db):
    """Test basic ag.init() and tracing workflow."""
    # Initialize
    ag.init(mode="headless", db_path=temp_db)
    
    # Use decorator
    @ag.trace
    def test_function():
        return "success"
    
    result = test_function()
    assert result == "success"
