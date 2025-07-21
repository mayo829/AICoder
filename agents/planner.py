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
        config = state.get("config", {})
        output_format = config.get("output_format", "python")
        
        # Build the planning prompt
        prompt = f"""
        You are an expert Next.js and React architect. Create a comprehensive TEMPLATE/OUTLINE for the following Next.js TSX project:
        
        User Input: {user_input}
        Requirements: {requirements}
        Context: {context}
        Existing Codebase: {existing_codebase}
        
        IMPORTANT: DO NOT GENERATE ANY ACTUAL CODE. Only provide a structured template/outline that describes what needs to be built.
        
        Please provide a structured template with:
        
        1. PROJECT OVERVIEW
            - Project name and description
            - Main features and functionality
            - Target audience and purpose
        
        2. FILE STRUCTURE TEMPLATE
            - Required files (page.tsx, layout.tsx, globals.css)
            - Optional components (Header.tsx, Hero.tsx, Features.tsx, etc.)
            - Component hierarchy and organization
        
        3. COMPONENT SPECIFICATIONS
            - Each component's purpose and functionality
            - Props and TypeScript interfaces needed
            - Styling requirements (Tailwind classes, colors, layout)
            - Whether it should be a server or client component
        
        4. PAGE STRUCTURE TEMPLATE
            - Main page sections (hero, features, testimonials, etc.)
            - Content requirements for each section
            - Layout and responsive design requirements
        
        5. STYLING TEMPLATE
            - Color scheme and design system
            - Typography requirements
            - Animation and transition specifications
            - Responsive breakpoints
        
        6. TECHNICAL REQUIREMENTS
            - Next.js version and features to use
            - TypeScript configuration
            - Tailwind CSS setup
            - Performance considerations
        
        7. CONTENT REQUIREMENTS
            - Text content for each section
            - Image placeholders and requirements
            - Call-to-action elements
            - Navigation structure
        
        8. IMPLEMENTATION PRIORITIES
            - Required files (must be implemented first)
            - Optional components (implement if time permits)
            - Error-free code requirements
            - Dependency-free implementation rules
        
        CRITICAL RULES FOR THE TEMPLATE:
        - NO ACTUAL CODE - only descriptions and specifications
        - Focus on structure, not implementation
        - Specify what each component should do, not how to do it
        - Include content requirements and design specifications
        - Define TypeScript interfaces and prop structures
        - Specify server vs client component requirements
        - Define styling requirements and design system
        
        CRITICAL TYPESCRIPT SYNTAX REQUIREMENTS:
        - Function parameters: Must use proper TypeScript syntax
        - Component props: Must define proper interfaces or inline types
        - Default exports: Must use correct export syntax
        - Import statements: Must use valid import syntax
        - JSX syntax: Must be properly structured without semicolons
        - TypeScript interfaces: Must be properly defined
        - Metadata exports: Must use correct export syntax for Next.js
        - No invalid syntax like function Component(: any) or trailing semicolons in JSX
        
        SYNTAX SPECIFICATIONS TO INCLUDE:
        - Component function signatures: function ComponentName({{ prop }}: Props) {{}}
        - Props interfaces: interface Props {{ prop: string }}
        - Import patterns: import Component from './Component'
        - Export patterns: export default function ComponentName() {{}}
        - JSX structure: Proper closing tags, no semicolons in attributes
        - TypeScript types: Proper type definitions for all props and state
        
        Format your response as a structured JSON-like template that can be easily parsed and followed by the coder agent.
        """
        
        # Log the prompt being sent
        logger.info("📋 Planner Prompt:")
        logger.info("-" * 30)
        logger.info(prompt)
        logger.info("-" * 30)
        
        # Generate plan using centralized LLM service
        plan_content = generate_agent_response("planner", prompt)
        
        # Log the raw plan content
        logger.info("📋 Planner Raw Output:")
        logger.info("-" * 50)
        logger.info(plan_content)
        logger.info("-" * 50)
        
        # Parse and structure the plan
        structured_plan = parse_plan(plan_content)
        
        # Update state with planning results
        updated_state = state.copy()
        updated_state["plan"] = structured_plan
        updated_state["planning_status"] = "completed"
        updated_state["file_structure"] = structured_plan.get("file_structure", {})
        updated_state["implementation_steps"] = structured_plan.get("implementation_steps", [])
        
        # Log structured plan summary
        logger.info("📋 Planner Structured Output:")
        logger.info(f"  Architecture: {len(str(structured_plan.get('architecture', '')))} chars")
        logger.info(f"  File Structure: {len(structured_plan.get('file_structure', {}))} items")
        logger.info(f"  Implementation Steps: {len(structured_plan.get('implementation_steps', []))} steps")
        logger.info(f"  Dependencies: {len(structured_plan.get('dependencies', []))} items")
        
        logger.info("✅ Planning completed successfully")
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
    Parse the LLM response into a structured plan template.
    
    Args:
        plan_content: Raw plan content from LLM
        
    Returns:
        Structured plan template dictionary
    """
    try:
        # Try to extract JSON-like structure from the response
        # This is a simplified parser - you might want to use more sophisticated parsing
        structured_plan = {
            "project_overview": {
                "name": "",
                "description": "",
                "features": [],
                "target_audience": ""
            },
            "file_structure": {
                "required_files": [],
                "optional_components": [],
                "component_hierarchy": {}
            },
            "component_specifications": {},
            "page_structure": {
                "sections": [],
                "content_requirements": {},
                "layout_requirements": {}
            },
            "styling_template": {
                "color_scheme": {},
                "typography": {},
                "animations": {},
                "responsive_breakpoints": {}
            },
            "technical_requirements": {
                "nextjs_version": "",
                "typescript_config": {},
                "tailwind_setup": {},
                "performance_considerations": []
            },
            "content_requirements": {
                "text_content": {},
                "image_requirements": {},
                "cta_elements": [],
                "navigation_structure": {}
            },
            "implementation_priorities": {
                "required_files": [],
                "optional_components": [],
                "error_free_requirements": [],
                "dependency_rules": []
            }
        }
        
        # Basic parsing logic - extract sections
        lines = plan_content.split('\n')
        current_section = None
        current_subsection = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect main sections
            if "project overview" in line.lower():
                current_section = "project_overview"
                current_subsection = None
            elif "file structure" in line.lower():
                current_section = "file_structure"
                current_subsection = None
            elif "component specifications" in line.lower():
                current_section = "component_specifications"
                current_subsection = None
            elif "page structure" in line.lower():
                current_section = "page_structure"
                current_subsection = None
            elif "styling template" in line.lower():
                current_section = "styling_template"
                current_subsection = None
            elif "technical requirements" in line.lower():
                current_section = "technical_requirements"
                current_subsection = None
            elif "content requirements" in line.lower():
                current_section = "content_requirements"
                current_subsection = None
            elif "implementation priorities" in line.lower():
                current_section = "implementation_priorities"
                current_subsection = None
            else:
                # Add content to current section
                if current_section:
                    if isinstance(structured_plan[current_section], dict):
                        # Handle nested structure
                        if current_subsection and current_subsection in structured_plan[current_section]:
                            if isinstance(structured_plan[current_section][current_subsection], list):
                                structured_plan[current_section][current_subsection].append(line)
                            elif isinstance(structured_plan[current_section][current_subsection], str):
                                structured_plan[current_section][current_subsection] += "\n" + line
                        else:
                            # Try to detect subsections
                            if ":" in line and not line.startswith("-"):
                                parts = line.split(":", 1)
                                if len(parts) == 2:
                                    subsection = parts[0].strip().lower().replace(" ", "_")
                                    content = parts[1].strip()
                                    if subsection not in structured_plan[current_section]:
                                        structured_plan[current_section][subsection] = content
                                    current_subsection = subsection
                            else:
                                # Add to general content
                                if "description" not in structured_plan[current_section]:
                                    structured_plan[current_section]["description"] = ""
                                structured_plan[current_section]["description"] += "\n" + line
        
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
    required_sections = ["project_overview", "file_structure", "component_specifications"]
    for section in required_sections:
        if not plan.get(section):
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Missing required section: {section}")
    
    # Add more validation logic as needed
    
    return validation_result