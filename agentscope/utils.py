from opentelemetry import context
import sqlite3
from sqlite_vec import serialize_float32
import numpy as np
import json

def run_in_thread(func, *args):
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

def log_vector(db_path: str, trace_id: str, span_id: str, vector, text: str, metadata: dict = None):
    """
    Logs a vector and its metadata to the SQLite database.
    """
    with sqlite3.connect(db_path) as conn:
        conn.enable_load_extension(True)
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
        except ImportError:
            pass

        cursor = conn.cursor()
        
        # 1. Insert Metadata
        cursor.execute(
            "INSERT INTO vector_metadata (trace_id, span_id, text_content, metadata) VALUES (?,?,?,?)",
            (trace_id, span_id, text, json.dumps(metadata) if metadata else "{}")
        )
        row_id = cursor.lastrowid
        
        # 2. Serialize and Insert Vector
        # Ensure vector is flat list of floats
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
            
        binary_blob = serialize_float32(vector)
        try:
            cursor.execute(
                "INSERT INTO debug_vectors(rowid, embedding) VALUES (?,?)",
                (row_id, binary_blob)
            )
        except sqlite3.OperationalError:
            print("Warning: debug_vectors table not found or sqlite-vec not loaded. Vector not stored.")
