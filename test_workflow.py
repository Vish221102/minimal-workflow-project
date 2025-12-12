import requests
import time
import json

# This script talks to your local server
BASE_URL = "http://127.0.0.1:8000"

def run_demo():
    print("1. Creating the Graph...")
    
    # Define the graph structure (Nodes & Edges)
    graph_payload = {
        "name": "Code Review Agent",
        "start_node": "node_extract",
        "nodes": [
            { "id": "node_extract", "function_name": "extract_functions" },
            { "id": "node_complexity", "function_name": "check_complexity" },
            { "id": "node_issues", "function_name": "detect_issues" },
            { "id": "node_improve", "function_name": "suggest_improvements" }
        ],
        "edges": [
            { "from_node": "node_extract", "to_node": "node_complexity" },
            { "from_node": "node_complexity", "to_node": "node_issues" },
            { "from_node": "node_issues", "to_node": "node_improve" },
            # The Loop: Keep improving until score is high enough
            { 
                "from_node": "node_improve", 
                "to_node": "node_improve", 
                "condition": "quality_score < 80" 
            }
        ]
    }

    try:
        # Step 1: Create the graph
        res = requests.post(f"{BASE_URL}/graph/create", json=graph_payload)
        
        # Check for errors (e.g., if a node ID is wrong)
        if res.status_code != 200:
            print(f" Failed to create graph: {res.text}")
            return
            
        graph_id = res.json()["graph_id"]
        print(f" Graph Created! ID: {graph_id}\n")
        
    except requests.exceptions.ConnectionError:
        print(" Could not connect to server. Is 'uvicorn' running?")
        return

    print("2. Starting the Run...")
    # Initial state mimicking bad code
    bad_code_sample = """
    def calculate():
        print("Starting calculation")  # Issue 1
        x = 10
        y = 20
        # TODO: Fix this later         # Issue 2
        print(x + y)                   # Issue 3
        print("Done")                  # Issue 4
    """
    initial_state = {
        "code": bad_code_sample,
        "quality_score": 0
        # Note: We are NOT sending "issues_count" anymore!
    }
    
    run_res = requests.post(f"{BASE_URL}/graph/run", json={
        "graph_id": graph_id,
        "initial_state": initial_state
    })
    
    # SAFETY CHECK: Handle server errors (fixes the KeyError)
    if run_res.status_code != 200:
        print(f" Error starting run: {run_res.text}")
        return

    run_id = run_res.json()["run_id"]
    print(f" Run Started! ID: {run_id}\n")

    print("3. Watching the agent work...")
    last_score = -1
    
    while True:
        # Step 3: Poll for status
        try:
            status_res = requests.get(f"{BASE_URL}/graph/state/{run_id}")
            if status_res.status_code != 200:
                print(f" Error getting state: {status_res.text}")
                break
                
            data = status_res.json()
            status = data["status"]
            state = data["state"]
            
            # Get current score safely
            current_score = state['data'].get('quality_score', 0)
            
            # Print update only if score changed (keeps console clean)
            if current_score != last_score:
                print(f"   Status: {status} |  Quality Score: {current_score}")
                last_score = current_score
            
            if status in ["completed", "failed"]:
                print("\n Workflow Finished!")
                
                print("\n Execution Log:")
                # Print the history (now with timestamps!)
                for entry in state['history']:
                    print(f"   {entry}")

                print("\n Final Data Snapshot:")
                print(json.dumps(state['data'], indent=2))
                break
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n Stopped by user.")
            break

if __name__ == "__main__":
    run_demo()