"""
AgentScope Local - Universal AI Debugging Flight Recorder

New Package API (V1.5+):
    import agentscope as ag
    
    ag.init()  # Terminal mode
    response = ag.llm.chat("ollama/qwen2.5:0.5b", "What is AI?")
    
    @ag.trace
    def my_function():
        pass

Legacy API (V1 - Still Supported):
   from agentscope.instrumentation import setup_instrumentation
    setup_instrumentation(...)
"""

__version__ = "1.5.0"

# ============================================================================
# Legacy API (V1) - Backward Compatibility
# ============================================================================
from .instrumentation import setup_instrumentation
from .model_detector import detector
from .model_registry import registry
from .rag_logger import log_embedding

# ============================================================================
# New Package API (V1.5+)
# ============================================================================
from .core.session import Session
from .core.decorators import trace_function as trace, span
from .integrations.llm_wrapper import llm

# Global session instance
_session: Session = None


def init(
    mode: str = "terminal",
    db_path: str = "agentscope_traces.db",
    service_name: str = "agentscope_app",
    port: int = 8000
):
    """
    Initialize AgentScope.
    
    Args:
        mode: "terminal" (default), "web", or "headless"
        db_path: Path to SQLite database
        service_name: Name for this service
        port: Port for web UI (if mode="web")
    
    Example:
        import agentscope as ag
        ag.init()  # Terminal mode
        
        # or
        ag.init(mode="web", port=8000)
    """
    global _session
    
    _session = Session(
        mode=mode,
        db_path=db_path,
        service_name=service_name,
        port=port
    )
    _session.start()
    Session.set_instance(_session)
    
    return _session


class WebUI:
    """Helper class for web UI operations."""
    
    @staticmethod
    def open(port: int = 8000):
        """
        Open the web UI in browser.
        
        If session is running in terminal mode, this will
        launch the web server in a background thread.
        """
        import webbrowser
        
        session = Session.get_instance()
        
        if session and session.mode == "terminal":
            # Start web server in background
            session._start_web_server()
        
        # Open browser
        webbrowser.open(f"http://localhost:{port}")


# Web UI helper
web = WebUI()


# Convenience function to log embeddings (RAG)
def log_rag_embedding(text: str, vector: list, type: str = "document", metadata: dict = None):
    """
    Log an embedding for RAG debugging.
    
    Args:
        text: The text that was embedded
        vector: The embedding vector
        type: "document" or "query"
        metadata: Optional metadata dict
    """
    session = Session.get_instance()
    db_path = session.db_path if session else "agentscope_traces.db"
    
    log_embedding(
        db_path=db_path,
        text=text,
        vector=vector,
        model_name="default",
        metadata=metadata or {},
        vector_type=type
    )


# ============================================================================
# Exports
# ============================================================================
__all__ = [
    # New API
    'init',
    'trace',
    'span',
    'llm',
    'web',
    'log_rag_embedding',
    
    # Legacy API
    'setup_instrumentation',
    'detector',
    'registry',
    'log_embedding',
]
