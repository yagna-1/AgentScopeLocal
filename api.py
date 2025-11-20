from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI()

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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vector_metadata WHERE span_id = ?", (span_id,))
    rows = cursor.fetchall()
    conn.close()
    
    vectors = []
    for row in rows:
        vectors.append({
            "text_content": row["text_content"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "vector_type": row["vector_type"]
        })
        
    return vectors

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
