# 🕵️‍♂️ AgentScope Local

**The Local-First AI Flight Recorder for Debugging Agents**

AgentScope Local is a privacy-focused observability tool designed specifically for local LLM development. It captures, visualizes, and helps you debug your AI agents without sending data to the cloud.

![AgentScope Local UI](https://raw.githubusercontent.com/placeholder/screenshot.png)

---

## 🚀 Key Features

- **🔍 RAG Debugging**: Visualize vector retrieval, see what documents were fetched, and debug similarity scores.
- **⏱️ Time Travel Fork**: Replay any LLM call with modified prompts or parameters to test fixes instantly.
- **⚡ Performance Metrics**: Track TTFT (Time to First Token), TPS (Tokens/sec), and latency for every call.
- **🌊 Streaming Support**: Real-time visualization of streaming chunks, inter-chunk latency, and smooth rendering.
- **🔒 Privacy First**: All data is stored locally in SQLite. No API keys or data leave your machine.

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **Ollama** (recommended for local models)

### 1. Install & Setup

```bash
# Clone and setup backend
git clone https://github.com/yourusername/AgentScopeLocal.git
cd AgentScopeLocal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
npm run build
cd ..
```

### 2. Start the Server

```bash
# Start the all-in-one server (API + UI)
python cli.py serve
```

Visit **http://localhost:8000** to see the UI.

### 3. Run an Example

```bash
# In a new terminal (make sure venv is active)
python examples/simple_rag_chat.py
```

---

## 🤖 Local Model Support

AgentScope Local is built to work seamlessly with local models. It automatically identifies your model provider and configuration.

### How it Works

The system detects your local model setup using three methods (in order of priority):

1.  **Explicit Attributes**: If you set `gen_ai.system="ollama"` in your code.
2.  **URL Detection**: It recognizes common local endpoints:
    - `localhost:11434` → **Ollama**
    - `localhost:1234` → **LM Studio**
    - `localhost:8080` → **LocalAI**
3.  **Model Name Inference**: It guesses based on model names:
    - `llama`, `mistral`, `phi`, `qwen` → **Ollama**

### Supported Providers

| Provider      | Auto-Detection  | Notes                                       |
| ------------- | --------------- | ------------------------------------------- |
| **Ollama**    | ✅ Full Support | Streaming, Metrics, & Time Travel supported |
| **LM Studio** | ✅ Full Support | Compatible via OpenAI-style API             |
| **LocalAI**   | ✅ Full Support | Compatible via OpenAI-style API             |
| **OpenAI**    | ✅ Full Support | Requires API Key                            |
| **Anthropic** | ✅ Full Support | Requires API Key                            |

---

## 📂 Examples

### `simple_rag_chat.py`

A complete RAG (Retrieval Augmented Generation) chatbot that demonstrates:

- ✅ How to instrument your code with AgentScope
- ✅ How to log embeddings for RAG debugging
- ✅ How to trace LLM calls (Ollama)
- ✅ How to structure a RAG pipeline with proper spans

**Run it:**

```bash
python examples/simple_rag_chat.py
```

---

## 🔌 Instrumentation Guide

### 1. Basic Setup

```python
from agentscope.instrumentation import setup_instrumentation

# Initialize at startup
setup_instrumentation(
    service_name="my_app",
    db_path="debug_flight_recorder.db"
)
```

### 2. Creating Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### 3. Tracing LLM Calls

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

### 4. Logging Embeddings (for RAG Debugging)

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

---

## 💡 Tips for Your Application

1. **Wrap key operations in spans** - This creates the trace tree
2. **Set meaningful attributes** - Helps with debugging later
3. **Log embeddings for queries** - Enables RAG debugging
4. **Follow OpenTelemetry conventions** - Use `gen_ai.*` attributes for LLM calls
5. **Use descriptive span names** - Makes traces easier to understand

---

## 🛠️ Usage Guide

### 1. Debugging RAG (Retrieval)

- **Problem**: Your bot answers incorrectly because it retrieved the wrong documents.
- **Solution**:
  1.  Open the trace in AgentScope.
  2.  Click the **"Debug RAG"** button on the query span.
  3.  See exactly which chunks were retrieved and their similarity scores.
  4.  Identify if the issue is with the embedding or the retrieval logic.

### 2. Time Travel (Fixing Prompts)

- **Problem**: A prompt produced a bad response, and you want to fix it without re-running the whole app.
- **Solution**:
  1.  Find the LLM call in the trace.
  2.  Click **"Time Travel: Fork LLM Call"**.
  3.  Edit the prompt or change `temperature`.
  4.  Click **"Run Fork"** to see the new result side-by-side with the original.

### 3. Analyzing Performance

- **Problem**: Your app feels slow.
- **Solution**:
  1.  Check the **Performance Card** in the span details.
  2.  Look at **TTFT** (Time to First Token) - is the model taking too long to start?
  3.  Check **TPS** (Tokens Per Second) - is the generation speed acceptable?
  4.  Monitor **Resource Usage** (CPU/RAM) to see if your machine is overloaded.

---

## ❓ Troubleshooting

**Q: My traces aren't showing up.**
A: Click the **Refresh** button in the UI. If that fails, ensure you ran `python cli.py serve` and your application is pointing to the correct database path.

**Q: "Ollama not running" error.**
A: Ensure you have Ollama installed and running (`ollama serve`).

**Q: How do I clear the database?**
A: Run `python cli.py clear --force` to wipe all traces and start fresh.

---

## 🏗️ Architecture

- **Backend**: Python (FastAPI) + OpenTelemetry
- **Database**: SQLite + `sqlite-vec` (Vector Search)
- **Frontend**: React + TypeScript + Tailwind CSS

## 📄 License

MIT License
