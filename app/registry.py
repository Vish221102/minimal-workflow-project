from typing import Callable, Dict, Any

# A simple registry to hold available node functions
class ToolRegistry:
    _registry: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a function as a node tool."""
        def decorator(func: Callable):
            cls._registry[name] = func
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        return cls._registry.get(name)

# Initializer to ensure workflows are loaded
def load_tools():
    from app import workflows