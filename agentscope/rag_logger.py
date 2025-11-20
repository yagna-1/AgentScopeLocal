"""
RAG Logging Utilities
Utilities for logging vector embeddings and retrieval operations.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from opentelemetry import trace

from .utils import serialize_vector, get_vector_table_name, ensure_vector_table
from .model_registry import registry


def log_embedding(
    db_path: str,
    text: str,
    vector: List[float],
    model_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    vector_type: str = 'document'
):
    """
    Log an embedding vector to the database.
    
    Args:
        db_path: Path to SQLite database
        text: The text that was embedded
        vector: The embedding vector
        model_name: Name of the embedding model
        metadata: Optional metadata (source file, page number, etc.)
        vector_type: Type of vector ('document', 'query', 'chunk')
    """
    # Get current span context
    span = trace.get_current_span()
    ctx = span.get_span_context()
    span_id = f"{ctx.span_id:016x}" if ctx.span_id else "no_span"
    trace_id = f"{ctx.trace_id:032x}" if ctx.trace_id else "no_trace"
    
    # Detect dimension
    dimension = len(vector)
    
    # Serialize vector
    binary_vector = serialize_vector(vector)
    
    with sqlite3.connect(db_path) as conn:
        conn.enable_load_extension(True)
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
        except ImportError:
            print("Warning: sqlite-vec not available")
            return
        
        # Ensure table exists for this dimension
        ensure_vector_table(conn, dimension)
        table_name = get_vector_table_name(dimension)
        
        cursor = conn.cursor()
        
        # Insert vector
        cursor.execute(f"INSERT INTO {table_name}(embedding) VALUES (?)", (binary_vector,))
        row_id = cursor.lastrowid
        
        # Insert metadata
        meta_dict = metadata or {}
        meta_dict['model'] = model_name
        meta_dict['dimension'] = dimension
        meta_dict['type'] = vector_type
        
        cursor.execute("""
            INSERT INTO vector_metadata (vector_rowid, table_name, span_id, trace_id, content, metadata)
            VALUES (?,?,?,?,?,?)
        """, (row_id, table_name, span_id, trace_id, text, json.dumps(meta_dict)))
        
        conn.commit()


def log_retrieval(
    db_path: str,
    query: str,
    query_vector: List[float],
    retrieved_docs: List[Dict[str, Any]],
    scores: List[float],
    model_name: str
):
    """
    Log a RAG retrieval operation.
    
    Args:
        db_path: Path to SQLite database
        query: The query text
        query_vector: The query embedding
        retrieved_docs: List of retrieved documents (with 'text' and 'metadata' fields)
        scores: Similarity scores for each retrieved document
        model_name: Name of the embedding model
    """
    # Log the query vector
    log_embedding(
        db_path=db_path,
        text=query,
        vector=query_vector,
        model_name=model_name,
        metadata={'retrieved_count': len(retrieved_docs)},
        vector_type='query'
    )
    
    # Log retrieved documents
    for i, (doc, score) in enumerate(zip(retrieved_docs, scores)):
        doc_text = doc.get('text', doc.get('content', ''))
        doc_meta = doc.get('metadata', {})
        doc_meta['retrieval_score'] = score
        doc_meta['retrieval_rank'] = i + 1
        
        if 'vector' in doc:
            log_embedding(
                db_path=db_path,
                text=doc_text,
                vector=doc['vector'],
                model_name=model_name,
                metadata=doc_meta,
                vector_type='retrieved'
            )


def get_similar_vectors(
    db_path: str,
    query_vector: List[float],
    limit: int = 10,
    exclude_span_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Find similar vectors using cosine similarity.
    
    Args:
        db_path: Path to SQLite database
        query_vector: The query vector
        limit: Maximum number of results
        exclude_span_id: Optionally exclude vectors from a specific span
    
    Returns:
        List of similar vectors with their metadata and scores
    """
    dimension = len(query_vector)
    table_name = get_vector_table_name(dimension)
    binary_query = serialize_vector(query_vector)
    
    with sqlite3.connect(db_path) as conn:
        conn.enable_load_extension(True)
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
        except ImportError:
            return []
        
        conn.row_factory = sqlite3.Row
        
        # Build query
        query_sql = f"""
            SELECT 
                vm.id,
                vm.vector_rowid,
                vm.table_name,
                vm.span_id,
                vm.trace_id,
                vm.content,
                vm.metadata,
                vec_distance_cosine(v.embedding, ?) as distance
            FROM {table_name} v
            JOIN vector_metadata vm ON v.rowid = vm.vector_rowid AND vm.table_name = ?
        """
        
        params = [binary_query, table_name]
        
        if exclude_span_id:
            query_sql += " WHERE vm.span_id != ?"
            params.append(exclude_span_id)
        
        query_sql += " ORDER BY distance ASC LIMIT ?"
        params.append(limit)
        
        rows = conn.execute(query_sql, params).fetchall()
        
        results = []
        for row in rows:
            meta = json.loads(row['metadata']) if row['metadata'] else {}
            results.append({
                'id': row['id'],
                'vector_rowid': row['vector_rowid'],
                'table_name': row['table_name'],
                'span_id': row['span_id'],
                'trace_id': row['trace_id'],
                'content': row['content'],
                'metadata': meta,
                'distance': row['distance'],
                'similarity': 1 - row['distance']  # Convert distance to similarity
            })
        
        return results
