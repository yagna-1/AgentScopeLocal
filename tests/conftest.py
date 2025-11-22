"""Pytest configuration and fixtures for AgentScope tests."""
import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "model": "qwen2.5:0.5b",
        "content": "This is a test response.",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
