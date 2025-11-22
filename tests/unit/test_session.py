"""Unit tests for Session manager."""
import pytest
from agentscope.core.session import Session


def test_session_initialization(temp_db):
    """Test session can be initialized."""
    session = Session(
        mode="headless",
        db_path=temp_db,
        service_name="test_service"
    )
    
    assert session.mode == "headless"
    assert session.db_path == temp_db
    assert session.service_name == "test_service"


def test_session_singleton():
    """Test session singleton pattern."""
    session1 = Session(mode="headless")
    Session.set_instance(session1)
    
    session2 = Session.get_instance()
    
    assert session1 is session2
