"""
Orchestrator Agent

This agent is responsible for coordinating and orchestrating the workflow between
all other agents in the system. It manages the state transitions, agent sequencing,
and overall project execution flow.
"""

from typing import Dict, Any, List, Callable
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import logging
import asyncio
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    max_tokens=2000
)

class WorkflowStatus(Enum):
    """Enumeration for workflow status"""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    ENHANCING = "enhancing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

def orchestrator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrator node that manages the overall workflow and coordinates agents.
    
    Args:
        state: The current state containing workflow information
        
    Returns:
        Updated state with orchestration results
    """
    try:
        # Extract workflow information
        current_status = state.get("workflow_status", WorkflowStatus.INITIALIZED.value)
        user_input = state.get("user_input", "")
        agent_results = state.get("agent_results", {})
        
        # Determine next action based on current status
        next_action = determine_next_action(current_status, state)
        
        # Update workflow status
        updated_state = state.copy()
        updated_state["workflow_status"] = next_action["status"]
        updated_state["next_agent"] = next_action["agent"]
        updated_state["orchestration_notes"] = next_action["notes"]
        
        # Add workflow metadata
        updated_state["workflow_metadata"] = {
            "current_step": next_action["step"],
            "total_steps": 6,  # planner, coder, tester, enhancer, memory, toolbox
            "progress": calculate_progress(current_status),
            "estimated_completion": estimate_completion_time(state)
        }
        
        logger.info(f"Orchestration completed. Next action: {next_action['agent']}")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in orchestrator node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["workflow_status"] = WorkflowStatus.FAILED.value
        updated_state["error"] = str(e)
        return updated_state

def determine_next_action(current_status: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine the next action based on current workflow status and state.
    
    Args:
        current_status: Current workflow status
        state: Current state
        
    Returns:
        Dictionary containing next action details
    """
    user_input = state.get("user_input", "")
    agent_results = state.get("agent_results", {})
    
    if current_status == WorkflowStatus.INITIALIZED.value:
        # Start with planning
        return {
            "status": WorkflowStatus.PLANNING.value,
            "agent": "planner",
            "step": 1,
            "notes": "Initializing project planning phase"
        }
    
    elif current_status == WorkflowStatus.PLANNING.value:
        # Check if planning is complete
        if agent_results.get("planner", {}).get("planning_status") == "completed":
            return {
                "status": WorkflowStatus.CODING.value,
                "agent": "coder",
                "step": 2,
                "notes": "Planning complete, proceeding to code generation"
            }
        else:
            return {
                "status": WorkflowStatus.PLANNING.value,
                "agent": "planner",
                "step": 1,
                "notes": "Continuing planning phase"
            }
    
    elif current_status == WorkflowStatus.CODING.value:
        # Check if coding is complete
        if agent_results.get("coder", {}).get("code_generation_status") == "completed":
            return {
                "status": WorkflowStatus.TESTING.value,
                "agent": "tester",
                "step": 3,
                "notes": "Code generation complete, proceeding to testing"
            }
        else:
            return {
                "status": WorkflowStatus.CODING.value,
                "agent": "coder",
                "step": 2,
                "notes": "Continuing code generation"
            }
    
    elif current_status == WorkflowStatus.TESTING.value:
        # Check if testing is complete
        if agent_results.get("tester", {}).get("testing_status") == "completed":
            return {
                "status": WorkflowStatus.ENHANCING.value,
                "agent": "enhancer",
                "step": 4,
                "notes": "Testing complete, proceeding to enhancement"
            }
        else:
            return {
                "status": WorkflowStatus.TESTING.value,
                "agent": "tester",
                "step": 3,
                "notes": "Continuing testing phase"
            }
    
    elif current_status == WorkflowStatus.ENHANCING.value:
        # Check if enhancement is complete
        if agent_results.get("enhancer", {}).get("enhancement_status") == "completed":
            return {
                "status": WorkflowStatus.COMPLETED.value,
                "agent": None,
                "step": 5,
                "notes": "All phases complete"
            }
        else:
            return {
                "status": WorkflowStatus.ENHANCING.value,
                "agent": "enhancer",
                "step": 4,
                "notes": "Continuing enhancement phase"
            }
    
    else:
        # Default case
        return {
            "status": WorkflowStatus.FAILED.value,
            "agent": None,
            "step": 0,
            "notes": "Unknown workflow status"
        }

def calculate_progress(current_status: str) -> float:
    """
    Calculate the progress percentage based on current status.
    
    Args:
        current_status: Current workflow status
        
    Returns:
        Progress percentage (0.0 to 1.0)
    """
    progress_map = {
        WorkflowStatus.INITIALIZED.value: 0.0,
        WorkflowStatus.PLANNING.value: 0.2,
        WorkflowStatus.CODING.value: 0.4,
        WorkflowStatus.TESTING.value: 0.6,
        WorkflowStatus.ENHANCING.value: 0.8,
        WorkflowStatus.COMPLETED.value: 1.0,
        WorkflowStatus.FAILED.value: 0.0
    }
    
    return progress_map.get(current_status, 0.0)

def estimate_completion_time(state: Dict[str, Any]) -> str:
    """
    Estimate the time to completion based on current state.
    
    Args:
        state: Current state
        
    Returns:
        Estimated completion time as string
    """
    # Simple estimation logic
    current_step = state.get("workflow_metadata", {}).get("current_step", 1)
    total_steps = 5
    
    if current_step == 1:
        return "10-15 minutes"
    elif current_step == 2:
        return "5-10 minutes"
    elif current_step == 3:
        return "3-5 minutes"
    elif current_step == 4:
        return "2-3 minutes"
    else:
        return "Less than 1 minute"

def validate_workflow_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the current workflow state for consistency.
    
    Args:
        state: Current state
        
    Returns:
        Validation results
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "recommendations": []
    }
    
    # Check for required fields
    required_fields = ["user_input", "workflow_status"]
    for field in required_fields:
        if not state.get(field):
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Missing required field: {field}")
    
    # Check workflow status consistency
    workflow_status = state.get("workflow_status")
    if workflow_status and workflow_status not in [status.value for status in WorkflowStatus]:
        validation_result["is_valid"] = False
        validation_result["issues"].append(f"Invalid workflow status: {workflow_status}")
    
    return validation_result

def pause_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pause the current workflow.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with paused status
    """
    updated_state = state.copy()
    updated_state["workflow_status"] = WorkflowStatus.PAUSED.value
    updated_state["paused_at"] = "current_timestamp"
    return updated_state

def resume_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resume a paused workflow.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with resumed status
    """
    updated_state = state.copy()
    # Determine the appropriate status to resume to
    previous_status = state.get("previous_status", WorkflowStatus.INITIALIZED.value)
    updated_state["workflow_status"] = previous_status
    updated_state["resumed_at"] = "current_timestamp"
    return updated_state
