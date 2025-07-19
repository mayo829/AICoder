"""
Graph Module

LangGraph workflow management for the AICoder multi-agent system.
Provides tools for building, configuring, and executing multi-agent workflows.
"""

from .langgraph_builder import (
    AICoderGraphBuilder,
    create_aicoder_workflow,
    load_agent_nodes
)

# Try to import LangGraph components for convenience
try:
    import langgraph
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    # ToolExecutor might not be available in all versions
    try:
        from langgraph.prebuilt import ToolExecutor
    except ImportError:
        ToolExecutor = None
    LANGGRAPH_AVAILABLE = True
    print(f"✅ LangGraph imported successfully")
except ImportError as e:
    StateGraph = None
    END = None
    MemorySaver = None
    ToolExecutor = None
    LANGGRAPH_AVAILABLE = False
    print(f"❌ LangGraph import failed: {e}")

__all__ = [
    # Main classes
    "AICoderGraphBuilder",
    
    # Factory functions
    "create_aicoder_workflow",
    "load_agent_nodes",
    
    # LangGraph components (if available)
    "StateGraph",
    "END", 
    "MemorySaver",
    "ToolExecutor",
    "LANGGRAPH_AVAILABLE"
]

# Version info
__version__ = "1.0.0"

def get_workflow_builder() -> AICoderGraphBuilder:
    """
    Get a configured AICoderGraphBuilder instance.
    
    Returns:
        Configured AICoderGraphBuilder
    """
    return AICoderGraphBuilder()

def create_default_workflow() -> StateGraph:
    """
    Create the default AICoder workflow with all agents.
    
    Returns:
        Configured StateGraph workflow
        
    Raises:
        ImportError: If LangGraph is not installed
    """
    if not LANGGRAPH_AVAILABLE:
        raise ImportError(
            "LangGraph is required. Install with: pip install langgraph"
        )
    
    return create_aicoder_workflow(
        workflow_type="conditional",
        enable_checkpointing=False
    )

def validate_workflow_setup() -> dict:
    """
    Validate that the workflow can be created with all required components.
    
    Returns:
        Validation results dictionary
    """
    builder = AICoderGraphBuilder()
    
    # Load nodes
    nodes = builder.load_agent_nodes()
    
    # Create workflow
    try:
        workflow = builder.create_conditional_workflow()
        workflow_valid = True
        workflow_error = None
    except Exception as e:
        workflow_valid = False
        workflow_error = str(e)
    
    # Validate
    validation = builder.validate_workflow()
    
    return {
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "nodes_loaded": len(nodes),
        "expected_nodes": 7,  # orchestrator, planner, enhancer, coder, tester, memory, toolbox
        "workflow_valid": workflow_valid,
        "workflow_error": workflow_error,
        "validation": validation,
        "ready": LANGGRAPH_AVAILABLE and workflow_valid and validation["valid"]
    }
