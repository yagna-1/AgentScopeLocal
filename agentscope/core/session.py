"""
AgentScope Session Manager

Replaces the standalone server approach with an in-process session manager.
Handles telemetry collection, storage, and optional UI launching.
"""
import threading
import atexit
from typing import Optional, Literal
from pathlib import Path

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource

from ..exporter import SQLiteSpanExporter
from ..ui.terminal import TerminalUI


class Session:
    """
    Manages the AgentScope session lifecycle.
    
    Usage:
        session = Session(mode="terminal")
        session.start()
        # Your code runs here...
        session.stop()
    """
    
    _instance: Optional['Session'] = None
    _lock = threading.Lock()
    
    def __init__(
        self,
        mode: Literal["terminal", "web", "headless"] = "terminal",
        db_path: str = "agentscope_traces.db",
        service_name: str = "agentscope_app",
        port: int = 8000,
        auto_open_browser: bool = True
    ):
        self.mode = mode
        self.db_path = db_path
        self.service_name = service_name
        self.port = port
        self.auto_open_browser = auto_open_browser
        
        # Components
        self.tracer_provider: Optional[TracerProvider] = None
        self.exporter: Optional[SQLiteSpanExporter] = None
        self.terminal_ui: Optional[TerminalUI] = None
        self.web_server: Optional[threading.Thread] = None
        
        self._active = False
    
    @classmethod
    def get_instance(cls) -> Optional['Session']:
        """Get the current session instance."""
        return cls._instance
    
    @classmethod
    def set_instance(cls, session: 'Session'):
        """Set the global session instance."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.stop()
            cls._instance = session
    
    def start(self):
        """Start the session and initialize telemetry."""
        if self._active:
            return
        
        # Initialize OpenTelemetry
        resource = Resource.create({"service.name": self.service_name})
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Setup exporter with processor wrapper
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        
        self.exporter = SQLiteSpanExporter(db_path=self.db_path)
        processor = SimpleSpanProcessor(self.exporter)
        self.tracer_provider.add_span_processor(processor)
        
        # Set as global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Initialize UI based on mode
        if self.mode == "terminal":
            self.terminal_ui = TerminalUI()
            self.terminal_ui.start()
            self.exporter.set_callback(self.terminal_ui.on_span_end)
        
        elif self.mode == "web":
            self._start_web_server()
        
        # headless mode: just collect data, no UI
        
        self._active = True
        
        # Register cleanup on exit
        atexit.register(self.stop)
    
    def stop(self):
        """Stop the session and cleanup resources."""
        if not self._active:
            return
        
        # Shutdown terminal UI
        if self.terminal_ui:
            self.terminal_ui.stop()
        
        # Shutdown web server
        if self.web_server and self.web_server.is_alive():
            # Signal server to stop (implementation depends on web server)
            pass
        
        # Flush and close exporter
        if self.exporter:
            self.exporter.shutdown()
        
        # Shutdown tracer provider
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        
        self._active = False
    
    def _start_web_server(self):
        """Start the web UI in a background thread."""
        def run_server():
            import sys
            import os
            # Add parent directory to path to import api
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            import api
            import uvicorn
            
            uvicorn.run(
                api.app,
                host="127.0.0.1",
                port=self.port,
                log_level="error"  # Quiet mode
            )
        
        self.web_server = threading.Thread(target=run_server, daemon=True)
        self.web_server.start()
        
        # Auto-open browser
        if self.auto_open_browser:
            import webbrowser
            import time
            time.sleep(1)  # Wait for server to start
            webbrowser.open(f"http://localhost:{self.port}")
    
    def get_tracer(self, name: str = __name__):
        """Get a tracer instance."""
        return trace.get_tracer(name)
