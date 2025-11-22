"""Test ag.web.open() functionality"""
import agentscope as ag

# Initialize in terminal mode
ag.init()

# Make a quick LLM call to generate some traces
print("Making a test LLM call...")
response = ag.llm.chat(
    model="ollama/qwen2.5:0.5b",
    prompt="Say hello in one sentence.",
    temperature=0.7,
    max_tokens=20
)

print(f"\nLLM Response: {response.text}\n")

# Now open web UI
print("Opening web UI...")
ag.web.open()

print("\n✅ Web UI should open in your browser at http://localhost:8000")
print("Press Ctrl+C to stop the server when done.\n")

# Keep the script running so the web server stays active
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n👋 Shutting down...")
