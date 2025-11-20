"""
AgentScope Local - Universal AI Debugging Flight Recorder
"""

__version__ = "0.2.0"

from .instrumentation import setup_instrumentation
from .model_detector import detector
from .model_registry import registry

__all__ = [
    'setup_instrumentation',
    'detector',
    'registry',
]
