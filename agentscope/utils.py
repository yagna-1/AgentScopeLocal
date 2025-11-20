"""
Utility Functions for AgentScope Local
"""
from opentelemetry import context
import sqlite3
import json
import numpy as np
from typing import Optional, List, Dict, Any


def run_in_thread(func, *args):
    """
    Context propagation wrapper for running functions in threads.
    Ensures OpenTelemetry trace context is maintained across threads.
    """
    # Capture the current context (which contains the active Trace ID)
    current_context = context.get_current()
    
    def wrapper():
        # Attach the context inside the new thread
        token = context.attach(current_context)
        try:
            return func(*args)
        finally:
            context.detach(token)
            
    # This function returns the wrapper, which should be submitted to a thread pool
    return wrapper


def serialize_vector(vector: List[float]) -> bytes:
    """
    Serialize a vector for storage in sqlite-vec.
    Converts a list of floats to binary format.
    """
    from sqlite_vec import serialize_float32
    
    if isinstance(vector, np.ndarray):
        vector = vector.tolist()
    
    return serialize_float32(vector)


def deserialize_vector(binary: bytes) -> List[float]:
    """
    Deserialize a vector from sqlite-vec binary format.
    """
    import struct
    
    # Each float is 4 bytes
    num_floats = len(binary) // 4
    return list(struct.unpack(f'{num_floats}f', binary))


def get_vector_table_name(dimension: int) -> str:
    """
    Get the name of the vector table for a specific dimension.
    Example: 1536 -> 'vectors_1536'
    """
    return f"vectors_{dimension}"


def ensure_vector_table(conn: sqlite3.Connection, dimension: int):
    """
    Ensure a vector table exists for the given dimension.
    Creates it if it doesn't exist.
    """
    table_name = get_vector_table_name(dimension)
    
    try:
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {table_name} 
            USING vec0(embedding float[{dimension}])
        """)
    except sqlite3.OperationalError as e:
        # Table might already exist
        if "already exists" not in str(e).lower():
            raise


def log_vector(db_path: str, trace_id: str, span_id: str, vector, text: str, metadata: dict = None):
    """
    Legacy function for backwards compatibility.
    Use rag_logger.log_embedding instead.
    """
    from .rag_logger import log_embedding
    
    model_name = metadata.get('model', 'unknown') if metadata else 'unknown'
    log_embedding(db_path, text, vector, model_name, metadata)
