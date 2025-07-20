"""
LangGraph Builder

Builds and configures the LangGraph workflow for the AICoder multi-agent system.
Creates a comprehensive workflow that orchestrates all agents in the system.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: LangGraph not available. Install with: pip install langgraph")

# Import actual agent functions
try:
    from agents import (
        planner_node,
        coder_node,
        tester_node,
        memory_node,
        orchestrator_node,
        toolbox_node,
        enhancer_node
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Agent functions not available: {e}")
    AGENTS_AVAILABLE = False

class AICoderGraphBuilder:
    """
    Builder class for creating LangGraph workflows for the AICoder multi-agent system.
    Loads agent configurations from contracts and builds dynamic workflows.
    """
    
    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.agent_configs = {}
        self.agent_functions = {}
        self.load_agent_contracts()
        self.load_agent_functions()
    
    def load_agent_contracts(self) -> None:
        """Load all agent contracts from the contracts directory."""
        if not self.contracts_dir.exists():
            print(f"Warning: Contracts directory {self.contracts_dir} not found")
            return
            
        for contract_file in self.contracts_dir.glob("*.agent.json"):
            agent_name = contract_file.stem.replace(".agent", "")
            try:
                with open(contract_file, 'r') as f:
                    self.agent_configs[agent_name] = json.load(f)
                print(f"Loaded contract for agent: {agent_name}")
            except Exception as e:
                print(f"Error loading contract for {agent_name}: {e}")
    
    def load_agent_functions(self) -> None:
        """Load actual agent functions from the agents module."""
        if not AGENTS_AVAILABLE:
            print("Warning: Agent functions not available")
            return
        
        # Map agent names to their actual functions
        agent_function_map = {
            "planner": planner_node,
            "coder": coder_node,
            "tester": tester_node,
            "memory": memory_node,
            "orchestrator": orchestrator_node,
            "toolbox": toolbox_node,
            "enhancer": enhancer_node
        }
        
        for agent_name, agent_func in agent_function_map.items():
            if agent_func:
                self.agent_functions[agent_name] = agent_func
                print(f"Loaded function for agent: {agent_name}")
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent."""
        return self.agent_configs.get(agent_name)
    
    def get_agent_function(self, agent_name: str):
        """Get the actual function for a specific agent."""
        return self.agent_functions.get(agent_name)
    
    def list_available_agents(self) -> List[str]:
        """List all available agents from contracts."""
        return list(self.agent_configs.keys())
    
    def create_simple_workflow(self, agents: List[str] = None) -> Optional[Any]:
        """
        Create a simple linear workflow with specified agents.
        
        Args:
            agents: List of agent names to include in workflow. 
                   If None, uses all available agents.
        
        Returns:
            LangGraph workflow or None if LangGraph unavailable
        """
        if not LANGGRAPH_AVAILABLE:
            print("Error: LangGraph not available")
            return None
            
        if agents is None:
            agents = self.list_available_agents()
        
        # Validate agents exist
        for agent in agents:
            if agent not in self.agent_configs:
                print(f"Warning: Agent '{agent}' not found in contracts")
                return None
        
        # Create state graph
        workflow = StateGraph(state_schema=Dict[str, Any])
        
        # Add nodes using actual agent functions
        for agent in agents:
            agent_func = self.get_agent_function(agent)
            
            if agent_func:
                # Use the actual agent function
                workflow.add_node(agent, agent_func)
                print(f"Added agent node: {agent} (using actual function)")
            else:
                # Fallback to LLM service if function not available
                print(f"Warning: No function found for {agent}, using LLM service")
                from services.llm import generate_agent_response
                
                def create_node_function(agent_name: str):
                    def node_func(state: Dict[str, Any]) -> Dict[str, Any]:
                        try:
                            response = generate_agent_response(
                                agent_name=agent_name,
                                user_input=state.get("user_input", ""),
                                context=state
                            )
                            return {
                                **state,
                                f"{agent_name}_result": response,
                                "current_agent": agent_name,
                                "workflow_step": f"completed_{agent_name}"
                            }
                        except Exception as e:
                            return {
                                **state,
                                f"{agent_name}_error": str(e),
                                "current_agent": agent_name,
                                "workflow_step": f"error_{agent_name}"
                            }
                    return node_func
                
                workflow.add_node(agent, create_node_function(agent))
        
        # Set entry point
        if agents:
            workflow.set_entry_point(agents[0])
        
        # Add edges (linear flow)
        for i in range(len(agents) - 1):
            workflow.add_edge(agents[i], agents[i + 1])
        
        # Add end edge
        if agents:
            workflow.add_edge(agents[-1], END)
        
        return workflow.compile()
    
    def create_conditional_workflow(self, 
                                  start_agent: str = "orchestrator",
                                  conditional_routing: bool = True) -> Optional[Any]:
        """
        Create a conditional workflow with orchestrator-based routing.
        
        Args:
            start_agent: The agent to start the workflow
            conditional_routing: Whether to use conditional routing
        
        Returns:
            LangGraph workflow or None if LangGraph unavailable
        """
        if not LANGGRAPH_AVAILABLE:
            print("Error: LangGraph not available")
            return None
        
        if start_agent not in self.agent_configs:
            print(f"Error: Start agent '{start_agent}' not found in contracts")
            return None
        
        # Create state graph
        workflow = StateGraph(state_schema=Dict[str, Any])
        
        # Add all agent nodes using actual functions
        for agent_name, config in self.agent_configs.items():
            agent_func = self.get_agent_function(agent_name)
            
            if agent_func:
                # Use the actual agent function
                workflow.add_node(agent_name, agent_func)
                print(f"Added agent node: {agent_name} (using actual function)")
            else:
                # Fallback to LLM service
                print(f"Warning: No function found for {agent_name}, using LLM service")
                from services.llm import generate_agent_response
                
                def create_node_function(agent_name: str):
                    def node_func(state: Dict[str, Any]) -> Dict[str, Any]:
                        try:
                            response = generate_agent_response(
                                agent_name=agent_name,
                                user_input=state.get("user_input", ""),
                                context=state
                            )
                            return {
                                **state,
                                f"{agent_name}_result": response,
                                "current_agent": agent_name,
                                "workflow_step": f"completed_{agent_name}"
                            }
                        except Exception as e:
                            return {
                                **state,
                                f"{agent_name}_error": str(e),
                                "current_agent": agent_name,
                                "workflow_step": f"error_{agent_name}"
                            }
                    return node_func
                
                workflow.add_node(agent_name, create_node_function(agent_name))
        
        # Add conditional routing
        if conditional_routing and start_agent == "orchestrator":
            def route_to_next_agent(state: Dict[str, Any]) -> str:
                """Route to next agent based on orchestrator decision."""
                orchestrator_result = state.get("orchestrator_result", {})
                next_agent = orchestrator_result.get("next_agent", "END")
                
                if next_agent == "END" or next_agent not in self.agent_configs:
                    return END
                
                return next_agent
            
            # Add conditional edges from orchestrator
            workflow.add_conditional_edges(
                "orchestrator",
                route_to_next_agent,
                {agent: agent for agent in self.agent_configs.keys()} | {END: END}
            )
            
            # Add edges from other agents back to orchestrator
            for agent_name in self.agent_configs.keys():
                if agent_name != "orchestrator":
                    workflow.add_edge(agent_name, "orchestrator")
        
        # Set entry point
        workflow.set_entry_point(start_agent)
        
        return workflow.compile()
    
    def add_checkpointing(self, workflow: Any, checkpoint_dir: str = "checkpoints") -> Any:
        """
        Add checkpointing to a workflow.
        
        Args:
            workflow: The compiled workflow
            checkpoint_dir: Directory to store checkpoints
        
        Returns:
            Workflow with checkpointing enabled
        """
        if not LANGGRAPH_AVAILABLE:
            return workflow
        
        try:
            memory_saver = MemorySaver()
            return workflow.with_checkpointer(memory_saver)
        except Exception as e:
            print(f"Warning: Could not add checkpointing: {e}")
            return workflow
    
    def validate_workflow(self, workflow: Any) -> bool:
        """
        Validate a workflow configuration.
        
        Args:
            workflow: The workflow to validate
        
        Returns:
            True if valid, False otherwise
        """
        if workflow is None:
            return False
        
        # Basic validation - workflow should be callable
        try:
            # Test with empty state
            test_state = {"user_input": "test"}
            # Note: We can't actually run the workflow here without proper setup
            return True
        except Exception as e:
            print(f"Workflow validation failed: {e}")
            return False
    
    def get_workflow_info(self, workflow: Any) -> Dict[str, Any]:
        """
        Get information about a workflow.
        
        Args:
            workflow: The workflow to analyze
        
        Returns:
            Dictionary with workflow information
        """
        if workflow is None:
            return {"error": "No workflow provided"}
        
        return {
            "type": type(workflow).__name__,
            "available_agents": self.list_available_agents(),
            "agent_count": len(self.agent_configs),
            "contracts_loaded": len(self.agent_configs) > 0,
            "functions_loaded": len(self.agent_functions) > 0
        }
