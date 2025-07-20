"""
Graph module for AICoder multi-agent system.

This module provides LangGraph workflow creation and management capabilities
for coordinating the multi-agent system.
"""

from typing import Dict, Any, List, Optional

try:
    from .langgraph_builder import AICoderGraphBuilder
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available. Install with: pip install langgraph")

def create_workflow_from_contracts(
    workflow_type: str = "conditional",
    start_agent: str = "orchestrator",
    agents: List[str] = None,
    enable_checkpointing: bool = False,
    contracts_dir: str = "contracts"
) -> Optional[Any]:
    """
    Create a workflow using agent contracts.
    
    Args:
        workflow_type: Type of workflow ("simple", "conditional")
        start_agent: The agent to start the workflow
        agents: List of agents to include (for simple workflow)
        enable_checkpointing: Whether to enable checkpointing
        contracts_dir: Directory containing agent contracts
    
    Returns:
        Compiled LangGraph workflow or None if unavailable
    """
    if not LANGGRAPH_AVAILABLE:
        print("Error: LangGraph not available")
        return None
    
    try:
        builder = AICoderGraphBuilder(contracts_dir)
        
        if workflow_type == "simple":
            workflow = builder.create_simple_workflow(agents)
        elif workflow_type == "conditional":
            workflow = builder.create_conditional_workflow(start_agent)
        else:
            print(f"Error: Unknown workflow type '{workflow_type}'")
            return None
        
        if workflow and enable_checkpointing:
            workflow = builder.add_checkpointing(workflow)
        
        return workflow
        
    except Exception as e:
        print(f"Error creating workflow: {e}")
        return None

def get_available_agents(contracts_dir: str = "contracts") -> List[str]:
    """
    Get list of available agents from contracts.
    
    Args:
        contracts_dir: Directory containing agent contracts
    
    Returns:
        List of available agent names
    """
    if not LANGGRAPH_AVAILABLE:
        return []
    
    try:
        builder = AICoderGraphBuilder(contracts_dir)
        return builder.list_available_agents()
    except Exception as e:
        print(f"Error loading agents: {e}")
        return []

def get_agent_config(agent_name: str, contracts_dir: str = "contracts") -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent
        contracts_dir: Directory containing agent contracts
    
    Returns:
        Agent configuration or None if not found
    """
    if not LANGGRAPH_AVAILABLE:
        return None
    
    try:
        builder = AICoderGraphBuilder(contracts_dir)
        return builder.get_agent_config(agent_name)
    except Exception as e:
        print(f"Error loading agent config: {e}")
        return None

def validate_workflow(workflow: Any) -> bool:
    """
    Validate a workflow configuration.
    
    Args:
        workflow: The workflow to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not LANGGRAPH_AVAILABLE:
        return False
    
    try:
        builder = AICoderGraphBuilder()
        return builder.validate_workflow(workflow)
    except Exception as e:
        print(f"Error validating workflow: {e}")
        return False

def get_workflow_info(workflow: Any, contracts_dir: str = "contracts") -> Dict[str, Any]:
    """
    Get information about a workflow.
    
    Args:
        workflow: The workflow to analyze
        contracts_dir: Directory containing agent contracts
    
    Returns:
        Dictionary with workflow information
    """
    if not LANGGRAPH_AVAILABLE:
        return {"error": "LangGraph not available"}
    
    try:
        builder = AICoderGraphBuilder(contracts_dir)
        return builder.get_workflow_info(workflow)
    except Exception as e:
        return {"error": f"Error getting workflow info: {e}"}

# Factory functions for common workflow patterns
def create_simple_workflow(agents: List[str] = None, contracts_dir: str = "contracts") -> Optional[Any]:
    """Create a simple linear workflow."""
    return create_workflow_from_contracts(
        workflow_type="simple",
        agents=agents,
        contracts_dir=contracts_dir
    )

def create_orchestrator_workflow(contracts_dir: str = "contracts") -> Optional[Any]:
    """Create a conditional workflow starting with orchestrator."""
    return create_workflow_from_contracts(
        workflow_type="conditional",
        start_agent="orchestrator",
        contracts_dir=contracts_dir
    )

def create_planner_workflow(contracts_dir: str = "contracts") -> Optional[Any]:
    """Create a conditional workflow starting with planner."""
    return create_workflow_from_contracts(
        workflow_type="conditional",
        start_agent="planner",
        contracts_dir=contracts_dir
    )

# Export main classes and functions
__all__ = [
    "AICoderGraphBuilder",
    "create_workflow_from_contracts",
    "get_available_agents", 
    "get_agent_config",
    "validate_workflow",
    "get_workflow_info",
    "create_simple_workflow",
    "create_orchestrator_workflow",
    "create_planner_workflow"
]
