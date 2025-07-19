"""
LangGraph Builder

Builds and configures the LangGraph workflow for the AICoder multi-agent system.
Creates a comprehensive workflow that orchestrates all agents in the system.
"""

import importlib
import json
import os
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    # ToolExecutor might not be available in all versions
    try:
        from langgraph.prebuilt import ToolExecutor
    except ImportError:
        ToolExecutor = None
except ImportError:
    print("Warning: LangGraph not installed. Install with: pip install langgraph")
    StateGraph = None
    END = None
    ToolExecutor = None
    MemorySaver = None

# Configure logging
logger = logging.getLogger(__name__)

class AICoderGraphBuilder:
    """
    Builder class for creating the AICoder LangGraph workflow.
    
    This class handles the creation and configuration of the multi-agent workflow
    that coordinates all agents in the AICoder system.
    """
    
    def __init__(self, contract_folder: str = "contracts"):
        self.contract_folder = Path(contract_folder)
        self.nodes = {}
        self.graph = None
        self.workflow_config = {}
        
    def load_agent_nodes(self) -> Dict[str, Callable]:
        """
        Load all agent nodes from the contracts folder.
        
        Returns:
            Dictionary mapping agent names to their node functions
        """
        nodes = {}
        
        # Define agent configurations (since some contract files are empty)
        agent_configs = {
            "orchestrator": {
                "path": "agents.orchestrator",
                "entrypoint": "orchestrator_node",
                "description": "Coordinates workflow and manages state transitions"
            },
            "planner": {
                "path": "agents.planner", 
                "entrypoint": "planner_node",
                "description": "Creates project plans and architecture"
            },
            "enhancer": {
                "path": "agents.enhancer",
                "entrypoint": "enhancer_node", 
                "description": "Enhances user prompts and interactions"
            },
            "coder": {
                "path": "agents.coder",
                "entrypoint": "coder_node",
                "description": "Generates code based on requirements"
            },
            "tester": {
                "path": "agents.tester",
                "entrypoint": "tester_node",
                "description": "Tests and validates generated code"
            },
            "memory": {
                "path": "agents.memory",
                "entrypoint": "memory_node",
                "description": "Manages long-term memory and context"
            },
            "toolbox": {
                "path": "agents.toolbox",
                "entrypoint": "toolbox_node",
                "description": "Provides utility functions and tools"
            }
        }
        
        for agent_name, config in agent_configs.items():
            try:
                # Import the module
                module = importlib.import_module(config["path"])
                
                # Get the node function
                node_func = getattr(module, config["entrypoint"])
                
                # Store the node
                nodes[agent_name] = node_func
                
                logger.info(f"Loaded agent node: {agent_name}")
                
            except (ImportError, AttributeError) as e:
                logger.error(f"Failed to load agent {agent_name}: {str(e)}")
                continue
        
        self.nodes = nodes
        return nodes
    
    def create_workflow_graph(self) -> StateGraph:
        """
        Create the LangGraph workflow with all agents.
        
        Returns:
            Configured StateGraph with the complete workflow
        """
        if StateGraph is None:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Load agent nodes
        nodes = self.load_agent_nodes()
        
        # Create the state graph
        workflow = StateGraph(state_schema=Dict[str, Any])
        
        # Add all nodes to the graph
        for agent_name, node_func in nodes.items():
            workflow.add_node(agent_name, node_func)
        
        # Define the workflow edges based on your architecture
        self._add_workflow_edges(workflow)
        
        # Set the entry point
        workflow.set_entry_point("orchestrator")
        
        # Compile the graph
        self.graph = workflow.compile()
        
        logger.info("Workflow graph created successfully")
        return self.graph
    
    def _add_workflow_edges(self, workflow: StateGraph):
        """
        Add edges to define the workflow flow between agents.
        
        Args:
            workflow: The StateGraph to add edges to
        """
        # Define the workflow routing logic
        def route_workflow(state: Dict[str, Any]) -> str:
            """
            Route the workflow based on current state and next agent.
            
            Args:
                state: Current workflow state
                
            Returns:
                Name of the next agent to execute, or END
            """
            workflow_status = state.get("workflow_status", "initialized")
            next_agent = state.get("next_agent")
            
            # If workflow is completed or failed, end
            if workflow_status in ["completed", "failed"]:
                return END
            
            # If there's a specific next agent, route to it
            if next_agent and next_agent in self.nodes:
                return next_agent
            
            # Default routing based on workflow status
            routing_map = {
                "initialized": "orchestrator",
                "planning": "planner", 
                "enhancing": "enhancer",
                "coding": "coder",
                "testing": "tester",
                "memory_processing": "memory",
                "tool_processing": "toolbox"
            }
            
            return routing_map.get(workflow_status, "orchestrator")
        
        # Add edges from each agent to the router
        for agent_name in self.nodes.keys():
            workflow.add_edge(agent_name, "orchestrator")
    
    def create_conditional_workflow(self) -> StateGraph:
        """
        Create a more sophisticated workflow with conditional routing.
        
        Returns:
            StateGraph with conditional workflow logic
        """
        if StateGraph is None:
            raise ImportError("LangGraph is required. Install with: pip install langgraph")
        
        # Load agent nodes
        nodes = self.load_agent_nodes()
        
        # Create the state graph
        workflow = StateGraph(state_schema=Dict[str, Any])
        
        # Add all nodes
        for agent_name, node_func in nodes.items():
            workflow.add_node(agent_name, node_func)
        
        # Add conditional routing
        self._add_conditional_edges(workflow)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Compile
        self.graph = workflow.compile()
        
        logger.info("Conditional workflow graph created successfully")
        return self.graph
    
    def _add_conditional_edges(self, workflow: StateGraph):
        """
        Add conditional edges for more sophisticated workflow routing.
        
        Args:
            workflow: The StateGraph to add conditional edges to
        """
        # Define conditional routing functions
        def should_continue_to_planner(state: Dict[str, Any]) -> str:
            """Decide whether to continue to planner or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "planner"
        
        def should_continue_to_enhancer(state: Dict[str, Any]) -> str:
            """Decide whether to continue to enhancer or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "enhancer"
        
        def should_continue_to_coder(state: Dict[str, Any]) -> str:
            """Decide whether to continue to coder or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "coder"
        
        def should_continue_to_tester(state: Dict[str, Any]) -> str:
            """Decide whether to continue to tester or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "tester"
        
        def should_continue_to_memory(state: Dict[str, Any]) -> str:
            """Decide whether to continue to memory or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "memory"
        
        def should_continue_to_toolbox(state: Dict[str, Any]) -> str:
            """Decide whether to continue to toolbox or end"""
            if state.get("workflow_status") == "failed":
                return END
            return "toolbox"
        
        def should_end_workflow(state: Dict[str, Any]) -> str:
            """Decide whether to end the workflow"""
            if state.get("workflow_status") in ["completed", "failed"]:
                return END
            return "orchestrator"
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "orchestrator",
            should_continue_to_planner
        )
        
        workflow.add_conditional_edges(
            "planner",
            should_continue_to_enhancer
        )
        
        workflow.add_conditional_edges(
            "enhancer", 
            should_continue_to_coder
        )
        
        workflow.add_conditional_edges(
            "coder",
            should_continue_to_tester
        )
        
        workflow.add_conditional_edges(
            "tester",
            should_continue_to_memory
        )
        
        workflow.add_conditional_edges(
            "memory",
            should_continue_to_toolbox
        )
        
        workflow.add_conditional_edges(
            "toolbox",
            should_end_workflow
        )
    
    def get_workflow_config(self) -> Dict[str, Any]:
        """
        Get the current workflow configuration.
        
        Returns:
            Dictionary containing workflow configuration
        """
        return {
            "nodes": list(self.nodes.keys()),
            "entry_point": "orchestrator",
            "workflow_type": "conditional" if hasattr(self, '_add_conditional_edges') else "simple",
            "state_type": "Dict[str, Any]",
            "checkpointing": True
        }
    
    def create_checkpointed_workflow(self, memory_saver: Optional[MemorySaver] = None) -> StateGraph:
        """
        Create a workflow with checkpointing for state persistence.
        
        Args:
            memory_saver: Optional MemorySaver for checkpointing
            
        Returns:
            StateGraph with checkpointing enabled
        """
        if MemorySaver is None:
            logger.warning("MemorySaver not available, creating workflow without checkpointing")
            return self.create_conditional_workflow()
        
        # Create the workflow
        workflow = self.create_conditional_workflow()
        
        # Add checkpointing
        if memory_saver:
            workflow = workflow.checkpointer(memory_saver)
            logger.info("Checkpointing enabled for workflow")
        
        return workflow
    
    def validate_workflow(self) -> Dict[str, Any]:
        """
        Validate the workflow configuration and nodes.
        
        Returns:
            Validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "node_count": len(self.nodes),
            "missing_nodes": []
        }
        
        # Check if all expected agents are loaded
        expected_agents = ["orchestrator", "planner", "enhancer", "coder", "tester", "memory", "toolbox"]
        
        for agent in expected_agents:
            if agent not in self.nodes:
                validation_results["missing_nodes"].append(agent)
                validation_results["warnings"].append(f"Agent {agent} not loaded")
        
        if validation_results["missing_nodes"]:
            validation_results["valid"] = False
        
        # Check if graph is compiled
        if not self.graph:
            validation_results["errors"].append("Workflow graph not compiled")
            validation_results["valid"] = False
        
        return validation_results

def create_aicoder_workflow(
    workflow_type: str = "conditional",
    enable_checkpointing: bool = True,
    contract_folder: str = "contracts"
) -> StateGraph:
    """
    Factory function to create an AICoder workflow.
    
    Args:
        workflow_type: Type of workflow ("simple", "conditional")
        enable_checkpointing: Whether to enable checkpointing
        contract_folder: Path to contracts folder
        
    Returns:
        Configured StateGraph workflow
    """
    builder = AICoderGraphBuilder(contract_folder)
    
    if workflow_type == "simple":
        workflow = builder.create_workflow_graph()
    elif workflow_type == "conditional":
        workflow = builder.create_conditional_workflow()
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    # Add checkpointing if requested
    if enable_checkpointing and MemorySaver is not None:
        try:
            memory_saver = MemorySaver()
            workflow = builder.create_checkpointed_workflow(memory_saver)
        except Exception as e:
            logger.warning(f"Checkpointing failed, using workflow without checkpointing: {e}")
            # Return the workflow without checkpointing if it fails
    
    return workflow

def load_agent_nodes(contract_folder: str = "contracts") -> Dict[str, Callable]:
    """
    Legacy function for backward compatibility.
    
    Args:
        contract_folder: Path to contracts folder
        
    Returns:
        Dictionary of agent nodes
    """
    builder = AICoderGraphBuilder(contract_folder)
    return builder.load_agent_nodes()
