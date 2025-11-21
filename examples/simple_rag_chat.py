"""
Simple RAG Chat Application - Example Usage of AgentScope Local

This example shows how a new user would instrument their own RAG application
to debug it with AgentScope Local.

Prerequisites:
1. Ollama installed and running: `ollama serve`
2. Model downloaded: `ollama pull qwen2.5:0.5b`
3. AgentScope Local server: `python3 cli.py serve`

Then run this script: `python3 examples/simple_rag_chat.py`
View traces at: http://localhost:8000
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import numpy as np
import hashlib
from opentelemetry import trace

# Step 1: Setup AgentScope instrumentation
from agentscope.instrumentation import setup_instrumentation
from agentscope.rag_logger import log_embedding

setup_instrumentation(
    service_name="my_rag_chatbot",
    db_path="debug_flight_recorder.db"
)

tracer = trace.get_tracer(__name__)


# Mock embedding function (in real app, use sentence-transformers or OpenAI)
def create_embedding(text: str, dimension: int = 384) -> list:
    """Create a simple mock embedding for demo purposes"""
    hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
    np.random.seed(hash_val % (2**32))
    vec = np.random.randn(dimension)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()


# RAG Knowledge Base
KNOWLEDGE_BASE = [
    "Python is a high-level programming language known for its simplicity.",
    "Machine learning is a subset of AI that learns from data.",
    "Ollama allows you to run large language models locally on your computer.",
    "RAG (Retrieval Augmented Generation) improves LLM responses with external knowledge.",
    "AgentScope Local helps you debug AI applications with tracing and vector search.",
]


def index_knowledge_base():
    """Index the knowledge base with embeddings"""
    with tracer.start_as_current_span("index_knowledge_base") as span:
        span.set_attribute("kb_size", len(KNOWLEDGE_BASE))
        
        print("📚 Indexing knowledge base...")
        for idx, doc in enumerate(KNOWLEDGE_BASE):
            embedding = create_embedding(doc)
            log_embedding(
                db_path="debug_flight_recorder.db",
                text=doc,
                vector=embedding,
                model_name="mock-embedding-384",
                metadata={"doc_id": idx, "source": "knowledge_base"},
                vector_type="document"
            )
            print(f"  ✓ Indexed doc {idx + 1}/{len(KNOWLEDGE_BASE)}")
        
        print(f"✅ Indexed {len(KNOWLEDGE_BASE)} documents\n")


def retrieve_relevant_docs(query: str, top_k: int = 3) -> list:
    """Retrieve relevant documents using vector similarity"""
    with tracer.start_as_current_span("retrieve_docs") as span:
        span.set_attribute("query", query)
        span.set_attribute("top_k", top_k)
        
        print(f"🔍 Searching for: '{query}'")
        
        # Create query embedding
        query_embedding = create_embedding(query)
        
        # Log query embedding (this enables RAG debugging in the UI!)
        log_embedding(
            db_path="debug_flight_recorder.db",
            text=query,
            vector=query_embedding,
            model_name="mock-embedding-384",
            metadata={"type": "query"},
            vector_type="query"
        )
        
        # In a real app, you'd do similarity search here
        # For demo, just return top documents
        retrieved = KNOWLEDGE_BASE[:top_k]
        span.set_attribute("retrieved_count", len(retrieved))
        
        print(f"  Found {len(retrieved)} relevant documents\n")
        return retrieved


def call_ollama_llm(prompt: str, context: list) -> str:
    """Call Ollama LLM with enhanced performance tracking"""
    import time
    from agentscope.performance_tracker import PerformanceTracker
    from agentscope.resource_monitor import ResourceMonitor
    
    with tracer.start_as_current_span("ollama_call") as span:
        # Model configuration (Week 6: Configuration tracking)
        temperature = 0.7
        max_tokens = 500
        
        # Set attributes for model detection
        span.set_attribute("gen_ai.system", "ollama")
        span.set_attribute("gen_ai.request.model", "qwen2.5:0.5b")
        span.set_attribute("gen_ai.prompt", prompt)
        
        # Track model configuration (Week 6)
        span.set_attribute("gen_ai.request.temperature", temperature)
        span.set_attribute("gen_ai.request.max_tokens", max_tokens)
        span.set_attribute("gen_ai.model.context_window", 4096)  # qwen2.5 limit
        
        # Initialize performance tracker (Week 6)
        tracker = PerformanceTracker(span)
        
        # Capture resource usage before call (Week 6)
        ResourceMonitor.capture(span)
        
        # Build RAG prompt
        context_str = "\n".join([f"- {doc}" for doc in context])
        full_prompt = f"""Based on the following context, answer the question:

Context:
{context_str}

Question: {prompt}

Answer:"""
        
        print("💬 Calling Ollama LLM...")
        print(f"  Model: qwen2.5:0.5b")
        print(f"  Temperature: {temperature}")
        print(f"  Max tokens: {max_tokens}")
        print(f"  Context docs: {len(context)}")
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:0.5b",
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            completion = result.get("response", "")
            span.set_attribute("gen_ai.completion", completion)
            
            # Track tokens
            completion_tokens = result.get("eval_count", 0)
            prompt_tokens = result.get("prompt_eval_count", 0)
            
            if completion_tokens:
                span.set_attribute("gen_ai.usage.completion_tokens", completion_tokens)
                # Mark first token for TTFT (simulated for non-streaming)
                tracker.mark_first_token()
                # Set total tokens generated for TPS calculation
                tracker.set_tokens(completion_tokens)
            
            if prompt_tokens:
                span.set_attribute("gen_ai.usage.prompt_tokens", prompt_tokens)
            
            # Finalize performance metrics (Week 6)
            tracker.finalize()
            
            # Get and display performance metrics
            metrics = tracker.get_metrics()
            print(f"  ✓ Got response ({len(completion)} chars)")
            if 'ttft_ms' in metrics:
                print(f"  ⚡ TTFT: {metrics['ttft_ms']:.0f}ms")
            if 'tokens_per_second' in metrics:
                print(f"  ⚡ Speed: {metrics['tokens_per_second']:.1f} tokens/sec")
            if 'generation_time_ms' in metrics:
                print(f"  ⚡ Total time: {metrics['generation_time_ms']:.0f}ms")
            print()
            
            return completion
            
        except requests.exceptions.ConnectionError:
            error_msg = "Ollama not running. Start with: ollama serve"
            span.set_attribute("error", True)
            span.set_attribute("error.message", error_msg)
            print(f"  ✗ Error: {error_msg}\n")
            return error_msg
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            print(f"  ✗ Error: {e}\n")
            return f"Error: {e}"


def call_ollama_llm_streaming(prompt: str, context: list) -> str:
    """Call Ollama LLM with streaming enabled (Week 7)"""
    import json
    from agentscope.streaming_tracker import StreamingTracker
    from agentscope.resource_monitor import ResourceMonitor
    
    with tracer.start_as_current_span("ollama_call_streaming") as span:
        # Model configuration
        temperature = 0.7
        max_tokens = 500
        
        # Set attributes for model detection
        span.set_attribute("gen_ai.system", "ollama")
        span.set_attribute("gen_ai.request.model", "qwen2.5:0.5b")
        span.set_attribute("gen_ai.prompt", prompt)
        
        # Track model configuration
        span.set_attribute("gen_ai.request.temperature", temperature)
        span.set_attribute("gen_ai.request.max_tokens", max_tokens)
        span.set_attribute("gen_ai.model.context_window", 4096)
        
        # Initialize streaming tracker (Week 7)
        stream_tracker = StreamingTracker(span)
        
        # Capture resource usage
        ResourceMonitor.capture(span)
        
        # Build RAG prompt
        context_str = "\n".join([f"- {doc}" for doc in context])
        full_prompt = f"""Based on the following context, answer the question:

Context:
{context_str}

Question: {prompt}

Answer:"""
        
        print("💬 Calling Ollama LLM (streaming)...")
        print(f"  Model: qwen2.5:0.5b")
        print(f"  Temperature: {temperature}")
        print(f"  Max tokens: {max_tokens}")
        print(f"  Context docs: {len(context)}")
        print()
        print("  📡 Streaming response: ", end="", flush=True)
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:0.5b",
                    "prompt": full_prompt,
                    "stream": True,  # Enable streaming!
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                stream=True,  # Important for streaming
                timeout=60
            )
            response.raise_for_status()
            
            full_response = ""
            chunk_count = 0
            
            # Process streaming chunks
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    chunk_text = chunk.get("response", "")
                    
                    if chunk_text:
                        full_response += chunk_text
                        stream_tracker.record_chunk(chunk_text)
                        chunk_count += 1
                        print(chunk_text, end="", flush=True)
                    
                    # Check if this is the final chunk
                    if chunk.get("done", False):
                        # Get token counts from final chunk
                        completion_tokens = chunk.get("eval_count", 0)
                        prompt_tokens = chunk.get("prompt_eval_count", 0)
                        
                        if prompt_tokens:
                            span.set_attribute("gen_ai.usage.prompt_tokens", prompt_tokens)
            
            print()  # New line after streaming
            
            # Finalize streaming metrics (Week 7)
            stream_tracker.finalize()
            span.set_attribute("gen_ai.completion", full_response)
            
            # Get and display streaming metrics
            metrics = stream_tracker.get_metrics()
            print()
            print(f"  ✓ Got response ({len(full_response)} chars)")
            print(f"  📡 Chunks: {metrics.get('chunk_count', 0)}")
            if 'ttft_ms' in metrics:
                print(f"  ⚡ TTFT: {metrics['ttft_ms']:.0f}ms (first chunk)")
            if 'tokens_per_second' in metrics:
                print(f"  ⚡ Speed: {metrics['tokens_per_second']:.1f} tokens/sec")
            if 'per_token_ms' in metrics:
                print(f"  ⚡ Per-token latency: {metrics['per_token_ms']:.1f}ms")
            if 'avg_inter_chunk_ms' in metrics:
                print(f"  ⚡ Avg inter-chunk: {metrics['avg_inter_chunk_ms']:.1f}ms")
            if 'total_time_ms' in metrics:
                print(f"  ⚡ Total time: {metrics['total_time_ms']:.0f}ms")
            print()
            
            return full_response
            
        except requests.exceptions.ConnectionError:
            error_msg = "Ollama not running. Start with: ollama serve"
            span.set_attribute("error", True)
            span.set_attribute("error.message", error_msg)
            print(f"\n  ✗ Error: {error_msg}\n")
            return error_msg
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            print(f"\n  ✗ Error: {e}\n")
            return f"Error: {e}"



def chat(question: str):
    """Main RAG chat function"""
    with tracer.start_as_current_span("rag_chat") as span:
        span.set_attribute("question", question)
        
        print("=" * 70)
        print(f"❓ Question: {question}")
        print("=" * 70)
        print()
        
        # Retrieve relevant documents
        context = retrieve_relevant_docs(question, top_k=3)
        
        # Call LLM with context
        answer = call_ollama_llm(question, context)
        
        span.set_attribute("answer", answer)
        
        print("💡 Answer:")
        print(f"  {answer}")
        print()
        
        return answer


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 Simple RAG Chatbot - Instrumented with AgentScope Local")
    print("=" * 70)
    print()
    
    # Index knowledge base (only needed once)
    index_knowledge_base()
    
    # Example queries
    questions = [
        "What is Ollama?",
        "How can I debug my AI application?",
        "Tell me about Python programming",
    ]
    
    for question in questions:
        chat(question)
        print()
    
    print("=" * 70)
    print("✅ Done! View traces at: http://localhost:8000")
    print("=" * 70)
    print()
    print("🎯 What to do next:")
    print("  1. Open http://localhost:8000 in your browser")
    print("  2. Click 'Refresh' to load the traces")
    print("  3. Select a trace to see the RAG workflow")
    print("  4. Click 'Debug RAG' on query spans to see similar vectors")
    print("  5. Click 'Time Travel Fork' on LLM spans to modify prompts")
    print()
