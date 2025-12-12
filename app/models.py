from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field

# The shared state flowing between nodes 
class WorkflowState(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)
    # Execution log to track steps [cite: 36]
    history: List[str] = Field(default_factory=list) 

# Definition of a Node in the API request
class NodeDefinition(BaseModel):
    id: str
    function_name: str  # References a function in the Registry

# Definition of an Edge (Sequence) [cite: 19]
class EdgeDefinition(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Logic for branching [cite: 20]

# API Input: Create Graph [cite: 32]
class GraphCreateRequest(BaseModel):
    name: str
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node: str

# API Input: Run Graph [cite: 35]
class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

# API Output: Run Status [cite: 36, 38]
class RunStatusResponse(BaseModel):
    run_id: str
    status: Literal["running", "completed", "failed"]
    state: WorkflowState