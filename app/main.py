import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.models import (
    GraphCreateRequest, RunGraphRequest, RunStatusResponse
)
from app.engine import WorkflowEngine, GRAPHS, RUNS
from app.registry import load_tools

app = FastAPI(title="Minimal Workflow Engine")

# Load registered tools on startup
load_tools()

@app.post("/graph/create")
async def create_graph(request: GraphCreateRequest):
    """
    Register a new graph topology with validation.
    """
    # VALIDATION: Ensure all nodes referenced in edges actually exist
    node_ids = {n.id for n in request.nodes}
    for edge in request.edges:
        if edge.from_node not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge source '{edge.from_node}' not found in nodes.")
        if edge.to_node not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge target '{edge.to_node}' not found in nodes.")
            
    # VALIDATION: Ensure start_node exists
    if request.start_node not in node_ids:
        raise HTTPException(status_code=400, detail=f"Start node '{request.start_node}' not found.")

    graph_id = str(uuid.uuid4())
    GRAPHS[graph_id] = request
    return {"graph_id": graph_id, "message": "Graph created successfully"}

@app.post("/graph/run")
async def run_graph(request: RunGraphRequest, background_tasks: BackgroundTasks):
    """
    Start a workflow execution. Runs asynchronously in background.
    """
    if request.graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    graph_def = GRAPHS[request.graph_id]
    
    # Initialize engine
    engine = WorkflowEngine(graph_def, request.initial_state)
    
    # Store initial pending state
    RUNS[engine.run_id] = {"status": "running", "state": engine.state}
    
    # Run in background (non-blocking)
    background_tasks.add_task(engine.run)
    
    return {
        "run_id": engine.run_id, 
        "status": "queued",
        "message": "Workflow started in background"
    }

@app.get("/graph/state/{run_id}")
async def get_run_state(run_id: str) -> RunStatusResponse:
    """
    Retrieve the current state and logs of a workflow.
    """
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run ID not found")
    
    run_data = RUNS[run_id]
    return RunStatusResponse(
        run_id=run_id,
        status=run_data["status"],
        state=run_data["state"]
    )