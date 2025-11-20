import time
import numpy as np
from opentelemetry import trace
from agentscope.instrumentation import setup_instrumentation
from agentscope.utils import log_vector

# Setup Instrumentation
setup_instrumentation(debug=True)
tracer = trace.get_tracer("test_agent")

def mock_llm_call(prompt):
    with tracer.start_as_current_span("llm_call") as span:
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", "gpt-4")
        span.set_attribute("gen_ai.prompt", prompt)
        time.sleep(0.1)
        response = "This is a mock response."
        span.set_attribute("gen_ai.completion", response)
        return response

def mock_vector_search(query):
    with tracer.start_as_current_span("vector_search") as span:
        span_id = f"{span.get_span_context().span_id:016x}"
        trace_id = f"{span.get_span_context().trace_id:032x}"
        
        # Simulate embedding
        vector = np.random.rand(1536).astype(np.float32)
        
        # Log vector
        log_vector(
            db_path="debug_flight_recorder.db",
            trace_id=trace_id,
            span_id=span_id,
            vector=vector,
            text=query,
            metadata={"source": "test"}
        )
        
        span.set_attribute("db.system", "sqlite-vec")
        time.sleep(0.05)
        return ["doc1", "doc2"]

def main():
    print("Starting trace...")
    with tracer.start_as_current_span("agent_workflow") as parent_span:
        parent_span.set_attribute("user.id", "123")
        
        query = "How do I fix this bug?"
        print(f"Processing query: {query}")
        
        docs = mock_vector_search(query)
        print(f"Retrieved docs: {docs}")
        
        response = mock_llm_call(f"Context: {docs}. Question: {query}")
        print(f"Agent response: {response}")
        
    print("Trace finished. Checking database...")

if __name__ == "__main__":
    main()
