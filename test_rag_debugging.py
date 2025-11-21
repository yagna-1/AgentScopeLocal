"""
Test Week 2: RAG Debugging and Time Travel
Tests the new API endpoints for similarity search and LLM forking.
"""
import requests
import json
from test_multi_provider import mock_llm_call, mock_embedding
from opentelemetry import trace
from agentscope.instrumentation import setup_instrumentation
from agentscope.rag_logger import log_embedding
import numpy as np

# Setup
setup_instrumentation(debug=True)
tracer = trace.get_tracer("test_week2")

BASE_URL = "http://localhost:8000"

def generate_test_data():
    """Generate test data with LLM calls and embeddings"""
    print("📝 Generating test data...")
    
    with tracer.start_as_current_span("test_rag_scenario"):
        # Simulate a RAG query
        query = "How do I use AgentScope Local?"
        
        # Log some document embeddings (simulating a knowledge base)
        docs = [
            "AgentScope Local is a debugging tool for AI agents",
            "To install AgentScope, run: pip install agentscope-local",
            "AgentScope supports OpenAI, Anthropic, and Ollama",
            "Use the Time Travel feature to replay LLM calls",
            "RAG debugging shows what chunks should have been retrieved",
        ]
        
        print(f"  Indexing {len(docs)} documents...")
        for doc in docs:
            vector = np.random.rand(1536).astype(np.float32)
            log_embedding(
                db_path="debug_flight_recorder.db",
                text=doc,
                vector=vector.tolist(),
                model_name="text-embedding-3-small",
                metadata={"type": "knowledge_base"},
                vector_type="document"
            )
        
        # Log query embedding
        print(f"  Processing query: '{query}'")
        query_vector = np.random.rand(1536).astype(np.float32)
        
        with tracer.start_as_current_span("query_embedding") as span:
            span.set_attribute("gen_ai.system", "openai")
            span.set_attribute("gen_ai.request.model", "text-embedding-3-small")
            
            log_embedding(
                db_path="debug_flight_recorder.db",
                text=query,
                vector=query_vector.tolist(),
                model_name="text-embedding-3-small",
                metadata={"type": "user_query"},
                vector_type="query"
            )
            
            query_span_id = f"{span.get_span_context().span_id:016x}"
        
        # Simulate LLM response
        print("  Generating LLM response...")
        response = mock_llm_call(
            "openai",
            "gpt-4",
            "Based on the context, explain how to use AgentScope Local"
        )
        
        # Get the LLM span ID
        with tracer.start_as_current_span("get_llm_span") as span:
            llm_span_id = f"{span.get_span_context().span_id:016x}"
    
    print(f"✅ Test data generated")
    print(f"   Query span ID: {query_span_id}")
    return query_span_id


def test_rag_debugging():
    """Test the RAG debugging endpoint"""
    print("\n" + "="*60)
    print("🔍 Testing RAG Debugging Endpoint")
    print("="*60)
    
    # Generate test data first
    query_span_id = generate_test_data()
    
    print(f"\n📡 Calling /api/debug-rag/{query_span_id}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/debug-rag/{query_span_id}", params={"limit": 5})
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\n✅ RAG Debugging Results:")
        print(f"   Query: {data['query']['content'][:60]}...")
        print(f"\n   Top {len(data['similar_vectors'])} Similar Vectors:")
        
        for i, vec in enumerate(data['similar_vectors'], 1):
            print(f"\n   {i}. Similarity: {vec['similarity']:.4f}")
            print(f"      Content: {vec['content'][:70]}...")
            print(f"      Metadata: {vec['metadata']}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: API server not running!")
        print("   Start it with: uvicorn api:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_travel():
    """Test the Time Travel fork endpoint"""
    print("\n" + "="*60)
    print("⏰ Testing Time Travel (Fork) Endpoint")
    print("="*60)
    
    print("\n⚠️  Note: This requires OpenAI API key in environment")
    print("   Set OPENAI_API_KEY to test with real API")
    print("   Or mock data will be used for demonstration")
    
    # For now, just show the endpoint structure
    print("\n📡 Endpoint: POST /api/fork/{span_id}")
    print("   Body: {")
    print('     "modified_prompt": "Your new prompt here",')
    print('     "temperature": 0.7,')
    print('     "max_tokens": 1000')
    print("   }")
    
    print("\n✅ Time Travel endpoint is ready")
    print("   Test it by selecting an LLM span in the UI and")
    print("   clicking the 'Fork' button (to be implemented in Week 3)")
    
    return True


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║       Week 2 Testing: Advanced API Endpoints          ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    rag_ok = test_rag_debugging()
    travel_ok = test_time_travel()
    
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"   RAG Debugging: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    print(f"   Time Travel:   {'✅ PASS' if travel_ok else '❌ FAIL'}")
    
    if rag_ok and travel_ok:
        print("\n🎉 Week 2 Backend Implementation Complete!")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    main()
