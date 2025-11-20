# AgentScope Local

AgentScope Local is a local-first AI debugging flight recorder designed to capture, store, and visualize the execution of AI agents.

## Features

- **Capture Layer**: OpenTelemetry instrumentation to capture traces from your agent.
- **Storage Engine**: SQLite database with `sqlite-vec` for storing traces and vector embeddings locally.
- **Visualization**: React-based UI to view traces, timelines, and vector details.

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+

### Installation

1. **Backend Setup**

   ```bash
   cd AgentScopeLocal
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend API**

   ```bash
   # In AgentScopeLocal directory
   source venv/bin/activate
   python api.py
   ```

2. **Start the Frontend**

   ```bash
   # In frontend directory
   npm run dev
   ```

3. **Generate Traces**
   Run the test script to simulate an agent:
   ```bash
   python test_agent.py
   ```

## Architecture

- **Backend**: Python, FastAPI, OpenTelemetry, SQLite, sqlite-vec
- **Frontend**: React, TypeScript, Tailwind CSS, Vite

## License

MIT
