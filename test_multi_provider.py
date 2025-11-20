"""
Enhanced Test Script - Multi-Provider & Dynamic Vectors
Tests the new model detection and dynamic vector table features.
"""
import time
import numpy as np
from opentelemetry import trace
from agentscope.instrumentation import setup_instrumentation
from agentscope.rag_logger import log_embedding, log_retrieval

# Setup Instrumentation
setup_instrumentation(debug=True)
tracer = trace.get_tracer("test_multi_provider")

def mock_llm_call(provider, model, prompt):
    """Simulate different LLM providers"""
    with tracer.start_as_current_span(f"llm_call_{provider}") as span:
        # Set GenAI attributes based on provider
        span.set_attribute("gen_ai.system", provider)
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.prompt", prompt)
        
        # Simulate token usage
        prompt_tokens = len(prompt.split()) * 2
        completion_tokens = 50
        
        span.set_attribute("gen_ai.usage.prompt_tokens", prompt_tokens)
        span.set_attribute("gen_ai.usage.completion_tokens", completion_tokens)
        span.set_attribute("gen_ai.usage.total_tokens", prompt_tokens + completion_tokens)
        
        time.sleep(0.1)
        response = f"[{provider}/{model}] Mock response to: {prompt}"
        span.set_attribute("gen_ai.completion", response)
        return response

def mock_embedding(text, model, dimension):
    """Simulate embedding with different dimensions"""
    with tracer.start_as_current_span("embedding_call") as span:
        span.set_attribute("gen_ai.system", "openai" if dimension == 1536 else "local")
        span.set_attribute("gen_ai.request.model", model)
        
        # Generate random embedding of specified dimension
        vector = np.random.rand(dimension).astype(np.float32)
        
        # Log the embedding
        log_embedding(
            db_path="debug_flight_recorder.db",
            text=text,
            vector=vector.tolist(),
            model_name=model,
            metadata={"source": "test", "dimension": dimension},
            vector_type="test"
        )
        
        return vector.tolist()

def test_multi_provider():
    """Test multiple LLM providers"""
    print("=== Testing Multiple LLM Providers ===\n")
    
    with tracer.start_as_current_span("multi_provider_test") as parent_span:
        parent_span.set_attribute("test.type", "multi_provider")
        
        # Test OpenAI
        print("1. Testing OpenAI...")
        mock_llm_call("openai", "gpt-4", "What is the meaning of life?")
        
        # Test Anthropic
        print("2. Testing Anthropic...")
        mock_llm_call("anthropic", "claude-3-sonnet-20240229", "Explain quantum computing")
        
        # Test Ollama (local)
        print("3. Testing Ollama...")
        mock_llm_call("ollama", "llama3:8b", "Write a poem about AI")
        
        # Test with URL-based detection
        print("4. Testing URL-based detection...")
        with tracer.start_as_current_span("ollama_url_test") as span:
            span.set_attribute("server.address", "localhost:11434")
            span.set_attribute("gen_ai.request.model", "mistral:7b")
            span.set_attribute("gen_ai.prompt", "Hello from Ollama")
            time.sleep(0.05)

def test_dynamic_vectors():
    """Test different embedding dimensions"""
    print("\n=== Testing Dynamic Vector Dimensions ===\n")
    
    with tracer.start_as_current_span("vector_dimension_test") as parent_span:
        parent_span.set_attribute("test.type", "dynamic_vectors")
        
        # Test 1536 dimensions (OpenAI standard)
        print("1. Testing 1536-dim vectors (OpenAI)...")
        mock_embedding("Large embedding model", "text-embedding-3-small", 1536)
        
        # Test 768 dimensions (BGE base)
        print("2. Testing 768-dim vectors (BGE)...")
        mock_embedding("Medium embedding model", "bge-base-en-v1.5", 768)
        
        # Test 384 dimensions (MiniLM)
        print("3. Testing 384-dim vectors (MiniLM)...")
        mock_embedding("Small embedding model", "all-minilm-l6-v2", 384)

def test_rag_workflow():
    """Test complete RAG workflow"""
    print("\n=== Testing RAG Workflow ===\n")
    
    with tracer.start_as_current_span("rag_workflow") as parent_span:
        parent_span.set_attribute("test.type", "rag_workflow")
        
        query = "How do I debug AI agents?"
        
        # 1. Generate query embedding
        print("1. Generating query embedding...")
        query_vector = mock_embedding(query, "text-embedding-3-small", 1536)
        
        # 2. Simulate retrieval
        print("2. Simulating document retrieval...")
        retrieved_docs = [
            {"text": "AgentScope is a debugging tool", "vector": np.random.rand(1536).tolist()},
            {"text": "Use traces to debug agents", "vector": np.random.rand(1536).tolist()},
            {"text": "Vector search finds relevant docs", "vector": np.random.rand(1536).tolist()},
        ]
        scores = [0.95, 0.87, 0.73]
        
        log_retrieval(
            db_path="debug_flight_recorder.db",
            query=query,
            query_vector=query_vector,
            retrieved_docs=retrieved_docs,
            scores=scores,
            model_name="text-embedding-3-small"
        )
        
        # 3. Generate response
        print("3. Generating LLM response...")
        context = " ".join([doc["text"] for doc in retrieved_docs])
        mock_llm_call("openai", "gpt-4", f"Context: {context}\n\nQuestion: {query}")

def main():
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  AgentScope Local - Enhanced Multi-Provider Test     ║")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    try:
        test_multi_provider()
        test_dynamic_vectors()
        test_rag_workflow()
        
        print("\n✅ All tests completed successfully!")
        print("\n📊 Check debug_flight_recorder.db for:")
        print("   - Different provider detections (OpenAI, Anthropic, Ollama)")
        print("   - Token usage and cost estimates")
        print("   - Multiple vector tables (vectors_384, vectors_768, vectors_1536)")
        print("   - RAG workflow traces")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
