# AgentScope Local - Examples

This directory contains example applications showing how to use AgentScope Local to debug your AI applications.

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install and start Ollama (if not already running)
ollama serve

# Download a small model
ollama pull qwen2.5:0.5b
```

### 2. Start AgentScope Local

```bash
# From the project root
python3 cli.py serve
```

This will start the server at http://localhost:8000

### 3. Run an Example

```bash
# Run the RAG chatbot example
python3 examples/simple_rag_chat.py
```

### 4. View the Traces

1. Open http://localhost:8000 in your browser
2. Click **Refresh** to load the traces
3. Select a trace to see the RAG workflow
4. Try the debugging features:
   - **Debug RAG**: Click on query spans to see vector similarity
   - **Time Travel Fork**: Click on LLM spans to modify and re-run prompts

---

## Examples

### `simple_rag_chat.py`

A complete RAG (Retrieval Augmented Generation) chatbot that shows:

- ✅ How to instrument your code with AgentScope
- ✅ How to log embeddings for RAG debugging
- ✅ How to trace LLM calls (Ollama)
- ✅ How to structure a RAG pipeline with proper spans

**What it does:**

1. Indexes a small knowledge base with embeddings
2. Takes user questions
3. Retrieves relevant documents
4. Calls Ollama LLM with context
5. Returns answers

**Tracing features:**

- Each step is wrapped in OpenTelemetry spans
- Embeddings are logged for RAG debugging
- LLM attributes are set for model detection
- Full trace tree visible in the UI

---

## Understanding the Code

### Basic Instrumentation

```python
from agentscope.instrumentation import setup_instrumentation

# Initialize at startup
setup_instrumentation(
    service_name="my_app",
    db_path="debug_flight_recorder.db"
)
```

### Creating Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### Logging Embeddings (for RAG Debugging)

```python
from agentscope.rag_logger import log_embedding

log_embedding(
    db_path="debug_flight_recorder.db",
    text="Your text here",
    vector=[0.1, 0.2, ...],  # Your embedding vector
    model_name="text-embedding-ada-002",
    metadata={"source": "document"},
    vector_type="document"  # or "query"
)
```

### Tracing LLM Calls

```python
with tracer.start_as_current_span("llm_call") as span:
    # Set these attributes for model detection
    span.set_attribute("gen_ai.system", "ollama")
    span.set_attribute("gen_ai.request.model", "qwen2.5:0.5b")
    span.set_attribute("gen_ai.prompt", prompt)

    # Make your LLM call
    response = call_llm(prompt)

    # Log the response
    span.set_attribute("gen_ai.completion", response)
    span.set_attribute("gen_ai.usage.prompt_tokens", prompt_tokens)
    span.set_attribute("gen_ai.usage.completion_tokens", completion_tokens)
```

---

## Debugging Features

### RAG Debugging

When you log embeddings with `vector_type="query"`, you can click the **Debug RAG** button in the UI to:

- See the top-K most similar vectors
- View similarity scores
- Understand why certain documents were/weren't retrieved
- Debug retrieval quality issues

### Time Travel Fork

When you trace LLM calls, you can click the **Time Travel Fork** button to:

- Modify the prompt
- Adjust temperature and max_tokens
- Re-run the LLM call
- Compare original vs. forked responses side-by-side

---

## Tips for Your Own Application

1. **Wrap key operations in spans** - This creates the trace tree
2. **Set meaningful attributes** - Helps with debugging later
3. **Log embeddings for queries** - Enables RAG debugging
4. **Follow OpenTelemetry conventions** - Use `gen_ai.*` attributes for LLM calls
5. **Use descriptive span names** - Makes traces easier to understand

---

## Common Issues

### Ollama not responding

```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list
```

### UI not showing traces

```bash
# Restart the server
pkill -f "cli.py serve"
python3 cli.py serve
```

### Database errors

```bash
# Clear the database and start fresh
python3 cli.py clear --force
```

---

## Next Steps

- Instrument your own application
- Try different LLM providers (OpenAI, Anthropic)
- Experiment with different embedding models
- Build more complex RAG pipelines
- Use Time Travel to optimize prompts

Happy debugging! 🎉
