"""
Planner Agent

This agent is responsible for planning the architecture of what needs to be built
and the steps to build it efficiently and accurately. It provides a base structure
and architecture to follow while maintaining flexibility.
"""

from typing import Dict, Any, List
import logging
import json
from services.llm import generate_agent_response

# Configure logging
logger = logging.getLogger(__name__)

# LLM service is imported and used via generate_agent_response function

def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Planner node that creates a comprehensive plan and architecture for the project.
    
    Args:
        state: The current state containing user requirements and context
        
    Returns:
        Updated state with planning results
    """
    try:
        # Extract relevant information from state
        user_input = state.get("user_input", "")
        requirements = state.get("requirements", "")
        context = state.get("context", "")
        existing_codebase = state.get("existing_codebase", {})
        
        # Build the planning prompt
        prompt = f"""
        You are an expert software architect and project planner. Create a comprehensive plan for the following project:
        
        User Input: {user_input}
        Requirements: {requirements}
        Context: {context}
        Existing Codebase: {existing_codebase}
        
        Please provide:
        1. Project Architecture Overview
        2. File Structure and Organization
        3. Technology Stack Recommendations
        4. Implementation Steps (detailed breakdown)
        5. Dependencies and Requirements
        6. Testing Strategy
        7. Deployment Considerations
        
        Format your response as a structured plan that can be easily parsed and followed by other agents.
        """
        
        # Generate plan using centralized LLM service
        plan_content = generate_agent_response("planner", prompt)
        
        # Parse and structure the plan
        structured_plan = parse_plan(plan_content)
        
        # Update state with planning results
        updated_state = state.copy()
        updated_state["plan"] = structured_plan
        updated_state["planning_status"] = "completed"
        updated_state["file_structure"] = structured_plan.get("file_structure", {})
        updated_state["implementation_steps"] = structured_plan.get("implementation_steps", [])
        
        logger.info("Planning completed successfully")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in planner node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["planning_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def parse_plan(plan_content: str) -> Dict[str, Any]:
    """
    Parse the LLM response into a structured plan.
    
    Args:
        plan_content: Raw plan content from LLM
        
    Returns:
        Structured plan dictionary
    """
    try:
        # Try to extract JSON-like structure from the response
        # This is a simplified parser - you might want to use more sophisticated parsing
        structured_plan = {
            "architecture": "",
            "file_structure": {},
            "technology_stack": [],
            "implementation_steps": [],
            "dependencies": [],
            "testing_strategy": "",
            "deployment_notes": ""
        }
        
        # Basic parsing logic - extract sections
        lines = plan_content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if "architecture" in line.lower() or "overview" in line.lower():
                current_section = "architecture"
            elif "file structure" in line.lower() or "organization" in line.lower():
                current_section = "file_structure"
            elif "technology stack" in line.lower() or "tech stack" in line.lower():
                current_section = "technology_stack"
            elif "implementation" in line.lower() or "steps" in line.lower():
                current_section = "implementation_steps"
            elif "dependencies" in line.lower():
                current_section = "dependencies"
            elif "testing" in line.lower():
                current_section = "testing_strategy"
            elif "deployment" in line.lower():
                current_section = "deployment_notes"
            else:
                # Add content to current section
                if current_section:
                    if isinstance(structured_plan[current_section], list):
                        structured_plan[current_section].append(line)
                    elif isinstance(structured_plan[current_section], str):
                        structured_plan[current_section] += "\n" + line
        
        return structured_plan
        
    except Exception as e:
        logger.error(f"Error parsing plan: {str(e)}")
        return {"error": str(e)}

def decompose_tasks(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Break down the plan into specific, actionable tasks.
    
    Args:
        plan: The structured plan
        
    Returns:
        List of specific tasks
    """
    tasks = []
    
    # Convert implementation steps to tasks
    for i, step in enumerate(plan.get("implementation_steps", [])):
        task = {
            "id": f"task_{i+1}",
            "description": step,
            "status": "pending",
            "priority": "medium",
            "dependencies": [],
            "estimated_effort": "medium"
        }
        tasks.append(task)
    
    return tasks

def validate_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the generated plan for completeness and feasibility.
    
    Args:
        plan: The plan to validate
        
    Returns:
        Validation results
    """
    validation_result = {
        "is_valid": True,
        "issues": [],
        "recommendations": []
    }
    
    # Check for required sections
    required_sections = ["architecture", "file_structure", "implementation_steps"]
    for section in required_sections:
        if not plan.get(section):
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Missing required section: {section}")
    
    # Add more validation logic as needed
    
    return validation_result