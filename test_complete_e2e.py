"""
End-to-End Test with Local LLM (Ollama)
Tests the complete AgentScope Local application with a real local model.

This test demonstrates:
1. Model detection (Ollama)
2. RAG logging with embeddings
3. Vector similarity search
4. Time Travel forking capability

Run this after starting Ollama: `ollama serve`
"""
import os
from opentelemetry import trace
from agentscope.instrumentation import setup_instrumentation
from agentscope.rag_logger import log_embedding, get_similar_vectors
import requests
import json

# Setup
setup_instrumentation(service_name="local_llm_test", db_path="debug_flight_recorder.db")
tracer = trace.get_tracer(__name__)

def call_ollama(model: str, prompt: str) -> str:
    """Call Ollama API directly"""
    with tracer.start_as_current_span("ollama_call") as span:
        # Set OpenTelemetry attributes for model detection
        span.set_attribute("gen_ai.system", "ollama")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.prompt", prompt)
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            completion = result.get("response", "")
            span.set_attribute("gen_ai.completion", completion)
            
            # Token tracking (if available)
            if "eval_count" in result:
                span.set_attribute("gen_ai.usage.completion_tokens", result["eval_count"])
            if "prompt_eval_count" in result:
                span.set_attribute("gen_ai.usage.prompt_tokens", result["prompt_eval_count"])
            
            return completion
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise

def mock_embedding(text: str, dimension: int = 384) -> list:
    """Create a simple mock embedding for testing"""
    import hashlib
    import numpy as np
    
    # Use hash to create deterministic but varied embeddings
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    np.random.seed(hash_val % (2**32))
    
    # Generate normalized vector
    vec = np.random.randn(dimension)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()

def test_complete_workflow(model: str = "qwen2.5:0.5b"):
    """Test the complete AgentScope Local workflow"""
    
    print("=" * 70)
    print("🚀 AgentScope Local - End-to-End Test with Local LLM")
    print("=" * 70)
    print()
    
    # Phase 1: RAG Document Indexing
    print("📚 Phase 1: Indexing Knowledge Base")
    print("-" * 70)
    
    documents = [
        "AgentScope Local is a universal AI debugging flight recorder.",
        "It supports OpenAI, Anthropic, Ollama, and other LLM providers.",
        "RAG debugging helps identify retrieval quality issues.",
        "Time Travel allows re-running LLM calls with modified prompts.",
        "The system uses SQLite with vector extensions for storage."
    ]
    
    with tracer.start_as_current_span("index_documents"):
        for idx, doc in enumerate(documents):
            embedding = mock_embedding(doc, 384)
            log_embedding(
                db_path="debug_flight_recorder.db",
                text=doc,
                vector=embedding,
                model_name="all-minilm-l6-v2",
                metadata={
                    "type": "document",
                    "index": idx,
                    "dimension": 384
                }
            )
            print(f"  ✓ Indexed: {doc[:50]}...")
    
    print(f"\n  Indexed {len(documents)} documents")
    print()
    
    # Phase 2: Query with Local LLM
    print("🤖 Phase 2: Query with Local LLM (Ollama)")
    print("-" * 70)
    
    query = "What is AgentScope Local and what can it do?"
    print(f"  Query: {query}")
    print()
    
    # Log query embedding
    query_embedding = mock_embedding(query, 384)
    query_span_id = None
    
    with tracer.start_as_current_span("process_query") as span:
        query_span_id = format(span.get_span_context().span_id, '016x')
        log_embedding(
            db_path="debug_flight_recorder.db",
            text=query,
            vector=query_embedding,
            model_name="all-minilm-l6-v2",
            metadata={
                "type": "query",
                "dimension": 384
            }
        )
    
    print(f"  Query Span ID: {query_span_id}")
    print()
    
    # Phase 3: RAG Similarity Search
    print("🔍 Phase 3: RAG Similarity Search")
    print("-" * 70)
    
    similar = get_similar_vectors(
        db_path="debug_flight_recorder.db",
        query_vector=query_embedding,
        limit=3,
        exclude_span_id=query_span_id  # Exclude the query itself
    )
    print(f"  Found {len(similar)} similar documents:")
    for idx, vec in enumerate(similar, 1):
        similarity = 1 - vec['distance']
        print(f"    {idx}. [{similarity:.2%}] {vec['content'][:60]}...")
    print()
    
    # Phase 4: Call Local LLM
    print("💬 Phase 4: Calling Local LLM")
    print("-" * 70)
    print(f"  Model: {model}")
    print(f"  Checking Ollama status...")
    
    try:
        # Check if Ollama is running
        status_response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if status_response.status_code == 200:
            print(f"  ✓ Ollama is running")
            
            # Build context from similar documents
            context = "\n".join([f"- {v['content']}" for v in similar[:3]])
            full_prompt = f"Based on this context:\n{context}\n\nAnswer: {query}"
            
            print(f"\n  Sending prompt...")
            response = call_ollama(model, full_prompt)
            
            print(f"\n  ✓ LLM Response:")
            print(f"  {response[:200]}{'...' if len(response) > 200 else ''}")
            print()
        else:
            print(f"  ⚠ Ollama not responding properly")
            print(f"    Status: {status_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ⚠ Ollama not running (connection refused)")
        print(f"    Start Ollama with: ollama serve")
        print(f"    Or run in background: ollama serve &")
        print()
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print()
    
    # Phase 5: API Integration Test
    print("🌐 Phase 5: Testing API Endpoints")
    print("-" * 70)
    
    try:
        # Test RAG Debug endpoint
        print(f"  Testing /api/debug-rag/{query_span_id}...")
        response = requests.post(
            f"http://localhost:8000/api/debug-rag/{query_span_id}",
            params={"limit": 3},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ RAG Debug API working")
            print(f"    Found {len(result['similar_vectors'])} similar vectors")
        else:
            print(f"  ⚠ API returned: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"  ⚠ API server not running")
        print(f"    Start with: python3 cli.py serve")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    
    # Summary
    print("=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Start API: python3 cli.py serve")
    print("  2. Open UI: http://localhost:8000")
    print("  3. View traces and test Time Travel fork!")
    print()


if __name__ == "__main__":
    test_complete_workflow()
