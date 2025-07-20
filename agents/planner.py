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
        if output_format == "tsx":
            prompt = f"""
            You are an expert Next.js and React architect. Create a comprehensive plan for the following Next.js TSX project:
            
            User Input: {user_input}
            Requirements: {requirements}
            Context: {context}
            Existing Codebase: {existing_codebase}
            
            Please provide:
            1. Project Architecture Overview (Next.js App Router structure)
            2. File Structure and Organization (app/ directory, components, etc.)
            3. Technology Stack Recommendations (Next.js 14+, React 18+, TypeScript, Tailwind CSS)
            4. Implementation Steps (detailed breakdown of components and pages)
            5. Dependencies and Requirements (Next.js ecosystem)
            6. Component Architecture (reusable components, layouts, etc.)
            7. Styling Strategy (Tailwind CSS, responsive design with rich gradients and modern design)
            8. Deployment Considerations (Vercel, Netlify, etc.)
            9. Design Requirements (rich, modern, professional website with multiple sections)
            10. Content Strategy (hero, features, testimonials, pricing, contact sections)
            
            CRITICAL DEPENDENCY-FREE REQUIREMENTS:
            - Use ONLY built-in React/Next.js features - NO external libraries
            - NO framer-motion, react-spring, or other animation libraries
            - Use Tailwind CSS transitions and animations instead
            - All components must be self-contained with no external dependencies
            - Focus on error-free code generation over additional features
            - Prioritize required files (page.tsx, layout.tsx, globals.css) over optional components
            - Ensure all imports use relative paths, not @/ aliases
            - All components must have proper TypeScript types and exports
            
            CRITICAL NEXT.JS ERROR PREVENTION RULES:
            - layout.tsx: NEVER use "use client" - it must be a server component with metadata export
            - page.tsx: Can use "use client" if needed for interactivity, but prefer server components
            - metadata: Only export from server components (layout.tsx), never from client components
            - "use client": Only use when absolutely necessary for browser APIs or interactivity
            - Server components: Default choice for static content, SEO, and performance
            - Client components: Only for interactive elements, event handlers, or browser APIs
            - Import paths: Always use relative paths (./components/), never @/ aliases
            - Default exports: Every component must have proper default export
            - TypeScript types: All components must be properly typed
            - No mixing: Don't mix server and client component patterns in the same file
            
            IMPORTANT: Plan for a RICH, MODERN, PROFESSIONAL website that looks expensive and comprehensive, not minimal.
            Include multiple sections and rich content that would impress users.
            BUT: Error-free code and dependency-free implementation is MORE IMPORTANT than additional features.
            
            ERROR-FREE FILE GENERATION STRATEGY:
            - REQUIRED FILES (must be generated first):
              * page.tsx: Main page with rich content, proper exports, no missing imports
              * layout.tsx: Root layout with metadata, proper TypeScript types
              * globals.css: Tailwind imports and custom styles
            
            - OPTIONAL COMPONENTS (generate only if time permits and no errors):
              * components/Header.tsx: Navigation with Tailwind animations
              * components/Hero.tsx: Hero section with gradients and CSS transitions
              * components/Features.tsx: Feature cards with hover effects
              * components/Testimonials.tsx: Testimonial section with modern styling
              * components/Pricing.tsx: Pricing cards with shadows and gradients
              * components/Contact.tsx: Contact form with validation
              * components/Footer.tsx: Footer with links and styling
            
            - DEPENDENCY MANAGEMENT:
              * Zero external dependencies beyond Next.js/React/Tailwind
              * All animations use CSS transitions and Tailwind classes
              * All imports use relative paths (./components/)
              * All components have proper default exports
              * All TypeScript types are properly defined
            
            - NEXT.JS COMPONENT RULES:
              * layout.tsx: Server component with metadata export, NO "use client"
              * page.tsx: Server component by default, "use client" only if needed
              * Component files: "use client" only for interactive components
              * Metadata: Only in layout.tsx, never in client components
              * Server vs Client: Choose based on functionality needs
            
            Format your response as a structured plan that can be easily parsed and followed by other agents.
            """
        else:
            prompt = f"""
            You are an expert software architect and project planner. Create a comprehensive plan for the following {output_format.upper()} project:
            
            User Input: {user_input}
            Requirements: {requirements}
            Context: {context}
            Existing Codebase: {existing_codebase}
            Output Format: {output_format.upper()}
            
            Please provide:
            1. Project Architecture Overview
            2. File Structure and Organization (appropriate for {output_format.upper()})
            3. Technology Stack Recommendations (for {output_format.upper()} development)
            4. Implementation Steps (detailed breakdown)
            5. Dependencies and Requirements (for {output_format.upper()} ecosystem)
            6. Testing Strategy
            7. Deployment Considerations
            
            Format your response as a structured plan that can be easily parsed and followed by other agents.
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
            "deployment_notes": "",
            "required_files": [],
            "optional_components": [],
            "dependency_management": []
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
            elif "required files" in line.lower():
                current_section = "required_files"
            elif "optional components" in line.lower():
                current_section = "optional_components"
            elif "dependency management" in line.lower():
                current_section = "dependency_management"
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