import random
from .registry import ToolRegistry

@ToolRegistry.register("extract_functions")
def extract_functions(state: dict):
    # Simulates parsing code [cite: 46]
    code = state.get("code", "")
    return {"functions_found": ["func_a", "func_b"], "loc": len(code)}

@ToolRegistry.register("check_complexity")
def check_complexity(state: dict):
    # Simulates complexity check [cite: 47]
    loc = state.get("loc", 0)
    complexity = "high" if loc > 100 else "low"
    return {"complexity": complexity}

@ToolRegistry.register("detect_issues")
def detect_issues(state: dict):
    code = state.get("code", "")
    issues_found = 0
    issue_list = []

    # RULE 1: Check for 'print' statements (Production code shouldn't have them)
    print_count = code.count("print(")
    if print_count > 0:
        issues_found += print_count
        issue_list.append(f"Found {print_count} 'print' statements")

    # RULE 2: Check for 'TODO' comments
    todo_count = code.count("TODO")
    if todo_count > 0:
        issues_found += todo_count
        issue_list.append(f"Found {todo_count} TODOs")
        
    # RULE 3: Check for empty 'pass' blocks
    pass_count = code.count("pass")
    if pass_count > 0:
        issues_found += pass_count
        issue_list.append(f"Found {pass_count} empty 'pass' blocks")

    # If the user manually provided a count, we add it (optional), 
    # but now we mainly rely on our analysis.
    return {
        "issues_count": issues_found, 
        "analysis_log": issue_list
    }

@ToolRegistry.register("suggest_improvements")
def suggest_improvements(state: dict):
    # Simulates fixing code and updating score [cite: 49]
    issues = state.get("issues_count", 0)
    current_score = state.get("quality_score", 0)
    
    # Improve the code (reduce issues, increase score)
    new_issues = max(0, issues - 1)
    new_score = current_score + 20
    
    return {
        "issues_count": new_issues,
        "quality_score": new_score, 
        "improvements": f"Fixed 1 issue. Score is {new_score}"
    }

# NOTE: The loop logic (Step 5) is handled by the Graph Edges defined in the request,
# specifically checking "quality_score < threshold".