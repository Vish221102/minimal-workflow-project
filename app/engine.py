import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, List
from .models import WorkflowState, GraphCreateRequest 

# In-memory storage
GRAPHS: Dict[str, GraphCreateRequest] = {}
RUNS: Dict[str, Dict[str, Any]] = {}

class WorkflowEngine:
    def __init__(self, graph_def: GraphCreateRequest, initial_data: Dict[str, Any]):
        self.graph_def = graph_def
        self.state = WorkflowState(data=initial_data)
        self.current_node_id = graph_def.start_node
        self.run_id = str(uuid.uuid4())
        self.status = "running"
        
        # Build adjacency map for O(1) lookups
        self.edges_map = {}
        for edge in graph_def.edges:
            if edge.from_node not in self.edges_map:
                self.edges_map[edge.from_node] = []
            self.edges_map[edge.from_node].append(edge)

    async def run(self):
        """Executes the workflow loop."""
        from app.registry import ToolRegistry

        try:
            while self.current_node_id and self.status == "running":
                # 1. Find the current node definition
                node_def = next((n for n in self.graph_def.nodes if n.id == self.current_node_id), None)
                if not node_def:
                    break
                
                # SIMULATION: Pause briefly to simulate "work"
                await asyncio.sleep(0.5)

                # 2. Get the function from registry and execute
                tool_func = ToolRegistry.get_tool(node_def.function_name)
                if not tool_func:
                    raise ValueError(f"Function {node_def.function_name} not found")

                # LOGGING: Add timestamp
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.state.history.append(f"[{timestamp}] Executing {node_def.id} ({node_def.function_name})")
                
                # Execute function (support async or sync)
                if asyncio.iscoroutinefunction(tool_func):
                    result_updates = await tool_func(self.state.data)
                else:
                    result_updates = tool_func(self.state.data)
                
                # Update state
                if result_updates:
                    self.state.data.update(result_updates)

                # 3. Determine next node (Routing/Branching)
                next_node = None
                possible_edges = self.edges_map.get(self.current_node_id, [])

                for edge in possible_edges:
                    # If edge has a condition, evaluate it against state
                    if edge.condition:
                        try:
                            # Allow safe access to state dict in condition string
                            if eval(edge.condition, {}, self.state.data):
                                next_node = edge.to_node
                                break
                        except Exception:
                            continue
                    else:
                        # Unconditional edge (default path)
                        next_node = edge.to_node
                        break
                
                self.current_node_id = next_node
                
                # Stop if no next node
                if not self.current_node_id:
                    self.status = "completed"

        except Exception as e:
            self.status = "failed"
            self.state.history.append(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {str(e)}")
        finally:
            # Save final state to memory
            RUNS[self.run_id] = {
                "status": self.status,
                "state": self.state
            }
            return self.run_id