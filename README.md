# Minimal AI Workflow Engine

A backend-only, graph-based workflow engine built with FastAPI and Python. This system allows for the definition of nodes, edges, and shared state to execute autonomous agent workflows with branching and looping capabilities.

# 1 How to run

### 1. Setup

# Clone the repository
git clone <your-repo-url>
cd ai_engine_assignment

# Install dependencies
pip install -r requirements.txt

# start the server
uvicorn app.main:app --reload

The API will be available at http://127.0.0.1:8000.
Interactive API docs are available at http://127.0.0.1:8000/docs.

# Run the included test script to see the agent logic in action:
python test_workflow.py

# What happens when you run this?
Creates a Graph: Registers nodes (extract, complexity, issues, improve) and edges via the /graph/create endpoint.

Triggers a Run: Sends an initial state with "bad code" (score: 0) to /graph/run.

Polls for Completion: Watches the agent loop repeatedly until the code quality score meets the threshold (80/100)

# 2 What this Workflow engine supports

This engine is designed to be a lightweight, flexible foundation for agentic workflows. It supports:

Graph-Based Execution: Workflows are defined as a collection of Nodes (Python functions) connected by Edges.

Shared State Management: A dictionary-based state object flows between nodes, allowing functions to read previous results and modify the context dynamically.

Conditional Branching: Edges support logic (e.g., condition: "quality_score < 80"), enabling the graph to make decisions on where to route execution next.

Looping (Cycles): The engine supports cyclic graphs, allowing agents to retry steps or refine outputs repeatedly until a condition is met.

Async & Non-Blocking: Execution is handled via FastAPI BackgroundTasks and Python asyncio, allowing the API to respond immediately while long-running workflows process in the background.

Dynamic Tool Registry: A decorator-based registry (@ToolRegistry.register) allows easy mapping of JSON node definitions to actual Python logic.

# 3 What can be done to improve

Given more development time, I would enhance the system in the following areas:

Persistence Layer: Currently, graph definitions and run states are stored in memory dictionaries (GRAPHS, RUNS). I would replace this with PostgreSQL or SQLite to ensure workflows survive server restarts.

Robust Concurrency: While BackgroundTasks works for simple cases, I would integrate a proper task queue like Celery or Redis to manage heavy workloads and prevent task loss.

Real-Time Streaming: Instead of polling the state endpoint, I would implement WebSockets to stream execution logs and state updates to the client in real-time.

Security Sandbox: The current implementation uses eval() for simple condition checking. I would replace this with a safer expression parser to prevent potential code injection risks.

Visualizer: A frontend endpoint that renders the graph topology (nodes and edges) visually to help debug complex workflows.