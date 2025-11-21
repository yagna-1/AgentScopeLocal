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
    """Call Ollama LLM with context"""
    with tracer.start_as_current_span("ollama_call") as span:
        # Set attributes for model detection
        span.set_attribute("gen_ai.system", "ollama")
        span.set_attribute("gen_ai.request.model", "qwen2.5:0.5b")
        span.set_attribute("gen_ai.prompt", prompt)
        
        # Build RAG prompt
        context_str = "\n".join([f"- {doc}" for doc in context])
        full_prompt = f"""Based on the following context, answer the question:

Context:
{context_str}

Question: {prompt}

Answer:"""
        
        print("💬 Calling Ollama LLM...")
        print(f"  Model: qwen2.5:0.5b")
        print(f"  Context docs: {len(context)}")
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:0.5b",
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            completion = result.get("response", "")
            span.set_attribute("gen_ai.completion", completion)
            
            # Track tokens
            if "eval_count" in result:
                span.set_attribute("gen_ai.usage.completion_tokens", result["eval_count"])
            if "prompt_eval_count" in result:
                span.set_attribute("gen_ai.usage.prompt_tokens", result["prompt_eval_count"])
            
            print(f"  ✓ Got response ({len(completion)} chars)\n")
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
