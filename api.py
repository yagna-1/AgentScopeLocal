"""
FastAPI server for AgentScope Local
Serves the web UI and provides APIs for trace analysis.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path

app = FastAPI(title="AgentScope Local", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "debug_flight_recorder.db"

class Span(BaseModel):
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    name: str
    kind: str
    start_time: int
    end_time: Optional[int]
    status_code: str
    status_message: Optional[str]
    attributes: Dict[str, Any]
    events: List[Dict[str, Any]]
    resource: Dict[str, Any]

class TraceSummary(BaseModel):
    trace_id: str
    root_span_name: str
    start_time: int
    span_count: int

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/traces", response_model=List[TraceSummary])
def list_traces():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get unique trace IDs and their root span info
    # Assuming root span has no parent_span_id or we pick the earliest one
    query = """
        SELECT 
            t.trace_id,
            min(t.start_time) as start_time,
            count(t.span_id) as span_count,
            (SELECT name FROM spans WHERE trace_id = t.trace_id ORDER BY start_time ASC LIMIT 1) as root_span_name
        FROM spans t
        GROUP BY t.trace_id
        ORDER BY start_time DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return [
        TraceSummary(
            trace_id=row["trace_id"],
            root_span_name=row["root_span_name"] or "Unknown",
            start_time=row["start_time"],
            span_count=row["span_count"]
        )
        for row in rows
    ]

@app.get("/traces/{trace_id}", response_model=List[Span])
def get_trace(trace_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM spans WHERE trace_id = ?", (trace_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Trace not found")
        
    spans = []
    for row in rows:
        # Parse JSON fields
        attributes = json.loads(row["attributes"]) if row["attributes"] else {}
        events = json.loads(row["events"]) if row["events"] else []
        resource = json.loads(row["resource"]) if row["resource"] else {}
        
        spans.append(Span(
            span_id=row["span_id"],
            trace_id=row["trace_id"],
            parent_span_id=row["parent_span_id"],
            name=row["name"],
            kind=row["kind"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            status_code=row["status_code"],
            status_message=row["status_message"],
            attributes=attributes,
            events=events,
            resource=resource
        ))
        
    return spans

@app.get("/vectors/{span_id}")
def get_vectors(span_id: str):
    """Get all vectors associated with a span"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vector_metadata WHERE span_id = ?", (span_id,))
    rows = cursor.fetchall()
    conn.close()
    
    vectors = []
    for row in rows:
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        vectors.append({
            "id": row["id"],
            "content": row["content"],
            "metadata": metadata,
            "table_name": row["table_name"],
            "vector_rowid": row["vector_rowid"]
        })
        
    return vectors


@app.post("/api/debug-rag/{span_id}")
def debug_rag(span_id: str, limit: int = 10):
    """
    Debug RAG by finding similar vectors.
    Shows what chunks SHOULD have been retrieved.
    """
    conn = get_db_connection()
    conn.enable_load_extension(True)
    
    try:
        import sqlite_vec
        sqlite_vec.load(conn)
    except ImportError:
        raise HTTPException(status_code=500, detail="sqlite-vec not available")
    
    cursor = conn.cursor()
    
    # Get the vector(s) for this span
    cursor.execute("""
        SELECT vector_rowid, table_name, content, metadata 
        FROM vector_metadata 
        WHERE span_id = ?
        LIMIT 1
    """, (span_id,))
    
    query_row = cursor.fetchone()
    if not query_row:
        raise HTTPException(status_code=404, detail="No vectors found for this span")
    
    table_name = query_row["table_name"]
    vector_rowid = query_row["vector_rowid"]
    query_content = query_row["content"]
    
    # Get the query vector
    query_vector = cursor.execute(
        f"SELECT embedding FROM {table_name} WHERE rowid = ?",
        (vector_rowid,)
    ).fetchone()
    
    if not query_vector:
        raise HTTPException(status_code=404, detail="Vector data not found")
    
    # Find similar vectors (excluding the query itself)
    similar = cursor.execute(f"""
        SELECT 
            vm.id,
            vm.span_id,
            vm.content,
            vm.metadata,
            vec_distance_cosine(v.embedding, ?) as distance,
            (1 - vec_distance_cosine(v.embedding, ?)) as similarity
        FROM {table_name} v
        JOIN vector_metadata vm ON v.rowid = vm.vector_rowid AND vm.table_name = ?
        WHERE vm.span_id != ?
        ORDER BY distance ASC
        LIMIT ?
    """, (query_vector["embedding"], query_vector["embedding"], table_name, span_id, limit)).fetchall()
    
    conn.close()
    
    results = []
    for row in similar:
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}
        results.append({
            "id": row["id"],
            "span_id": row["span_id"],
            "content": row["content"],
            "metadata": metadata,
            "distance": row["distance"],
            "similarity": row["similarity"]
        })
    
    return {
        "query": {
            "span_id": span_id,
            "content": query_content
        },
        "similar_vectors": results
    }


class ForkRequest(BaseModel):
    modified_prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None


@app.post("/api/fork/{span_id}")
def fork_span(span_id: str, request: ForkRequest):
    """
    Time Travel: Fork an LLM call with a modified prompt.
    Re-runs the LLM with the new prompt and returns the result.
    """
    from agentscope.llm_client import llm_client
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get the original span
    cursor.execute("SELECT * FROM spans WHERE span_id = ?", (span_id,))
    span_row = cursor.fetchone()
    conn.close()
    
    if not span_row:
        raise HTTPException(status_code=404, detail="Span not found")
    
    # Parse attributes
    attributes = json.loads(span_row["attributes"]) if span_row["attributes"] else {}
    
    # Extract model info
    provider = span_row["provider"]
    model = span_row["model_name"]
    
    if not provider or not model:
        raise HTTPException(
            status_code=400, 
            detail="Span does not contain LLM call information (missing provider or model)"
        )
    
    # Check if client is available
    if not llm_client.is_available(provider):
        raise HTTPException(
            status_code=503,
            detail=f"Provider '{provider}' is not available. Check API keys or installation."
        )
    
    # Extract original prompt (if available)
    original_prompt = attributes.get("gen_ai.prompt", "")
    original_completion = attributes.get("gen_ai.completion", "")
    
    # Build messages
    messages = [{"role": "user", "content": request.modified_prompt}]
    
    try:
        # Call the LLM
        response = llm_client.call(
            provider=provider,
            model=model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "original": {
                "span_id": span_id,
                "provider": provider,
                "model": model,
                "prompt": original_prompt,
                "completion": original_completion,
                "prompt_tokens": span_row["prompt_tokens"],
                "completion_tokens": span_row["completion_tokens"],
            },
            "forked": {
                "prompt": request.modified_prompt,
                "completion": response["content"],
                "model": response["model"],
                "usage": response["usage"],
                "finish_reason": response["finish_reason"],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


# ============================================================================
# Static File Serving
# ============================================================================

# Mount static files from the built frontend
FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    # Serve static assets
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")
    
    # Serve index.html for the root and any SPA routes
    @app.get("/")
    async def serve_root():
        """Serve the React app"""
        return FileResponse(str(FRONTEND_DIST / "index.html"))
    
    # Catch-all route for SPA routing (must be last)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React app for all routes (SPA routing)"""
        # If it's an API route, let FastAPI handle it
        if full_path.startswith("api/") or full_path.startswith("traces/") or full_path.startswith("vectors/"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Otherwise serve the React app
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    async def no_frontend():
        """Development mode - frontend not built"""
        return {
            "message": "AgentScope Local API is running",
            "frontend": "not built (run 'npm run build' in frontend/)",
            "api_docs": "/docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
