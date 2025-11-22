# Changelog

All notable changes to AgentScope Local will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-11-22

### Added

- **Beautiful Terminal UI** with Rich library
  - Comprehensive LLM metrics display (TTFT, TPS, tokens, temperature, CPU, RAM)
  - Gradient progress bars and color-coded thresholds
  - ASCII art header and session summaries
  - Real-time streaming token visualization
- **Minimal Integration** - 2-3 line setup with `ag.init()`
- **Unified LLM Wrapper** - `ag.llm.chat()` for all providers
  - Auto-tracing for Ollama, OpenAI, Anthropic
  - Built-in streaming support with live terminal output
  - Performance tracking integrated
- **Decorator Pattern** - `@ag.trace` for automatic span creation
- **Web UI Launcher** - `ag.web.open()` for quick browser access
- **Session Manager** - Replaces standalone server architecture
- **Framework Compatibility** - 100% verified with 29+ frameworks
  - LangChain, LlamaIndex, Haystack, DSPy, CrewAI, AutoGPT
  - All RAG frameworks (GraphRAG, LightRAG, R2R, etc.)
  - All vector databases (Pinecone, Weaviate, Chroma, etc.)
- **Examples** - Comprehensive integration demos
- **Documentation** - Complete README rewrite

### Changed

- Updated package structure with `core/`, `integrations/`, `ui/` modules
- Improved database .gitignore rules
- Version bumped to 1.5.0

### Fixed

- Database files no longer tracked in git
- Import paths for package installation

## [1.0.0] - 2025-11-XX

### Added

- Initial release
- SQLite-based trace storage with sqlite-vec
- OpenTelemetry instrumentation
- Web UI for trace inspection
- RAG debugging with vector similarity
- Time Travel feature to fork and replay LLM calls
- Performance metrics tracking
- Resource monitoring (CPU, memory, GPU)
- Streaming support with detailed metrics
- Model detection and cost tracking
- Multi-provider support (Ollama, OpenAI, Anthropic)

---

## Release Notes

### Version 1.5.0 - "Package Refactor"

This release transforms AgentScope into a minimal-integration package with stunning terminal UI and universal framework support.

**Key Highlights:**

- Reduce integration from ~20 lines to just 2-3 lines
- See comprehensive metrics in your terminal without opening a browser
- Works with ANY Python AI framework (verified 100% compatibility)
- Beautiful, modern design with vibrant colors and progress bars

**Migration from 1.0.0:**
The V1 API (`setup_instrumentation()`) still works! No breaking changes. The new API is additive.

Old way (still works):

```python
from agentscope.instrumentation import setup_instrumentation
setup_instrumentation(...)
```

New way (recommended):

```python
import agentscope as ag
ag.init()  # That's it!
```
