"""Quick demo of beautiful terminal UI"""
import agentscope as ag

ag.init()

# Quick LLM call to showcase UI
response = ag.llm.chat(
    model="ollama/qwen2.5:0.5b",
    prompt="What is Python?",
    temperature=0.7,
    max_tokens=50
)

print(f"\n📝 Response: {response.text[:100]}...")
