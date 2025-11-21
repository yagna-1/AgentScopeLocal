import sqlite3
import json
from typing import Sequence
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from .model_detector import detector


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
                pass

            # Create the Spans table with enhanced schema
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
                    resource JSON,
                    
                    -- Enhanced fields for model detection
                    provider TEXT,
                    model_name TEXT,
                    model_family TEXT,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    reasoning_tokens INTEGER,
                    estimated_cost_usd REAL,
                    
                    -- Performance metrics (Week 6)
                    ttft_ms REAL,
                    tokens_per_second REAL,
                    generation_time_ms REAL,
                    
                    -- Model configuration (Week 6)
                    temperature REAL,
                    top_p REAL,
                    top_k INTEGER,
                    max_tokens INTEGER,
                    context_window_size INTEGER,
                    
                    -- Resource monitoring (Week 6)
                    cpu_percent REAL,
                    memory_mb REAL,
                    gpu_utilization REAL,
                    gpu_memory_used_mb REAL,
                    
                    -- Streaming support (Week 7)
                    streaming_enabled BOOLEAN DEFAULT FALSE,
                    streaming_chunk_count INTEGER,
                    streaming_ttft_ms REAL,
                    streaming_total_time_ms REAL,
                    streaming_avg_inter_chunk_ms REAL,
                    streaming_per_token_ms REAL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_id ON spans(trace_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_start_time ON spans(start_time);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_provider ON spans(provider);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_model_name ON spans(model_name);")

            # Vector Metadata Table (dimension-agnostic metadata)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vector_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vector_rowid INTEGER,
                    table_name TEXT,
                    span_id TEXT,
                    trace_id TEXT,
                    content TEXT,
                    metadata JSON
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vm_span ON vector_metadata(span_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vm_trace ON vector_metadata(trace_id);")

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
                attrs = dict(span.attributes) if span.attributes else {}
                
                events_json = json.dumps([
                    {
                        "name": e.name, 
                        "timestamp": e.timestamp, 
                        "attributes": dict(e.attributes) if e.attributes else {}
                    } for e in span.events
                ])
                
                # Enhanced: Detect provider and extract model info
                provider = detector.detect_provider(attrs)
                model_name = attrs.get('gen_ai.request.model', attrs.get('gen_ai.response.model', None))
                
                # Get model family from registry
                from .model_registry import registry
                model_family = registry.get_model_family(model_name) if model_name else None
                
                # Extract token usage and cost
                usage = detector.extract_cost_info(attrs, provider)
                
                # Extract performance metrics (Week 6)
                ttft_ms = attrs.get('llm.ttft_ms')
                tokens_per_second = attrs.get('llm.tokens_per_second')
                generation_time_ms = attrs.get('llm.generation_time_ms')
                
                # Extract model configuration (Week 6)
                temperature = attrs.get('gen_ai.request.temperature')
                top_p = attrs.get('gen_ai.request.top_p')
                top_k = attrs.get('gen_ai.request.top_k')
                max_tokens = attrs.get('gen_ai.request.max_tokens')
                context_window_size = attrs.get('gen_ai.model.context_window')
                
                # Extract resource metrics (Week 6)
                cpu_percent = attrs.get('system.cpu_percent')
                memory_mb = attrs.get('system.memory_mb')
                gpu_utilization = attrs.get('system.gpu_utilization')
                gpu_memory_used_mb = attrs.get('system.gpu_memory_used_mb')
                
                # Extract streaming metrics (Week 7)
                streaming_enabled = attrs.get('llm.streaming.enabled', False)
                streaming_chunk_count = attrs.get('llm.streaming.chunk_count')
                streaming_ttft_ms = attrs.get('llm.streaming.ttft_ms')
                streaming_total_time_ms = attrs.get('llm.streaming.total_time_ms')
                streaming_avg_inter_chunk_ms = attrs.get('llm.streaming.avg_inter_chunk_ms')
                streaming_per_token_ms = attrs.get('llm.streaming.per_token_ms')
                
                data.append((
                    span_id, trace_id, parent_id, span.name, span.kind.name,
                    span.start_time, span.end_time, span.status.status_code.name,
                    span.status.description, attributes_json, events_json,
                    json.dumps(dict(span.resource.attributes)),
                    
                    # Enhanced fields
                    provider,
                    model_name,
                    model_family,
                    usage.get('prompt_tokens'),
                    usage.get('completion_tokens'),
                    usage.get('total_tokens'),
                    usage.get('reasoning_tokens'),
                    usage.get('estimated_cost_usd'),
                    
                    # Performance metrics (Week 6)
                    ttft_ms,
                    tokens_per_second,
                    generation_time_ms,
                    
                    # Model configuration (Week 6)
                    temperature,
                    top_p,
                    top_k,
                    max_tokens,
                    context_window_size,
                    
                    # Resource metrics (Week 6)
                    cpu_percent,
                    memory_mb,
                    gpu_utilization,
                    gpu_memory_used_mb,
                    
                    # Streaming metrics (Week 7)
                    streaming_enabled,
                    streaming_chunk_count,
                    streaming_ttft_ms,
                    streaming_total_time_ms,
                    streaming_avg_inter_chunk_ms,
                    streaming_per_token_ms
                ))

            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT OR REPLACE INTO spans 
                    (span_id, trace_id, parent_span_id, name, kind, start_time, end_time, 
                     status_code, status_message, attributes, events, resource,
                     provider, model_name, model_family, prompt_tokens, completion_tokens,
                     total_tokens, reasoning_tokens, estimated_cost_usd,
                     ttft_ms, tokens_per_second, generation_time_ms,
                     temperature, top_p, top_k, max_tokens, context_window_size,
                     cpu_percent, memory_mb, gpu_utilization, gpu_memory_used_mb,
                     streaming_enabled, streaming_chunk_count, streaming_ttft_ms,
                     streaming_total_time_ms, streaming_avg_inter_chunk_ms, streaming_per_token_ms)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, data)
                
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Error exporting spans: {e}")
            import traceback
            traceback.print_exc()
            return SpanExportResult.FAILURE

    def shutdown(self):
        pass
