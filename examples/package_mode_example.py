"""
AgentScope Package Example - Minimal Integration

Demonstrates the new 2-3 line integration for AgentScope.
"""
import agentscope as ag

# ============================================================================
# Step 1: Initialize (One Line!)
# ============================================================================
ag.init()  # Terminal mode by default

print("✨ AgentScope initialized in terminal mode!\n")


# ============================================================================
# Step 2: Auto-Traced LLM Calls
# ============================================================================
print("📡 Example 1: Direct LLM Call\n")

response = ag.llm.chat(
    model="ollama/qwen2.5:0.5b",
    prompt="What is machine learning in one sentence?",
    temperature=0.7,
    max_tokens=100
)

print(f"\n💬 Response: {response.text}")
print(f"📊 Metrics: {response.metrics}\n")


# ============================================================================
# Step 3: Decorator-Based Tracing
# ============================================================================
print("\n🎯 Example 2: Custom Function with @ag.trace\n")

@ag.trace
def analyze_sentiment(text: str) -> str:
    """Analyze sentiment using LLM."""
    prompt = f"Analyze the sentiment of this text in one word (positive/negative/neutral): {text}"
    
    response = ag.llm.chat(
        model="ollama/qwen2.5:0.5b",
        prompt=prompt,
        temperature=0.3
    )
    
    return response.text.strip().lower()

sentiment = analyze_sentiment("I love using AgentScope!")
print(f"\n💭 Sentiment: {sentiment}\n")


# ============================================================================
# Step 4: Manual Spans
# ============================================================================
print("\n🔍 Example 3: Manual Span\n")

with ag.span("data_processing") as span:
    span.set_attribute("input_size", 100)
    
    # Simulate processing
    import time
    time.sleep(0.1)
    
    span.set_metric("items_processed", 100)
    print("✓ Data processing complete")


# ============================================================================
# Step 5: RAG Example
# ============================================================================
print("\n\n📚 Example 4: RAG Pipeline\n")

@ag.trace(name="rag_pipeline")
def rag_answer(question: str):
    """Simple RAG pipeline."""
    
    # Simulate document retrieval
    with ag.span("retrieval") as span:
        docs = [
            "Machine learning is a subset of AI.",
            "Deep learning uses neural networks.",
            "Python is popular for ML."
        ]
        span.set_metric("docs_retrieved", len(docs))
        
        # Log embeddings (for RAG debugging)
        for i, doc in enumerate(docs):
            ag.log_rag_embedding(
                text=doc,
                vector=[0.1 * i] * 384,  # Dummy vector
                type="document",
                metadata={"doc_id": i}
            )
    
    # Generate answer
    context = "\n".join(docs)
    
    response = ag.llm.chat(
        model="ollama/qwen2.5:0.5b",
        prompt=f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:",
        temperature=0.7
    )
    
    return response.text

answer = rag_answer("What is machine learning?")
print(f"\n💡 Answer: {answer}\n")


# ============================================================================
# Finish
# ============================================================================
print("\n" + "="*60)
print("✅ All examples complete!")
print("="*60)
print("\n💡 Tip: All traces were automatically captured!")
print("   Run `ag.web.open()` to inspect them in the browser.\n")
