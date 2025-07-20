"""
Coder Agent

This agent is responsible for writing and generating code based on the requirements
and specifications provided by other agents in the system.
"""

from typing import Dict, Any, List
import logging
from services.llm import generate_agent_response

# Configure logging
logger = logging.getLogger(__name__)

# LLM service is imported and used via generate_agent_response function

def coder_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Coder node that generates code based on requirements and specifications.
    
    Args:
        state: The current state containing requirements, specifications, and context
        
    Returns:
        Updated state with generated code
    """
    try:
        # Extract relevant information from state
        requirements = state.get("requirements", "")
        specifications = state.get("specifications", "")
        context = state.get("context", "")
        file_structure = state.get("file_structure", {})
        config = state.get("config", {})
        output_format = config.get("output_format", "python")
        
        # Build the prompt for code generation
        if output_format == "tsx":
            prompt = f"""
            You are an expert Next.js and React developer. Generate high-quality, modern, production-ready Next.js TSX code based on the following requirements:
            
            Requirements: {requirements}
            Specifications: {specifications}
            Context: {context}
            File Structure: {file_structure}
            
            CRITICAL REQUIREMENTS FOR ERROR-FREE CODE (HIGHEST PRIORITY):
            1. All imports must be valid and exist in Next.js/React ecosystem
            2. All TypeScript types must be properly defined
            3. All components must have proper return statements
            4. All JSX must be properly closed and valid
            5. All hooks must follow React rules (only at top level)
            6. All async functions must be properly handled
            7. All event handlers must be properly typed
            8. All CSS classes must be valid Tailwind classes
            9. All file paths must be correct for Next.js App Router
            10. All exports must be properly defined
            11. All class components must have "use client" directive
            12. All import paths must use relative paths (./components/) not @/ alias
            13. All components must be properly typed with React.FC or explicit types
            14. All error boundaries must be client components
            15. All server components must not use client-side features
            16. ONLY use built-in React/Next.js features - NO external libraries like framer-motion
            17. Use CSS transitions and Tailwind classes for animations instead of external libraries
            18. All dependencies must be standard Next.js/React packages only
            19. ERROR-FREE CODE IS MORE IMPORTANT THAN ADDITIONAL FEATURES
            20. If in doubt, generate fewer files with perfect code rather than many files with errors
            
            CRITICAL NEXT.JS ERROR PREVENTION RULES:
            21. layout.tsx: NEVER use "use client" - must be server component with metadata export
            22. page.tsx: Server component by default, "use client" only if interactivity needed
            23. metadata: Only export from server components (layout.tsx), never from client components
            24. "use client": Only use when absolutely necessary for browser APIs or interactivity
            25. Server components: Default choice for static content, SEO, and performance
            26. Client components: Only for interactive elements, event handlers, or browser APIs
            27. No mixing: Don't mix server and client component patterns in the same file
            28. Import paths: Always use relative paths (./components/), never @/ aliases
            29. Default exports: Every component must have proper default export
            30. TypeScript types: All components must be properly typed
            
            REQUIRED FILES (must be generated):
            1. page.tsx - Main page with rich, modern content (must be default export)
            2. layout.tsx - Root layout component with metadata (must be default export)
            3. globals.css - Global styles with Tailwind imports (must be valid CSS)
            
            OPTIONAL COMPONENTS (generate if time permits, prioritize error-free code):
            4. components/Header.tsx - Modern navigation with animations
            5. components/Hero.tsx - Stunning hero section with gradients and animations
            6. components/Features.tsx - Feature cards with hover effects and modern design
            7. components/Testimonials.tsx - Testimonial section with modern styling
            8. components/Pricing.tsx - Pricing cards with gradients and shadows
            9. components/Contact.tsx - Contact form with modern styling
            10. components/Footer.tsx - Comprehensive footer with links
            
            PRIORITY: Error-free code is MORE IMPORTANT than additional components.
            If you can't generate all components without errors, focus on the required files first.
            
            The website should be RICH, MODERN, and BEAUTIFUL with:
            - Stunning visual design with gradients, shadows, and depth
            - Multiple interactive sections (hero, features, testimonials, pricing, contact)
            - Advanced Tailwind CSS: gradients, shadows, hover effects, transitions
            - Modern color schemes (blues, purples, gradients)
            - Professional typography and spacing
            - Micro-interactions and hover effects
            - Responsive design that looks great on all devices
            - Interactive elements and smooth animations
            - Rich content that feels premium and polished
            - NOT minimal - make it look expensive and professional
            
            CONTENT EXAMPLES TO FOLLOW:
            - Company name: "TechFlow Solutions" or "InnovateHub" or "DataSync Pro"
            - Hero: "Transform Your Business with AI-Powered Analytics" with specific benefits
            - Features: "Real-time Data Processing", "Advanced Machine Learning", "Enterprise Security"
            - Testimonials: "Sarah Johnson, CTO at TechCorp" with specific results
            - Pricing: "Starter: $29/month - 5GB storage, 100 API calls"
            - Contact: Real email, phone, address with specific details
            
            CODE QUALITY REQUIREMENTS:
            1. Uses Next.js 14+ App Router structure
            2. Follows React 18+ best practices
            3. Uses TypeScript with strict typing
            4. Includes Tailwind CSS for styling
            5. Is responsive and accessible
            6. Follows modern React patterns (hooks, functional components)
            7. All components are properly typed with React.FC or explicit types
            8. All imports use relative paths (./components/) not @/ alias
            9. All async operations are properly handled
            10. All error boundaries are client components with "use client"
            11. All class components must start with "use client"
            12. All server components avoid client-side features
            13. All import paths are correct for App Router structure
            14. All components have proper default exports
            15. All JSX is properly structured and closed
            16. Use only built-in React features and Tailwind CSS
            17. NO external animation libraries - use CSS transitions instead
            18. All animations use Tailwind transition classes
            19. Keep dependencies minimal and standard
            20. Create RICH, MODERN, BEAUTIFUL designs with gradients, shadows, and visual appeal
            21. Use advanced Tailwind features: gradients, shadows, hover effects, animations
            22. Include multiple sections: hero, features, testimonials, pricing, contact
            23. Use modern color schemes and typography
            24. Add interactive elements and micro-interactions
            25. Make it look professional and polished, not minimal
            
            DESIGN REQUIREMENTS (SECONDARY PRIORITY - after error-free code):
            - Make the website look EXPENSIVE and PROFESSIONAL
            - Use rich gradients: bg-gradient-to-r from-blue-600 to-purple-600
            - Add depth with shadows: shadow-2xl, shadow-lg
            - Use modern colors: blue, purple, indigo, emerald
            - Include hover effects: hover:scale-105, hover:shadow-xl
            - Add smooth transitions: transition-all duration-300
            - Use professional typography: font-bold, text-4xl, leading-tight
            - Include multiple sections with rich content
            - Make it look like a premium SaaS or modern business website
            - NOT a simple landing page - make it comprehensive and impressive
            - BUT: Error-free code comes FIRST, beautiful design comes SECOND
            
            FORBIDDEN CONTENT (NEVER USE):
            - "Feature 1", "Feature 2", "Feature 3"
            - "Company", "Business", "Organization"
            - "Lorem ipsum" or placeholder text
            - Generic descriptions without specific details
            - "Sample" or "Example" content
            - Basic placeholder images or icons
            - Vague benefits like "improve efficiency"
            
            CRITICAL CONTENT REQUIREMENTS:
            - Generate RICH, DETAILED content - NOT generic placeholders
            - Use specific, realistic business names and descriptions
            - Include detailed feature descriptions with real benefits
            - Add testimonials with realistic names and companies
            - Include pricing with actual features and benefits
            - Use specific industry examples and use cases
            - Add detailed contact information and company details
            - Make it look like a REAL, PROFESSIONAL business website
            - NO generic text like "Feature 1", "Company", "Lorem ipsum"
            - Include realistic statistics, numbers, and achievements
            - Add specific product/service descriptions
            - Use real industry terminology and professional language
            
            IMPORTANT: Return ONLY the pure code without any markdown formatting, explanations, or comments about the code. 
            Do not include ```tsx or ```typescript blocks. 
            Do not include any text before or after the code.
            Just return the clean, executable code.
            
            Format multiple files by prefixing each with "// filename.tsx" on a separate line.
            """
        else:
            prompt = f"""
            You are an expert software developer. Generate high-quality, production-ready {output_format.upper()} code based on the following requirements:
            
            Requirements: {requirements}
            Specifications: {specifications}
            Context: {context}
            File Structure: {file_structure}
            Output Format: {output_format.upper()}
            
            Please generate {output_format.upper()} code that:
            1. Follows {output_format.upper()} best practices and design patterns
            2. Is well-documented and readable
            3. Includes proper error handling
            4. Is modular and maintainable
            5. Follows the specified file structure and naming conventions
            6. Uses appropriate {output_format.upper()} syntax and conventions
            
            IMPORTANT: Return ONLY the pure code without any markdown formatting, explanations, or comments about the code. 
            Do not include ```typescript or ```python blocks. 
            Do not include any text before or after the code.
            Just return the clean, executable code.
            """
        
        # Log the prompt being sent
        logger.info("💻 Coder Prompt:")
        logger.info("-" * 30)
        logger.info(prompt)
        logger.info("-" * 30)
        
        # Generate code using centralized LLM service
        generated_code = generate_agent_response("coder", prompt)
        
        # Log the generated code
        logger.info("💻 Coder Raw Output:")
        logger.info("-" * 50)
        logger.info(generated_code)
        logger.info("-" * 50)
        
        # Log code statistics
        lines = generated_code.split('\n')
        logger.info("💻 Coder Code Statistics:")
        logger.info(f"  Total Lines: {len(lines)}")
        logger.info(f"  Code Lines: {len([l for l in lines if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')])}")
        logger.info(f"  Comment Lines: {len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')])}")
        logger.info(f"  Empty Lines: {len([l for l in lines if not l.strip()])}")
        
        # Update state with generated code
        updated_state = state.copy()
        updated_state["generated_code"] = generated_code
        updated_state["code_generation_status"] = "completed"
        
        logger.info("✅ Code generation completed successfully")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in coder node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["code_generation_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def validate_code(code: str) -> Dict[str, Any]:
    """
    Validate generated code for syntax errors and basic issues.
    
    Args:
        code: The code to validate
        
    Returns:
        Dictionary containing validation results
    """
    # Basic validation logic
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Add validation logic here (e.g., syntax checking, linting)
    
    return validation_result

def format_code(code: str, language: str = "python") -> str:
    """
    Format code according to language-specific conventions.
    
    Args:
        code: The code to format
        language: The programming language
        
    Returns:
        Formatted code
    """
    # Add code formatting logic here
    return code