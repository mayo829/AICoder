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
    Coder node that generates code based on the planner's template and specifications.
    
    Args:
        state: The current state containing the planner's template and specifications
        
    Returns:
        Updated state with generated code
    """
    try:
        # Extract relevant information from state
        plan = state.get("plan", {})
        user_input = state.get("user_input", "")
        requirements = state.get("requirements", "")
        context = state.get("context", "")
        config = state.get("config", {})
        output_format = config.get("output_format", "tsx")
        
        # Extract specific sections from the planner's template
        project_overview = plan.get("project_overview", {})
        file_structure = plan.get("file_structure", {})
        component_specs = plan.get("component_specifications", {})
        page_structure = plan.get("page_structure", {})
        styling_template = plan.get("styling_template", {})
        technical_reqs = plan.get("technical_requirements", {})
        content_reqs = plan.get("content_requirements", {})
        implementation_priorities = plan.get("implementation_priorities", {})
        
        # Build the comprehensive prompt for code generation
        prompt = f"""
        You are an expert Next.js and React developer. Generate high-quality, modern, production-ready Next.js TSX code based on the following detailed template and specifications:
        
        USER INPUT: {user_input}
        REQUIREMENTS: {requirements}
        CONTEXT: {context}
        
        PLANNER'S TEMPLATE:
        
        PROJECT OVERVIEW:
        {project_overview}
        
        FILE STRUCTURE:
        {file_structure}
        
        COMPONENT SPECIFICATIONS:
        {component_specs}
        
        PAGE STRUCTURE:
        {page_structure}
        
        STYLING TEMPLATE:
        {styling_template}
        
        TECHNICAL REQUIREMENTS:
        {technical_reqs}
        
        CONTENT REQUIREMENTS:
        {content_reqs}
        
        IMPLEMENTATION PRIORITIES:
        {implementation_priorities}
        
        CRITICAL REQUIREMENTS FOR ERROR-FREE CODE (HIGHEST PRIORITY):
        1. Follow the planner's template EXACTLY - implement what was specified and MAKE SURE to THINK BEFORE YOU CODE.
        2. All imports must be valid and exist in Next.js/React ecosystem
        3. All TypeScript types must be properly defined based on component specifications
        4. All components must have proper return statements and JSX structure
        5. All JSX must be properly closed and valid
        6. All hooks must follow React rules (only at top level)
        7. All async functions must be properly handled
        8. All event handlers must be properly typed
        9. All CSS classes must be valid Tailwind classes as specified in styling template
        10. All file paths must be correct for Next.js App Router
        11. All exports must be properly defined
        12. All client components must have "use client" directive
        13. All import paths must use relative paths (./components/) not @/ alias
        14. All components must be properly typed with React.FC or explicit types
        15. All error boundaries must be client components
        16. All server components must not use client-side features
        17. ONLY use built-in React/Next.js features - NO external libraries
        18. Use CSS transitions and Tailwind classes for animations as specified
        19. All dependencies must be standard Next.js/React packages only
        20. ERROR-FREE CODE IS MORE IMPORTANT THAN ADDITIONAL FEATURES
        
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
        30. TypeScript types: All components must be properly typed based on specifications
        
        CRITICAL TYPESCRIPT SYNTAX RULES (PREVENT SYNTAX ERRORS):
        31. Function parameters: Use proper TypeScript syntax - function Component({{ prop }}: {{ prop: string }}) {{}}
        32. NEVER use invalid syntax like function Component(: any) or function Component({{ prop }}: {{ prop: string }}: any)
        33. Component props: Always define proper interfaces or inline types
        34. Default exports: export default function ComponentName() {{}} or export default function ComponentName({{ prop }}: Props) {{}}
        35. Import statements: import Component from './Component' or import {{ Component }} from './Component'
        36. JSX syntax: All tags must be properly closed, no semicolons inside JSX
        37. TypeScript interfaces: interface Props {{ prop: string }} or type Props = {{ prop: string }}
        38. React.FC usage: const Component: React.FC<Props> = ({{ prop }}) => {{}} or function Component({{ prop }}: Props) {{}}
        39. Metadata exports: export const metadata = {{ title: 'string', description: 'string' }}
        40. No trailing semicolons in JSX attributes or component definitions
        
        SYNTAX VALIDATION CHECKLIST:
        - Function parameters: function Component({{ prop }}: Props) {{}} ✅
        - NOT: function Component(: any) {{}} ❌
        - NOT: function Component({{ prop }}: Props: any) {{}} ❌
        - JSX attributes: <div className="class" /> ✅
        - NOT: <div className="class"; /> ❌
        - Import statements: import Component from './Component' ✅
        - NOT: import Component; from './Component' ❌
        - Export statements: export default function Component() {{}} ✅
        - NOT: export default function Component;() {{}} ❌
        - TypeScript types: {{ children: React.ReactNode }} ✅
        - NOT: {{ children: React.ReactNode; }}: any ❌
        
        IMPLEMENTATION STRATEGY:
        - Start with REQUIRED files (page.tsx, layout.tsx, globals.css) as specified in priorities
        - Implement components based on the component specifications provided
        - Use the styling template for colors, typography, and design system
        - Follow the page structure template for layout and sections
        - Use content requirements for text, images, and interactive elements
        - Apply technical requirements for Next.js version, TypeScript config, etc.
        - Prioritize error-free code over additional features as specified
        
        COMPONENT IMPLEMENTATION RULES:
        - Each component should match its specification exactly
        - Props and TypeScript interfaces should be as specified
        - Styling should follow the styling template
        - Server vs client component choice should be as specified
        - Content should match the content requirements
        - Layout should follow the page structure template
        
        DESIGN IMPLEMENTATION:
        - Use the color scheme from styling template
        - Apply typography requirements from styling template
        - Implement animations and transitions as specified
        - Use responsive breakpoints from styling template
        - Create rich, modern, professional design as specified
        - Make it look expensive and comprehensive, not minimal
        
        CONTENT IMPLEMENTATION:
        - Use text content from content requirements
        - Implement image requirements and placeholders
        - Add call-to-action elements as specified
        - Follow navigation structure from content requirements
        - Create realistic, professional content (no "Feature 1", "Lorem ipsum")
        - Use specific business names, descriptions, and details
        
        PRIORITY ORDER:
        1. REQUIRED FILES (must be generated first):
           - page.tsx: Main page with rich content as specified
           - layout.tsx: Root layout with metadata as specified
           - globals.css: Global styles with Tailwind imports
        
        2. OPTIONAL COMPONENTS (generate if time permits and no errors):
           - components/Header.tsx: Navigation as specified
           - components/Hero.tsx: Hero section as specified
           - components/Features.tsx: Feature cards as specified
           - components/Testimonials.tsx: Testimonial section as specified
           - components/Pricing.tsx: Pricing cards as specified
           - components/Contact.tsx: Contact form as specified
           - components/Footer.tsx: Footer as specified
        
        ERROR PREVENTION:
        - If you can't implement all components without errors, focus on required files
        - Ensure all imports are valid and exist
        - Verify all TypeScript types are correct
        - Check all JSX is properly structured
        - Validate all Tailwind classes are correct
        - Confirm all file paths are accurate
        - Test all exports are properly defined
        - DOUBLE-CHECK all function parameter syntax
        - VERIFY no semicolons in JSX attributes
        - ENSURE proper TypeScript interface definitions
        
        IMPORTANT: Return ONLY the pure code without any markdown formatting, explanations, or comments about the code. 
        Do not include ```tsx or ```typescript blocks. 
        Do not include any text before or after the code.
        Just return the clean, executable code.
        
        Format multiple files by prefixing each with "// filename.tsx" on a separate line.
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
        
        # Apply automatic syntax fixes
        fixed_code = auto_fix_generated_code(generated_code)
        
        # Log code statistics
        lines = fixed_code.split('\n')
        logger.info("💻 Coder Code Statistics:")
        logger.info(f"  Total Lines: {len(lines)}")
        logger.info(f"  Code Lines: {len([l for l in lines if l.strip() and not l.strip().startswith('#') and not l.strip().startswith('//')])}")
        logger.info(f"  Comment Lines: {len([l for l in lines if l.strip().startswith('#') or l.strip().startswith('//')])}")
        logger.info(f"  Empty Lines: {len([l for l in lines if not l.strip()])}")
        
        # Parse the generated code into individual files
        parsed_files = parse_generated_code(fixed_code)
        
        # Validate the generated files for syntax errors
        validation_results = validate_generated_files(parsed_files)
        
        # Log validation results
        logger.info("🔍 Code Validation Results:")
        logger.info(f"  Overall Valid: {validation_results['overall_valid']}")
        logger.info(f"  Total Errors: {validation_results['total_errors']}")
        logger.info(f"  Total Warnings: {validation_results['total_warnings']}")
        
        if not validation_results['overall_valid']:
            logger.error("❌ Syntax errors found in generated code:")
            for filename, file_validation in validation_results['file_validations'].items():
                if not file_validation['is_valid']:
                    logger.error(f"  {filename}:")
                    for error in file_validation['errors']:
                        logger.error(f"    - {error}")
        
        if validation_results['total_warnings'] > 0:
            logger.warning("⚠️ Warnings found in generated code:")
            for filename, file_validation in validation_results['file_validations'].items():
                if file_validation['warnings']:
                    logger.warning(f"  {filename}:")
                    for warning in file_validation['warnings']:
                        logger.warning(f"    - {warning}")
        
        # Update state with generated code
        updated_state = state.copy()
        updated_state["generated_code"] = fixed_code
        updated_state["parsed_files"] = parsed_files
        updated_state["validation_results"] = validation_results
        updated_state["code_generation_status"] = "completed"
        
        logger.info("✅ Code generation completed successfully")
        logger.info(f"📁 Generated {len(parsed_files)} files")
        for filename, content in parsed_files.items():
            logger.info(f"  - {filename}: {len(content.split())} words")
        
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in coder node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["code_generation_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def parse_generated_code(generated_code: str) -> Dict[str, str]:
    """
    Parse the generated code into individual files based on filename comments.
    
    Args:
        generated_code: The raw generated code with filename comments
        
    Returns:
        Dictionary mapping filenames to their content
    """
    files = {}
    current_file = None
    current_content = []
    
    lines = generated_code.split('\n')
    
    for line in lines:
        # Check if this is a filename comment
        if line.strip().startswith('// ') and (line.strip().endswith('.tsx') or line.strip().endswith('.css')):
            # Save previous file if exists
            if current_file and current_content:
                files[current_file] = '\n'.join(current_content).strip()
            
            # Start new file
            current_file = line.strip()[3:]  # Remove "// " prefix
            current_content = []
        else:
            # Add line to current file
            if current_file:
                current_content.append(line)
    
    # Save the last file
    if current_file and current_content:
        files[current_file] = '\n'.join(current_content).strip()
    
    return files

def validate_code(code: str) -> Dict[str, Any]:
    """
    Validate generated code for syntax errors and basic issues.
    
    Args:
        code: The code to validate
        
    Returns:
        Dictionary containing validation results
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check for common TypeScript syntax errors
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # Check for invalid function parameter syntax
        if 'function' in line and '(: any)' in line:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Line {i}: Invalid function parameter syntax - use function Component({{ prop }}: Props) instead of function Component(: any)")
        
        # Check for double type annotations
        if '}: {' in line and '}: any' in line:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Line {i}: Double type annotation - remove ': any' after proper type definition")
        
        # Check for semicolons in JSX attributes
        if ';' in line and ('<' in line and '>' in line):
            if not line.strip().startswith('//') and not line.strip().startswith('import') and not line.strip().startswith('export'):
                validation_result["warnings"].append(f"Line {i}: Possible semicolon in JSX - check for invalid syntax")
        
        # Check for invalid import syntax
        if line.startswith('import') and ';' in line and not line.strip().endswith(';'):
            validation_result["errors"].append(f"Line {i}: Invalid import syntax - check for misplaced semicolons")
        
        # Check for invalid export syntax
        if line.startswith('export') and 'function' in line and ';' in line:
            validation_result["errors"].append(f"Line {i}: Invalid export syntax - check for misplaced semicolons")
    
    return validation_result

def validate_generated_files(parsed_files: Dict[str, str]) -> Dict[str, Any]:
    """
    Validate all generated files for syntax errors.
    
    Args:
        parsed_files: Dictionary of filename to content mapping
        
    Returns:
        Dictionary containing validation results for all files
    """
    all_validation = {
        "overall_valid": True,
        "file_validations": {},
        "total_errors": 0,
        "total_warnings": 0
    }
    
    for filename, content in parsed_files.items():
        file_validation = validate_code(content)
        all_validation["file_validations"][filename] = file_validation
        
        if not file_validation["is_valid"]:
            all_validation["overall_valid"] = False
            all_validation["total_errors"] += len(file_validation["errors"])
        
        all_validation["total_warnings"] += len(file_validation["warnings"])
    
    return all_validation

def format_code(code: str, language: str = "typescript") -> str:
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

def fix_typescript_syntax_errors(code: str) -> str:
    """
    Automatically fix common TypeScript syntax errors in generated code.
    
    Args:
        code: The code with potential syntax errors
        
    Returns:
        Fixed code with corrected syntax
    """
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        fixed_line = line
        
        # Fix function parameter syntax errors
        # function Component(: any) -> function Component()
        if 'function' in fixed_line and '(: any)' in fixed_line:
            fixed_line = fixed_line.replace('(: any)', '()')
        
        # Fix double type annotations
        # }: { children: React.ReactNode; }: any) -> }: { children: React.ReactNode; })
        if '}: {' in fixed_line and '}: any)' in fixed_line:
            fixed_line = fixed_line.replace('}: any)', ')')
        
        # Fix semicolons in JSX attributes
        # <Image; src="..." /> -> <Image src="..." />
        if '<' in fixed_line and '>' in fixed_line and ';' in fixed_line:
            # Only fix if it's not a comment or import/export
            if not fixed_line.strip().startswith('//') and not fixed_line.strip().startswith('import') and not fixed_line.strip().startswith('export'):
                # Replace semicolons in JSX attributes
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix invalid import syntax
        # import Component; from './Component' -> import Component from './Component'
        if fixed_line.strip().startswith('import') and ';' in fixed_line and not fixed_line.strip().endswith(';'):
            fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix invalid export syntax
        # export default function Component;() {} -> export default function Component() {}
        if fixed_line.strip().startswith('export') and 'function' in fixed_line and ';' in fixed_line:
            fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix missing function parameters
        # export default function Home(: any) -> export default function Home()
        if 'export default function' in fixed_line and '(: any)' in fixed_line:
            fixed_line = fixed_line.replace('(: any)', '()')
        
        # Fix invalid React.FC syntax
        # const Component: React.FC<Props> = ({ prop }) => {} -> const Component: React.FC<Props> = ({ prop }) => {}
        # (already correct, but ensure no semicolons)
        if 'React.FC' in fixed_line and ';' in fixed_line:
            fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

def fix_jsx_syntax_errors(code: str) -> str:
    """
    Fix common JSX syntax errors.
    
    Args:
        code: The code with potential JSX errors
        
    Returns:
        Fixed code with corrected JSX syntax
    """
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        fixed_line = line
        
        # Fix self-closing tags with semicolons
        # <Image; src="..." /> -> <Image src="..." />
        if '<' in fixed_line and '/>' in fixed_line and ';' in fixed_line:
            if not fixed_line.strip().startswith('//'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix JSX attributes with semicolons
        # className="class"; -> className="class"
        if 'className=' in fixed_line and ';' in fixed_line:
            if not fixed_line.strip().startswith('//'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix src attributes with semicolons
        # src="image.jpg"; -> src="image.jpg"
        if 'src=' in fixed_line and ';' in fixed_line:
            if not fixed_line.strip().startswith('//'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix alt attributes with semicolons
        # alt="description"; -> alt="description"
        if 'alt=' in fixed_line and ';' in fixed_line:
            if not fixed_line.strip().startswith('//'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

def fix_import_export_syntax(code: str) -> str:
    """
    Fix common import and export syntax errors.
    
    Args:
        code: The code with potential import/export errors
        
    Returns:
        Fixed code with corrected import/export syntax
    """
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        fixed_line = line
        
        # Fix import statements with misplaced semicolons
        # import { Component }; from './Component' -> import { Component } from './Component'
        if fixed_line.strip().startswith('import') and ';' in fixed_line:
            # Remove semicolons that are not at the end
            if not fixed_line.strip().endswith(';'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        # Fix export statements with misplaced semicolons
        # export default function Component;() {} -> export default function Component() {}
        if fixed_line.strip().startswith('export') and ';' in fixed_line:
            if not fixed_line.strip().endswith(';'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

def auto_fix_generated_code(code: str) -> str:
    """
    Apply all automatic fixes to generated code.
    
    Args:
        code: The raw generated code
        
    Returns:
        Fixed code with all common syntax errors corrected
    """
    logger.info("🔧 Applying automatic code fixes...")
    
    # Apply fixes in order
    fixed_code = code
    fixed_code = fix_typescript_syntax_errors(fixed_code)
    fixed_code = fix_jsx_syntax_errors(fixed_code)
    fixed_code = fix_import_export_syntax(fixed_code)
    
    # Log if any changes were made
    if fixed_code != code:
        logger.info("✅ Code fixes applied")
        # Log the specific fixes made
        original_lines = code.split('\n')
        fixed_lines = fixed_code.split('\n')
        
        for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines)):
            if orig != fixed:
                logger.info(f"  Line {i+1}: Fixed syntax error")
                logger.info(f"    Before: {orig.strip()}")
                logger.info(f"    After:  {fixed.strip()}")
    else:
        logger.info("✅ No syntax errors found - code is clean")
    
    return fixed_code