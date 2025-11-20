import sqlite3
import json
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class SQLiteSpanExporter(SpanExporter):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            # Enable sqlite-vec if available
            conn.enable_load_extension(True)
            try:
                import sqlite_vec
                sqlite_vec.load(conn)
            except ImportError:
                pass # Handle gracefully if vector support isn't needed immediately

            # Create the Spans table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS spans (
                    span_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    parent_span_id TEXT,
                    name TEXT,
                    kind TEXT,
                    start_time INTEGER,
                    end_time INTEGER,
                    status_code TEXT,
                    status_message TEXT,
                    attributes JSON,
                    events JSON,
                    resource JSON
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_id ON spans(trace_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_start_time ON spans(start_time);")

            # Vector Debugging Schema
            # 1. Create a Virtual Table for Embeddings
            # We use a 1536-dim float array (standard for OpenAI ada-002/003)
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS debug_vectors USING vec0(
                        embedding float[1536]
                    );
                """)
            except sqlite3.OperationalError:
                 # Fallback or ignore if vec0 not available/loaded
                 pass

            # 2. Create a Metadata Table linking Spans to Vectors
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_metadata (
                    rowid INTEGER PRIMARY KEY, -- Links to debug_vectors.rowid
                    trace_id TEXT NOT NULL,
                    span_id TEXT NOT NULL,
                    vector_type TEXT, -- 'query', 'retrieved_doc', 'generated_doc'
                    text_content TEXT, -- The actual text chunk
                    metadata JSON
                );
            """)

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            data = []
            for span in spans:
                # Serialize the span context and attributes
                span_ctx = span.get_span_context()
                parent_ctx = span.parent
                
                # OTel IDs are integers, convert to hex strings for readability
                trace_id = f"{span_ctx.trace_id:032x}"
                span_id = f"{span_ctx.span_id:016x}"
                parent_id = f"{parent_ctx.span_id:016x}" if parent_ctx else None
                
                # Serialize Attributes and Events
                attributes_json = json.dumps(dict(span.attributes)) if span.attributes else "{}"
                events_json = json.dumps([
                    {
                        "name": e.name, 
                        "timestamp": e.timestamp, 
                        "attributes": dict(e.attributes) if e.attributes else {}
                    } for e in span.events
                ])
                
                data.append((
                    span_id, trace_id, parent_id, span.name, span.kind.name,
                    span.start_time, span.end_time, span.status.status_code.name,
                    span.status.description, attributes_json, events_json,
                    json.dumps(dict(span.resource.attributes))
                ))

            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT OR REPLACE INTO spans 
                    (span_id, trace_id, parent_span_id, name, kind, start_time, end_time, 
                     status_code, status_message, attributes, events, resource)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)
                
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting spans: {e}")
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass
