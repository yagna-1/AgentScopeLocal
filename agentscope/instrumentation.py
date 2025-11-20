from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from .exporter import SQLiteSpanExporter

def setup_instrumentation(service_name: str = "agent_scope_local", debug: bool = False, db_path: str = "debug_flight_recorder.db"):
    """
    Initializes the OpenTelemetry tracing system with a custom SQLite exporter.
    """
    # 1. Define the Resource
    # This identifies the agent instance in the trace data.
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        "deployment.environment": "local",
        "telemetry.sdk.name": "agentscope-local"
    })

    # 2. Initialize TracerProvider
    provider = TracerProvider(resource=resource)
    
    # 3. Configure Exporter
    # We use the custom SQLiteSpanExporter
    exporter = SQLiteSpanExporter(db_path)
    
    # 4. Add Span Processor
    # Use SimpleSpanProcessor for immediate writes during debugging (slower but safer)
    # Use BatchSpanProcessor for production/performance
    processor_type = SimpleSpanProcessor if debug else BatchSpanProcessor
    provider.add_span_processor(processor_type(exporter))
    
    # 5. Set Global Provider
    trace.set_tracer_provider(provider)
    
    return provider
