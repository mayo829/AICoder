import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, using system environment variables")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aicoder.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AICoderWorkflow:
    """
    Main workflow orchestrator for the AICoder system.
    Handles the complete process from user input to generated files.
    """
    
    def __init__(self, output_dir: str = None):
        # For TSX projects, save to my-new-website/src/app
        output_format = self.load_config().get("output_format", "python")
        if output_format == "tsx":
            self.output_dir = Path("my-new-website/src/app")
            # Ensure the directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 TSX output directory: {self.output_dir.absolute()}")
        else:
            self.output_dir = Path(output_dir or "generated_code")
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize workflow components
        self.workflow = None
        self.state = {}
        self.generated_files = {}
        
        # Load configuration
        self.config = self.load_config()
        
        logger.info("AICoderWorkflow initialized")
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config file or use defaults."""
        config_file = Path("config.json")
        
        default_config = {
            "workflow_type": "simple",  # "simple" or "conditional"
            "agents": ["planner", "coder", "tester"],
            "output_format": "python",  # python, javascript, etc.
            "file_consistency_check": True,
            "error_handling": "strict",  # "strict" or "lenient"
            "max_retries": 3,
            "save_intermediate_results": True
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info("Loaded configuration from config.json")
            except Exception as e:
                logger.warning(f"Failed to load config.json: {e}, using defaults")
        else:
            logger.info("No config.json found, using default configuration")
        
        return default_config
    
    def initialize_workflow(self) -> bool:
        """Initialize the LangGraph workflow."""
        try:
            from graph import create_workflow_from_contracts
            from services.llm import get_llm_service
            
            # Log LLM service information
            llm_service = get_llm_service()
            available_services = llm_service.get_available_services()
            logger.info("🤖 LLM Services Available:")
            for service in available_services:
                logger.info(f"  - {service['name']}: {service.get('model', 'unknown')} ({service.get('status', 'unknown')})")
            
            logger.info("Initializing LangGraph workflow...")
            
            self.workflow = create_workflow_from_contracts(
                workflow_type=self.config["workflow_type"],
                agents=self.config["agents"],
                enable_checkpointing=False  # Disable for now to avoid complexity
            )
            
            if self.workflow:
                logger.info("✅ Workflow initialized successfully")
                return True
            else:
                logger.error("❌ Failed to initialize workflow")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error initializing workflow: {e}")
            return False
    
    def prepare_initial_state(self, user_prompt: str) -> Dict[str, Any]:
        """Prepare the initial state for the workflow."""
        timestamp = datetime.now().isoformat()
        
        initial_state = {
            "user_input": user_prompt,
            "timestamp": timestamp,
            "workflow_step": "initialized",
            "config": self.config,
            "output_directory": str(self.output_dir),
            "generated_files": {},
            "errors": [],
            "warnings": []
        }
        
        logger.info(f"Prepared initial state for prompt: {user_prompt[:50]}...")
        return initial_state
    
    def execute_workflow(self, user_prompt: str) -> Dict[str, Any]:
        """Execute the complete workflow."""
        try:
            # Initialize workflow if not already done
            if not self.workflow:
                if not self.initialize_workflow():
                    raise Exception("Failed to initialize workflow")
            
            # Prepare initial state
            initial_state = self.prepare_initial_state(user_prompt)
            
            logger.info("🚀 Starting workflow execution...")
            
            # Execute the workflow
            logger.info("🔄 Executing workflow...")
            final_state = self.workflow.invoke(initial_state)
            
            # Log workflow execution summary
            logger.info("🔄 Workflow Execution Summary:")
            logger.info(f"  Planner Status: {final_state.get('planning_status', 'unknown')}")
            logger.info(f"  Coder Status: {final_state.get('code_generation_status', 'unknown')}")
            logger.info(f"  Tester Status: {final_state.get('testing_status', 'unknown')}")
            logger.info(f"  Current Agent: {final_state.get('current_agent', 'unknown')}")
            logger.info(f"  Workflow Step: {final_state.get('workflow_step', 'unknown')}")
            
            logger.info("✅ Workflow execution completed")
            
            return final_state
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            return {
                "error": str(e),
                "user_input": user_prompt,
                "workflow_step": "failed"
            }
    
    def extract_generated_code(self, workflow_state: Dict[str, Any]) -> Dict[str, str]:
        """Extract generated code from workflow state."""
        generated_files = {}
        
        # Look for coder results - based on actual coder.py implementation
        coder_result = workflow_state.get("coder_result", "")
        
        if coder_result:
            # The coder returns generated code directly as a string
            # Use appropriate file extension based on output format
            output_format = self.config.get("output_format", "python")
            if output_format == "tsx":
                # For TSX, we need to parse the response and create multiple files
                generated_files.update(self.parse_tsx_response(coder_result))
            elif output_format == "typescript":
                generated_files["index.ts"] = coder_result
            else:
                generated_files["main.py"] = coder_result
        
        # Also check for direct code in state
        if "generated_code" in workflow_state:
            output_format = self.config.get("output_format", "python")
            if output_format == "tsx":
                generated_files.update(self.parse_tsx_response(workflow_state["generated_code"]))
            elif output_format == "typescript":
                generated_files["index.ts"] = workflow_state["generated_code"]
            else:
                generated_files["main.py"] = workflow_state["generated_code"]
        
        # Check for planner results to create additional files
        planner_result = workflow_state.get("plan", {})
        if isinstance(planner_result, dict):
            # Create package.json or requirements.txt if dependencies are specified
            if "dependencies" in planner_result:
                output_format = self.config.get("output_format", "python")
                if output_format == "typescript":
                    package_content = self.create_package_json_from_plan(planner_result)
                    generated_files["package.json"] = package_content
                    
                    # Also create tsconfig.json for TypeScript projects
                    tsconfig_content = self.create_tsconfig_json()
                    generated_files["tsconfig.json"] = tsconfig_content
                else:
                    requirements_content = self.create_requirements_from_plan(planner_result)
                    generated_files["requirements.txt"] = requirements_content
        
        logger.info(f"Extracted {len(generated_files)} generated files")
        return generated_files
    

    
    def create_requirements_from_plan(self, plan: Dict[str, Any]) -> str:
        """Create requirements.txt from planner dependencies."""
        dependencies = plan.get('dependencies', [])
        
        if not dependencies:
            return "# No specific dependencies identified\n"
        
        requirements_content = "# Project Dependencies\n\n"
        
        for dep in dependencies:
            if isinstance(dep, str):
                requirements_content += f"{dep}\n"
            elif isinstance(dep, dict):
                package = dep.get('package', '')
                version = dep.get('version', '')
                if package:
                    requirements_content += f"{package}{'==' + version if version else ''}\n"
        
        return requirements_content
    
    def parse_tsx_response(self, coder_result: str) -> Dict[str, str]:
        """Parse the coder response and create proper Next.js TSX files."""
        files = {}
        
        # Split the response by file markers
        if "// " in coder_result:
            # Parse existing file structure
            parts = coder_result.split("// ")
            for part in parts:
                if part.strip():
                    lines = part.split('\n')
                    if lines[0].strip().endswith(('.tsx', '.css', '.js')):
                        filename = lines[0].strip()
                        content = '\n'.join(lines[1:]).strip()
                        # Fix common issues in the content
                        content = self.fix_tsx_issues(content, filename)
                        files[filename] = content
        else:
            # Create default Next.js structure
            files["page.tsx"] = self.fix_tsx_issues(coder_result, "page.tsx")
            files["layout.tsx"] = self.create_default_layout()
            files["globals.css"] = self.create_default_globals()
        
        # Always ensure we have essential Next.js files (required files)
        if "layout.tsx" not in files:
            files["layout.tsx"] = self.create_default_layout()
            logger.info("📝 Created default layout.tsx (required file)")
        if "globals.css" not in files:
            files["globals.css"] = self.create_default_globals()
            logger.info("📝 Created default globals.css (required file)")
        
        # Log what files were generated
        required_files = ["page.tsx", "layout.tsx", "globals.css"]
        optional_files = [f for f in files.keys() if f not in required_files]
        
        logger.info(f"✅ Generated {len(required_files)} required files: {required_files}")
        if optional_files:
            logger.info(f"🎨 Generated {len(optional_files)} optional components: {optional_files}")
        else:
            logger.info("⚠️  No optional components generated - focusing on error-free required files")
        
        return files
    
    def fix_tsx_issues(self, content: str, filename: str) -> str:
        """Fix common TSX issues in generated code."""
        import re
        
        # Apply aggressive syntax correction first
        content = self.force_syntax_correction(content, filename)
        
        # Apply automatic syntax fixes
        content = self.fix_typescript_syntax_errors(content)
        content = self.fix_jsx_syntax_errors(content)
        content = self.fix_import_export_syntax(content)
        
        # Add "use client" directive for class components
        if 'class ' in content and 'extends Component' in content and '"use client"' not in content:
            content = '"use client"\n\n' + content
        
        # Fix @/ imports to use relative paths
        content = content.replace('@/components/', './components/')
        content = content.replace('@/app/', './')
        content = content.replace('@/', './')
        
        # Ensure proper React imports for hooks
        if ('useState' in content or 'useEffect' in content) and 'import React' not in content and 'import { ' not in content:
            if 'import { ' in content:
                # Add React to existing import
                content = content.replace('import { ', 'import React, { ')
            else:
                # Add new React import
                content = 'import React from \'react\'\n' + content
        
        # Ensure proper default exports
        if 'export default' not in content and 'function ' in content:
            # Find the function name and add export default
            match = re.search(r'function\s+(\w+)', content)
            if match:
                func_name = match.group(1)
                content = content.replace(f'function {func_name}', f'export default function {func_name}')
        
        # Remove external library imports and replace with built-in alternatives
        
        # Replace framer-motion with CSS transitions
        if 'framer-motion' in content:
            content = re.sub(r'import\s+\{[^}]*motion[^}]*\}\s+from\s+[\'"]framer-motion[\'"];?\n?', '', content)
            content = re.sub(r'<motion\.([^>]+)>', r'<div className="transition-all duration-300 ease-in-out \1">', content)
            content = re.sub(r'</motion\.([^>]+)>', r'</div>', content)
            content = re.sub(r'initial=\{[^}]*\}', '', content)
            content = re.sub(r'animate=\{[^}]*\}', '', content)
            content = re.sub(r'transition=\{[^}]*\}', '', content)
        
        # Remove other external animation libraries
        external_libs = ['react-spring', 'react-transition-group', 'lottie-react']
        for lib in external_libs:
            content = re.sub(r'import\s+.*from\s+[\'"]' + lib + r'[\'"];?\n?', '', content)
        
        # CRITICAL: Fix Next.js specific errors
        if filename == 'layout.tsx':
            # layout.tsx must be a server component with metadata export
            if '"use client"' in content:
                # Remove "use client" directive from layout.tsx
                content = re.sub(r'"use client"\s*\n?', '', content)
                logger.info(f"🔧 Removed 'use client' from layout.tsx (must be server component)")
            
            # Ensure metadata export exists
            if 'export const metadata' not in content:
                # Add metadata export if missing
                metadata_export = '''export const metadata = {
  title: 'Generated App',
  description: 'Generated by AICoder',
}'''
                # Insert after imports
                import_end = content.find('\n\n')
                if import_end != -1:
                    content = content[:import_end] + '\n\n' + metadata_export + content[import_end:]
                else:
                    content = metadata_export + '\n\n' + content
                logger.info(f"🔧 Added metadata export to layout.tsx")
        
        elif filename == 'page.tsx':
            # page.tsx should be server component by default, only use "use client" if needed
            if '"use client"' in content:
                # Check if it actually needs client features
                needs_client = any(keyword in content for keyword in ['useState', 'useEffect', 'onClick', 'onChange', 'addEventListener'])
                if not needs_client:
                    # Remove "use client" if not needed
                    content = re.sub(r'"use client"\s*\n?', '', content)
                    logger.info(f"🔧 Removed unnecessary 'use client' from page.tsx")
        
        # Fix metadata exports in client components
        if '"use client"' in content and 'export const metadata' in content:
            # Remove metadata export from client components
            content = re.sub(r'export const metadata\s*=\s*\{[^}]*\};?\n?', '', content)
            logger.info(f"🔧 Removed metadata export from client component {filename}")
        
        return content
    
    def fix_typescript_syntax_errors(self, content: str) -> str:
        """Fix common TypeScript syntax errors."""
        lines = content.split('\n')
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
            
            # Fix missing function parameters
            # export default function Home(: any) -> export default function Home()
            if 'export default function' in fixed_line and '(: any)' in fixed_line:
                fixed_line = fixed_line.replace('(: any)', '()')
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def fix_jsx_syntax_errors(self, content: str) -> str:
        """Fix common JSX syntax errors."""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Fix semicolons in JSX attributes
            # <Image; src="..." /> -> <Image src="..." />
            if '<' in fixed_line and '>' in fixed_line and ';' in fixed_line:
                # Only fix if it's not a comment or import/export
                if not fixed_line.strip().startswith('//') and not fixed_line.strip().startswith('import') and not fixed_line.strip().startswith('export'):
                    # Replace semicolons in JSX attributes
                    fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
            
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
    
    def fix_import_export_syntax(self, content: str) -> str:
        """Fix common import and export syntax errors."""
        lines = content.split('\n')
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
    
    def fix_missing_component_imports(self, generated_files: Dict[str, str]) -> Dict[str, str]:
        """Fix imports of components that don't exist by removing them."""
        import re
        
        # Get list of actually generated component files
        generated_components = []
        for filename in generated_files.keys():
            if filename.startswith('components/') and filename.endswith('.tsx'):
                component_name = filename.replace('components/', '').replace('.tsx', '')
                generated_components.append(component_name)
        
        logger.info(f"🔍 Generated components: {generated_components}")
        
        # Fix page.tsx if it exists
        if 'page.tsx' in generated_files:
            content = generated_files['page.tsx']
            
            # Remove imports for components that weren't generated
            optional_components = ['Header', 'Hero', 'Features', 'Testimonials', 'Pricing', 'Contact', 'Footer']
            for comp in optional_components:
                if comp not in generated_components:
                    # Remove the import line
                    content = re.sub(rf'import\s+{comp}\s+from\s+[\'"]\./components/{comp}[\'"];?\n?', '', content)
                    # Remove the component usage (self-closing)
                    content = re.sub(rf'<{comp}\s*/?>', '', content)
                    # Remove the component usage (with props)
                    content = re.sub(rf'<{comp}\s+[^>]*/>', '', content)
                    # Remove the component usage (with children)
                    content = re.sub(rf'<{comp}\s+[^>]*>.*?</{comp}>', '', content, flags=re.DOTALL)
            
            # Clean up any empty lines left by removed imports
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            content = re.sub(r'^\s*\n', '', content)  # Remove leading empty lines
            
            generated_files['page.tsx'] = content
            logger.info(f"🔧 Fixed page.tsx imports - removed references to missing components")
        
        return generated_files
    
    def compile_and_check_website(self, project_dir: str) -> Dict[str, Any]:
        """Compile the Next.js website and check for errors."""
        import subprocess
        import os
        
        compilation_result = {
            "success": False,
            "errors": [],
            "warnings": [],
            "build_output": ""
        }
        
        try:
            # Change to the project directory
            original_dir = os.getcwd()
            os.chdir(project_dir)
            
            logger.info(f"🔨 Compiling website in: {project_dir}")
            
            # Run Next.js build
            result = subprocess.run(
                ['npm', 'run', 'build'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            compilation_result["build_output"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                compilation_result["success"] = True
                logger.info("✅ Website compiled successfully!")
            else:
                # Parse errors from build output
                lines = compilation_result["build_output"].split('\n')
                for line in lines:
                    if 'error' in line.lower() or 'failed' in line.lower():
                        compilation_result["errors"].append(line.strip())
                    elif 'warning' in line.lower():
                        compilation_result["warnings"].append(line.strip())
                
                logger.error(f"❌ Website compilation failed with {len(compilation_result['errors'])} errors")
                for error in compilation_result["errors"][:5]:  # Show first 5 errors
                    logger.error(f"   - {error}")
            
            # Change back to original directory
            os.chdir(original_dir)
            
        except subprocess.TimeoutExpired:
            compilation_result["errors"].append("Build timed out after 2 minutes")
            logger.error("❌ Website compilation timed out")
        except FileNotFoundError:
            compilation_result["errors"].append("npm not found - Node.js not installed")
            logger.error("❌ npm not found - Node.js not installed")
        except Exception as e:
            compilation_result["errors"].append(f"Compilation error: {str(e)}")
            logger.error(f"❌ Website compilation error: {e}")
        
        return compilation_result
    
    def auto_fix_compilation_errors(self, generated_files: Dict[str, str], compilation_errors: List[str]) -> Dict[str, str]:
        """Automatically fix common compilation errors."""
        import re
        
        logger.info("🔧 Attempting to auto-fix compilation errors...")
        
        for error in compilation_errors:
            # Fix "Module not found" errors for components
            if "Module not found" in error and "Can't resolve" in error:
                # Extract component name from error
                match = re.search(r"Can't resolve '\./components/([^']+)'", error)
                if match:
                    component_name = match.group(1)
                    logger.info(f"🔧 Auto-fixing missing component: {component_name}")
                    
                    # Remove the import and usage from page.tsx
                    if 'page.tsx' in generated_files:
                        content = generated_files['page.tsx']
                        
                        # Remove import
                        content = re.sub(rf'import\s+{component_name}\s+from\s+[\'"]\./components/{component_name}[\'"];?\n?', '', content)
                        
                        # Remove usage
                        content = re.sub(rf'<{component_name}\s*/?>', '', content)
                        content = re.sub(rf'<{component_name}\s+[^>]*/>', '', content)
                        content = re.sub(rf'<{component_name}\s+[^>]*>.*?</{component_name}>', '', content, flags=re.DOTALL)
                        
                        # Clean up empty lines
                        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
                        content = re.sub(r'^\s*\n', '', content)
                        
                        generated_files['page.tsx'] = content
                        logger.info(f"✅ Removed references to missing component: {component_name}")
            
            # Fix "export default" errors
            elif "export default" in error.lower():
                logger.info("🔧 Auto-fixing export default issues...")
                for filename, content in generated_files.items():
                    if filename.endswith('.tsx') and 'export default' not in content:
                        # Find function name and add export default
                        match = re.search(r'function\s+(\w+)', content)
                        if match:
                            func_name = match.group(1)
                            content = content.replace(f'function {func_name}', f'export default function {func_name}')
                            generated_files[filename] = content
                            logger.info(f"✅ Added export default to {filename}")
            
            # Fix React import errors
            elif "React" in error and "import" in error.lower():
                logger.info("🔧 Auto-fixing React import issues...")
                for filename, content in generated_files.items():
                    if filename.endswith('.tsx') and 'import React' not in content:
                        content = 'import React from \'react\'\n' + content
                        generated_files[filename] = content
                        logger.info(f"✅ Added React import to {filename}")
        
        return generated_files
    
    def post_process_code_quality(self, generated_files: Dict[str, str]) -> Dict[str, str]:
        """Post-process generated code for quality improvements (ESLint-like without external calls)."""
        import re
        
        logger.info("🔧 Post-processing code for quality improvements...")
        
        for filename, content in generated_files.items():
            if filename.endswith('.tsx'):
                original_content = content
                
                # 1. Fix common ESLint issues
                content = self.fix_eslint_style_issues(content, filename)
                
                # 2. Fix TypeScript issues
                content = self.fix_typescript_issues(content, filename)
                
                # 3. Fix React/Next.js best practices
                content = self.fix_react_best_practices(content, filename)
                
                # 4. Fix accessibility issues
                content = self.fix_accessibility_issues(content, filename)
                
                # 5. Fix performance issues
                content = self.fix_performance_issues(content, filename)
                
                if content != original_content:
                    generated_files[filename] = content
                    logger.info(f"✅ Post-processed {filename} for code quality")
        
        return generated_files
    
    def fix_eslint_style_issues(self, content: str, filename: str) -> str:
        """Fix common ESLint style issues."""
        import re
        
        # Remove trailing whitespace
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Fix inconsistent quotes (prefer single quotes)
        content = re.sub(r'"([^"]*)"', r"'\1'", content)
        
        # Fix missing semicolons
        content = re.sub(r'(\w+)\s*$', r'\1;', content, flags=re.MULTILINE)
        
        # Fix double empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Fix inconsistent indentation (use 2 spaces)
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if line.strip() and line.startswith(' '):
                # Count leading spaces and convert to 2-space indentation
                leading_spaces = len(line) - len(line.lstrip())
                indent_level = leading_spaces // 2
                fixed_lines.append('  ' * indent_level + line.lstrip())
            else:
                fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        return content
    
    def fix_typescript_issues(self, content: str, filename: str) -> str:
        """Fix common TypeScript issues."""
        import re
        
        # Add proper TypeScript types for function parameters
        content = re.sub(
            r'function\s+(\w+)\s*\(\s*([^)]*)\s*\)',
            r'function \1(\2: any)',
            content
        )
        
        # Add proper TypeScript types for arrow functions
        content = re.sub(
            r'const\s+(\w+)\s*=\s*\(\s*([^)]*)\s*\)\s*=>',
            r'const \1 = (\2: any) =>',
            content
        )
        
        # Fix React.FC usage
        if 'React.FC' in content and 'const ' in content:
            content = re.sub(
                r'const\s+(\w+):\s*React\.FC\s*=\s*\(\)\s*=>',
                r'const \1: React.FC = () =>',
                content
            )
        
        return content
    
    def fix_react_best_practices(self, content: str, filename: str) -> str:
        """Fix React/Next.js best practices."""
        import re
        
        # Ensure proper key props for mapped elements
        content = re.sub(
            r'<(\w+)\s+([^>]*)\s*>\s*\{([^}]+)\.map\(',
            r'<\1 \2 key={index}>\{\3.map((',
            content
        )
        
        # Fix missing alt attributes for images
        content = re.sub(
            r'<img\s+([^>]*)\s*/>',
            r'<img \1 alt="" />',
            content
        )
        
        # Ensure proper event handler naming
        content = re.sub(
            r'onClick\s*=\s*\{([^}]+)\}',
            r'onClick={\1}',
            content
        )
        
        # Fix className vs class usage
        content = re.sub(
            r'\bclass\s*=\s*[\'"]([^\'"]*)[\'"]',
            r'className="\1"',
            content
        )
        
        return content
    
    def fix_accessibility_issues(self, content: str, filename: str) -> str:
        """Fix accessibility issues."""
        import re
        
        # Add proper ARIA labels
        if '<button' in content and 'aria-label' not in content:
            content = re.sub(
                r'<button\s+([^>]*)\s*>',
                r'<button \1 aria-label="Button">',
                content
            )
        
        # Add proper heading hierarchy
        if '<h1' in content and '<h2' not in content:
            # Ensure proper heading structure
            pass
        
        # Add proper form labels
        if '<input' in content and 'id=' in content and 'aria-label' not in content:
            content = re.sub(
                r'<input\s+([^>]*id=[\'"]([^\'"]*)[\'"][^>]*)\s*/>',
                r'<input \1 aria-label="\2" />',
                content
            )
        
        return content
    
    def fix_performance_issues(self, content: str, filename: str) -> str:
        """Fix performance issues."""
        import re
        
        # Add proper memoization for expensive components
        if 'useState' in content and 'useMemo' not in content:
            # Consider adding useMemo for expensive calculations
            pass
        
        # Fix unnecessary re-renders
        if 'onClick' in content and 'useCallback' not in content:
            # Consider adding useCallback for event handlers
            pass
        
        # Add proper image optimization
        if '<img' in content and 'next/image' not in content:
            content = re.sub(
                r'<img\s+([^>]*)\s*/>',
                r'<Image \1 />',
                content
            )
            # Add import if not present
            if 'import Image' not in content:
                content = 'import Image from \'next/image\'\n' + content
        
        return content
    
    def create_default_layout(self) -> str:
        """Create a default Next.js layout.tsx file."""
        return '''import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Generated App',
  description: 'Generated by AICoder',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}'''
    
    def create_default_globals(self) -> str:
        """Create a default globals.css file."""
        return '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 0, 0, 0;
  --background-start-rgb: 214, 219, 220;
  --background-end-rgb: 255, 255, 255;
}

@media (prefers-color-scheme: dark) {
  :root {
    --foreground-rgb: 255, 255, 255;
    --background-start-rgb: 0, 0, 0;
    --background-end-rgb: 0, 0, 0;
  }
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}'''
    
    def create_package_json_from_plan(self, plan: Dict[str, Any]) -> str:
        """Create package.json from planner dependencies for TypeScript projects."""
        dependencies = plan.get('dependencies', [])
        
        # Default Next.js project structure
        output_format = self.config.get("output_format", "python")
        if output_format == "tsx":
            package_json = {
                "name": "generated-nextjs-project",
                "version": "1.0.0",
                "description": "Generated Next.js project",
                "private": True,
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start",
                    "lint": "next lint"
                },
                "dependencies": {
                    "next": "^14.0.0",
                    "react": "^18.0.0",
                    "react-dom": "^18.0.0"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "@types/node": "^20.0.0",
                    "@types/react": "^18.0.0",
                    "@types/react-dom": "^18.0.0",
                    "tailwindcss": "^3.3.0",
                    "autoprefixer": "^10.4.0",
                    "postcss": "^8.4.0"
                }
            }
        else:
            package_json = {
                "name": "generated-typescript-project",
                "version": "1.0.0",
                "description": "Generated TypeScript project",
                "main": "index.js",
                "scripts": {
                    "build": "tsc",
                    "start": "node index.js",
                    "dev": "ts-node index.ts",
                    "test": "jest"
                },
                "dependencies": {},
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "ts-node": "^10.9.0",
                    "@types/node": "^20.0.0"
                }
            }
        
        # Add dependencies from plan
        for dep in dependencies:
            if isinstance(dep, str):
                package_json["dependencies"][dep] = "latest"
            elif isinstance(dep, dict):
                package = dep.get('package', '')
                version = dep.get('version', 'latest')
                if package:
                    package_json["dependencies"][package] = version
        
        # Add common TypeScript dependencies if not present
        common_deps = ["express", "axios", "lodash"]
        for dep in common_deps:
            if dep not in package_json["dependencies"]:
                package_json["dependencies"][dep] = "latest"
        
        return json.dumps(package_json, indent=2)
    
    def create_tsconfig_json(self) -> str:
        """Create a standard tsconfig.json for TypeScript projects."""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": [
                "**/*.ts"
            ],
            "exclude": [
                "node_modules",
                "dist"
            ]
        }
        
        return json.dumps(tsconfig, indent=2)
    
    def validate_code_consistency(self, generated_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate consistency between generated files."""
        validation_result = {
            "consistent": True,
            "issues": [],
            "suggestions": []
        }
        
        if not generated_files:
            validation_result["consistent"] = False
            validation_result["issues"].append("No files generated")
            return validation_result
        
        # Check for basic syntax issues
        for filename, content in generated_files.items():
            if not content.strip():
                validation_result["issues"].append(f"Empty file: {filename}")
                validation_result["consistent"] = False
            
            # Check for common Python issues
            if filename.endswith('.py'):
                try:
                    compile(content, filename, 'exec')
                except SyntaxError as e:
                    validation_result["issues"].append(f"Syntax error in {filename}: {e}")
                    validation_result["consistent"] = False
            
            # Check for TypeScript/TSX syntax issues
            elif filename.endswith(('.ts', '.tsx')):
                # Check for valid imports
                if 'import' in content and 'from' not in content:
                    validation_result["issues"].append(f"Invalid import syntax in {filename}")
                    validation_result["consistent"] = False
                
                # Check for proper JSX structure in TSX files
                if filename.endswith('.tsx'):
                    if '<' in content and '>' in content:
                        # Basic JSX validation
                        open_tags = content.count('<')
                        close_tags = content.count('>')
                        if abs(open_tags - close_tags) > 2:  # Allow for some legitimate differences
                            validation_result["issues"].append(f"Potential JSX tag mismatch in {filename}")
                            validation_result["consistent"] = False
                
                # Check for proper export syntax
                if 'export' in content and not any(keyword in content for keyword in ['export default', 'export {', 'export *']):
                    validation_result["suggestions"].append(f"Consider using explicit export syntax in {filename}")
                
                # Check for common React/Next.js errors
                if 'useState' in content and 'import' not in content:
                    validation_result["issues"].append(f"Missing React import in {filename}")
                    validation_result["consistent"] = False
                
                if 'useEffect' in content and 'import' not in content:
                    validation_result["issues"].append(f"Missing React import in {filename}")
                    validation_result["consistent"] = False
                
                # Check for class components without "use client"
                if 'class ' in content and 'extends Component' in content and '"use client"' not in content:
                    validation_result["issues"].append(f"Class component missing 'use client' directive in {filename}")
                    validation_result["consistent"] = False
                
                # Check for @/ imports which cause issues in App Router
                if '@/components/' in content:
                    validation_result["issues"].append(f"Using @/ alias instead of relative paths in {filename}")
                    validation_result["consistent"] = False
                
                # Check for ErrorBoundary without "use client"
                if 'ErrorBoundary' in content and 'class' in content and '"use client"' not in content:
                    validation_result["issues"].append(f"ErrorBoundary class component missing 'use client' directive in {filename}")
                    validation_result["consistent"] = False
                
                # Check for external library imports that aren't installed
                external_libs = ['framer-motion', 'react-spring', 'react-transition-group', 'lottie-react']
                for lib in external_libs:
                    if f'import.*{lib}' in content:
                        validation_result["issues"].append(f"External library '{lib}' imported but not installed in {filename}")
                        validation_result["consistent"] = False
                
                # Check for proper TypeScript types
                if 'interface' in content or 'type' in content:
                    if 'export' not in content and 'import' not in content:
                        validation_result["suggestions"].append(f"Consider exporting types in {filename}")
                
                # Check for async/await usage
                if 'async' in content and 'await' not in content:
                    validation_result["suggestions"].append(f"Async function without await in {filename}")
                
                # Check for proper error handling
                if 'try' in content and 'catch' not in content:
                    validation_result["suggestions"].append(f"Try block without catch in {filename}")
        
        # Check for import consistency
        imports = set()
        for filename, content in generated_files.items():
            if filename.endswith('.py'):
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        imports.add(line.strip())
            elif filename.endswith('.ts'):
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('import ') or line.strip().startswith('export '):
                        imports.add(line.strip())
        
        # Check if imports are used
        for import_line in imports:
            import_name = import_line.split()[1].split('.')[0]
            used = False
            for content in generated_files.values():
                if import_name in content:
                    used = True
                    break
            if not used:
                validation_result["suggestions"].append(f"Unused import: {import_line}")
        
        logger.info(f"Code validation: {len(validation_result['issues'])} issues found")
        return validation_result
    
    def validate_tsx_compilation(self, generated_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate TSX files by attempting to compile them."""
        validation_result = {
            "compilation_errors": [],
            "warnings": [],
            "success": True
        }
        
        # Check if we have the necessary files for a Next.js app
        required_files = ["page.tsx", "layout.tsx", "package.json"]
        missing_files = [f for f in required_files if f not in generated_files]
        
        if missing_files:
            validation_result["compilation_errors"].append(f"Missing required files: {', '.join(missing_files)}")
            validation_result["success"] = False
        
        # Validate package.json structure
        if "package.json" in generated_files:
            try:
                package_data = json.loads(generated_files["package.json"])
                required_deps = ["next", "react", "react-dom"]
                missing_deps = [dep for dep in required_deps if dep not in package_data.get("dependencies", {})]
                
                if missing_deps:
                    validation_result["compilation_errors"].append(f"Missing required dependencies: {', '.join(missing_deps)}")
                    validation_result["success"] = False
                    
            except json.JSONDecodeError:
                validation_result["compilation_errors"].append("Invalid package.json format")
                validation_result["success"] = False
        
        # Validate TSX syntax patterns (CRITICAL ERRORS FIRST)
        required_files = ["page.tsx", "layout.tsx"]
        for filename, content in generated_files.items():
            if filename.endswith('.tsx'):
                # CRITICAL: Check for proper component structure in required files
                if filename in required_files:
                    if 'export default function' not in content and 'export default' not in content:
                        validation_result["compilation_errors"].append(f"CRITICAL: Missing default export in required file {filename}")
                        validation_result["success"] = False
                
                # Check for proper React imports
                if 'React' in content and 'import React' not in content:
                    validation_result["warnings"].append(f"Consider explicit React import in {filename}")
                
                # Check for proper component structure (for all files)
                if 'export default function' not in content and 'export default' not in content:
                    validation_result["compilation_errors"].append(f"Missing default export in {filename}")
                    validation_result["success"] = False
                
                # Check for proper JSX return
                if 'return (' not in content and 'return <' not in content:
                    validation_result["warnings"].append(f"Component may not return JSX in {filename}")
                
                # Check for class components without "use client"
                if 'class ' in content and 'extends Component' in content and '"use client"' not in content:
                    validation_result["compilation_errors"].append(f"Class component missing 'use client' directive in {filename}")
                    validation_result["success"] = False
                
                # Check for @/ imports
                if '@/components/' in content:
                    validation_result["compilation_errors"].append(f"Using @/ alias instead of relative paths in {filename}")
                    validation_result["success"] = False
                
                # Check for ErrorBoundary without "use client"
                if 'ErrorBoundary' in content and 'class' in content and '"use client"' not in content:
                    validation_result["compilation_errors"].append(f"ErrorBoundary missing 'use client' directive in {filename}")
                    validation_result["success"] = False
                
                # CRITICAL: Check for Next.js specific errors
                if filename == 'layout.tsx':
                    # layout.tsx must be server component with metadata
                    if '"use client"' in content:
                        validation_result["compilation_errors"].append(f"CRITICAL: layout.tsx cannot use 'use client' - must be server component")
                        validation_result["success"] = False
                    
                    if 'export const metadata' not in content:
                        validation_result["compilation_errors"].append(f"CRITICAL: layout.tsx must export metadata")
                        validation_result["success"] = False
                
                # Check for metadata in client components
                if '"use client"' in content and 'export const metadata' in content:
                    validation_result["compilation_errors"].append(f"CRITICAL: Client component {filename} cannot export metadata")
                    validation_result["success"] = False
        
        return validation_result
    
    def validate_code_quality(self, generated_files: Dict[str, str]) -> Dict[str, Any]:
        """Validate code quality (ESLint-like checks without external calls)."""
        import re
        
        quality_result = {
            "success": True,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        for filename, content in generated_files.items():
            if filename.endswith('.tsx'):
                # Check for common code quality issues
                
                # 1. Check for trailing whitespace
                if re.search(r'[ \t]+$', content, re.MULTILINE):
                    quality_result["warnings"].append(f"Trailing whitespace found in {filename}")
                
                # 2. Check for inconsistent quotes
                single_quotes = len(re.findall(r"'[^']*'", content))
                double_quotes = len(re.findall(r'"[^"]*"', content))
                if double_quotes > single_quotes:
                    quality_result["suggestions"].append(f"Consider using single quotes consistently in {filename}")
                
                # 3. Check for missing semicolons
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}') and not line.strip().endswith('(') and not line.strip().endswith(')'):
                        if 'return' in line or 'const' in line or 'let' in line or 'var' in line:
                            quality_result["warnings"].append(f"Missing semicolon in {filename}:{i}")
                
                # 4. Check for proper TypeScript types
                if 'function' in content and ': any' not in content and 'React.FC' not in content:
                    quality_result["suggestions"].append(f"Consider adding TypeScript types in {filename}")
                
                # 5. Check for accessibility issues
                if '<img' in content and 'alt=' not in content:
                    quality_result["issues"].append(f"Missing alt attribute for images in {filename}")
                
                if '<button' in content and 'aria-label' not in content:
                    quality_result["suggestions"].append(f"Consider adding aria-label for buttons in {filename}")
                
                # 6. Check for performance issues
                if '.map(' in content and 'key=' not in content:
                    quality_result["issues"].append(f"Missing key prop in map function in {filename}")
                
                # 7. Check for React best practices
                if 'class=' in content and 'className=' not in content:
                    quality_result["issues"].append(f"Use className instead of class in {filename}")
                
                if 'onclick=' in content.lower():
                    quality_result["issues"].append(f"Use onClick instead of onclick in {filename}")
        
        # Set success based on critical issues
        if quality_result["issues"]:
            quality_result["success"] = False
        
        return quality_result
    
    def save_generated_files(self, generated_files: Dict[str, str], project_name: str = None) -> Dict[str, str]:
        """Save generated files to the output directory."""
        output_format = self.config.get("output_format", "python")
        
        if output_format == "tsx":
            # For TSX projects, save directly to my-new-website/src/app
            project_dir = self.output_dir
            logger.info(f"🎯 Saving TSX files directly to: {project_dir.absolute()}")
        else:
            # For other projects, create timestamped subdirectory
            if not project_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                project_name = f"project_{timestamp}"
            project_dir = self.output_dir / project_name
            project_dir.mkdir(exist_ok=True)
            logger.info(f"🎯 Saving files to: {project_dir.absolute()}")
        
        saved_files = {}
        
        for filename, content in generated_files.items():
            file_path = project_dir / filename
            
            # Ensure directory exists for nested files
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Simply overwrite the file (no backup, no questions)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                saved_files[filename] = str(file_path)
                logger.info(f"✅ Overwritten: {file_path.absolute()}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save {filename}: {e}")
        
        # Project summary is no longer generated
        logger.info(f"✅ Project files saved successfully to {project_dir.absolute()}")
        
        return saved_files
    
    def run_complete_workflow(self, user_prompt: str) -> Dict[str, Any]:
        """Run the complete workflow from prompt to saved files."""
        logger.info("🎯 Starting complete AICoder workflow")
        logger.info(f"📝 User prompt: {user_prompt}")
        
        try:
            # Step 1: Execute workflow
            workflow_state = self.execute_workflow(user_prompt)
            
            if "error" in workflow_state:
                return {
                    "success": False,
                    "error": workflow_state["error"],
                    "user_prompt": user_prompt
                }
            
            # Step 2: Extract generated code
            generated_files = self.extract_generated_code(workflow_state)
            
            if not generated_files:
                return {
                    "success": False,
                    "error": "No code was generated",
                    "user_prompt": user_prompt,
                    "workflow_state": workflow_state
                }
            
            # Step 3: Validate code consistency
            validation = self.validate_code_consistency(generated_files)
            
            # Step 3.5: Additional TSX validation and compilation if applicable
            output_format = self.config.get("output_format", "python")
            if output_format == "tsx":
                # CRITICAL: Final validation and force fixing of all files
                generated_files = self.validate_and_force_fix_files(generated_files)
                
                # Fix missing component imports before compilation
                generated_files = self.fix_missing_component_imports(generated_files)
                
                # Step 3.5.5: Post-process code quality (ESLint-like without external calls)
                generated_files = self.post_process_code_quality(generated_files)
                
                # Step 3.5.6: Validate code quality
                quality_validation = self.validate_code_quality(generated_files)
                validation["quality_validation"] = quality_validation
                
                if not quality_validation["success"]:
                    logger.warning(f"Code quality issues found: {quality_validation['issues']}")
                
                # Validate TSX syntax
                tsx_validation = self.validate_tsx_compilation(generated_files)
                validation["tsx_validation"] = tsx_validation
                
                if not tsx_validation["success"]:
                    logger.warning(f"TSX compilation issues found: {tsx_validation['compilation_errors']}")
                
                # Step 3.6: Actual compilation check
                project_dir = str(self.output_dir.parent.parent)  # my-new-website directory
                compilation_result = self.compile_and_check_website(project_dir)
                validation["compilation_result"] = compilation_result
                
                if compilation_result["success"]:
                    logger.info("🎉 Website compiles successfully!")
                else:
                    logger.error(f"❌ Website compilation failed: {len(compilation_result['errors'])} errors")
                    # Log first few errors
                    for error in compilation_result["errors"][:3]:
                        logger.error(f"   - {error}")
                    
                    # Step 3.7: Auto-fix compilation errors
                    logger.info("🔧 Attempting to auto-fix compilation errors...")
                    generated_files = self.auto_fix_compilation_errors(generated_files, compilation_result["errors"])
                    
                    # Re-compile after fixes
                    logger.info("🔨 Re-compiling after auto-fixes...")
                    compilation_result_2 = self.compile_and_check_website(project_dir)
                    validation["compilation_result_after_fix"] = compilation_result_2
                    
                    if compilation_result_2["success"]:
                        logger.info("🎉 Website compiles successfully after auto-fixes!")
                    else:
                        logger.error(f"❌ Website still has compilation errors after auto-fixes")
                        for error in compilation_result_2["errors"][:3]:
                            logger.error(f"   - {error}")
            
            # Step 4: Save files
            output_format = self.config.get("output_format", "python")
            if output_format == "tsx":
                project_name = "my-new-website"
            else:
                project_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            saved_files = self.save_generated_files(generated_files, project_name)
            
            # Step 5: Prepare result
            result = {
                "success": True,
                "user_prompt": user_prompt,
                "project_name": project_name,
                "generated_files": list(generated_files.keys()),
                "saved_files": saved_files,
                "validation": validation,
                "workflow_state": {
                    "plan": workflow_state.get("plan"),
                    "coder_result": workflow_state.get("coder_result"),
                    "test_results": workflow_state.get("test_results")
                }
            }
            
            logger.info("🎉 Complete workflow finished successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Complete workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_prompt": user_prompt
            }

    def force_syntax_correction(self, content: str, filename: str) -> str:
        """Force syntax correction by applying multiple passes of fixes until code is valid."""
        import re
        
        logger.info(f"🔧 Force correcting syntax for {filename}")
        
        # Multiple passes to ensure all errors are fixed
        for pass_num in range(5):  # Up to 5 passes
            original_content = content
            
            # Pass 1: Fix TypeScript function syntax
            content = self.aggressive_fix_function_syntax(content)
            
            # Pass 2: Fix JSX syntax
            content = self.aggressive_fix_jsx_syntax(content)
            
            # Pass 3: Fix import/export syntax
            content = self.aggressive_fix_import_export_syntax(content)
            
            # Pass 4: Fix Next.js specific issues
            content = self.aggressive_fix_nextjs_syntax(content, filename)
            
            # Pass 5: Final cleanup
            content = self.final_syntax_cleanup(content)
            
            # If no changes were made, we're done
            if content == original_content:
                logger.info(f"✅ Syntax correction completed in {pass_num + 1} passes")
                break
        
        return content
    
    def aggressive_fix_function_syntax(self, content: str) -> str:
        """Aggressively fix function syntax errors."""
        import re
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Fix ALL variations of invalid function parameters
            patterns_to_fix = [
                (r'function\s+\w+\s*\(\s*:\s*any\s*\)', 'function Component()'),
                (r'export\s+default\s+function\s+\w+\s*\(\s*:\s*any\s*\)', 'export default function Component()'),
                (r'\(\s*:\s*any\s*\)', '()'),
                (r'}\s*:\s*{\s*[^}]*}\s*:\s*any\s*\)', '}: { children: React.ReactNode })'),
                (r'}\s*:\s*any\s*\)', ')'),
            ]
            
            for pattern, replacement in patterns_to_fix:
                if re.search(pattern, fixed_line):
                    # Extract the actual function name if present
                    func_match = re.search(r'function\s+(\w+)', fixed_line)
                    if func_match:
                        func_name = func_match.group(1)
                        fixed_line = re.sub(pattern, replacement.replace('Component', func_name), fixed_line)
                    else:
                        fixed_line = re.sub(pattern, replacement, fixed_line)
            
            # Fix any remaining malformed function declarations
            if 'function' in fixed_line and '(' in fixed_line and ')' in fixed_line:
                # Ensure proper spacing around parentheses
                fixed_line = re.sub(r'\(\s*:\s*', '(', fixed_line)
                fixed_line = re.sub(r'\s*:\s*\)', ')', fixed_line)
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def aggressive_fix_jsx_syntax(self, content: str) -> str:
        """Aggressively fix JSX syntax errors."""
        import re
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Remove ALL semicolons from JSX (except in comments)
            if not fixed_line.strip().startswith('//') and not fixed_line.strip().startswith('/*'):
                # Fix JSX tags with semicolons
                fixed_line = re.sub(r'<\s*(\w+)\s*;', r'<\1', fixed_line)
                fixed_line = re.sub(r';\s*(\w+)\s*>', r'\1>', fixed_line)
                
                # Fix JSX attributes with semicolons
                fixed_line = re.sub(r'(\w+)\s*=\s*["\']([^"\']*)["\']\s*;', r'\1="\2"', fixed_line)
                fixed_line = re.sub(r';\s*(\w+)\s*=\s*["\']', r' \1="', fixed_line)
                
                # Fix self-closing tags
                fixed_line = re.sub(r'<\s*(\w+)\s*;([^>]*)\s*/>', r'<\1\2/>', fixed_line)
                fixed_line = re.sub(r'<\s*(\w+)([^>]*)\s*;\s*/>', r'<\1\2/>', fixed_line)
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def aggressive_fix_import_export_syntax(self, content: str) -> str:
        """Aggressively fix import/export syntax errors."""
        import re
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Fix import statements
            if fixed_line.strip().startswith('import'):
                # Remove semicolons that are not at the end
                if not fixed_line.strip().endswith(';'):
                    fixed_line = re.sub(r';\s+from\s+', ' from ', fixed_line)
                    fixed_line = re.sub(r'}\s*;\s*from\s+', '} from ', fixed_line)
                    fixed_line = re.sub(r'\s*;\s*from\s+', ' from ', fixed_line)
            
            # Fix export statements
            if fixed_line.strip().startswith('export'):
                # Remove semicolons that are not at the end
                if not fixed_line.strip().endswith(';'):
                    fixed_line = re.sub(r';\s*\(', '(', fixed_line)
                    fixed_line = re.sub(r'function\s+(\w+)\s*;\s*\(', r'function \1(', fixed_line)
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    def aggressive_fix_nextjs_syntax(self, content: str, filename: str) -> str:
        """Aggressively fix Next.js specific syntax issues."""
        import re
        
        # Fix layout.tsx specific issues
        if filename == 'layout.tsx':
            # Ensure proper function signature
            content = re.sub(
                r'export\s+default\s+function\s+(\w+)\s*\(\s*:\s*any\s*\)',
                r'export default function \1({ children }: { children: React.ReactNode })',
                content
            )
            
            # Ensure proper function signature without any
            content = re.sub(
                r'export\s+default\s+function\s+(\w+)\s*\(\s*\)',
                r'export default function \1({ children }: { children: React.ReactNode })',
                content
            )
            
            # Remove any "use client" directive
            content = re.sub(r'"use client"\s*\n?', '', content)
            
            # Ensure metadata export exists
            if 'export const metadata' not in content:
                metadata_export = '''export const metadata = {
  title: 'Generated App',
  description: 'Generated by AICoder',
}'''
                # Insert after imports
                import_end = content.find('\n\n')
                if import_end != -1:
                    content = content[:import_end] + '\n\n' + metadata_export + content[import_end:]
                else:
                    content = metadata_export + '\n\n' + content
        
        # Fix page.tsx specific issues
        elif filename == 'page.tsx':
            # Ensure proper function signature
            content = re.sub(
                r'export\s+default\s+function\s+(\w+)\s*\(\s*:\s*any\s*\)',
                r'export default function \1()',
                content
            )
            
            # Remove "use client" if not needed
            if '"use client"' in content:
                needs_client = any(keyword in content for keyword in ['useState', 'useEffect', 'onClick', 'onChange', 'addEventListener'])
                if not needs_client:
                    content = re.sub(r'"use client"\s*\n?', '', content)
        
        return content
    
    def final_syntax_cleanup(self, content: str) -> str:
        """Final cleanup pass to ensure syntax is correct."""
        import re
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # Remove any remaining problematic patterns
            # Fix any remaining function parameter issues
            fixed_line = re.sub(r'\(\s*:\s*any\s*\)', '()', fixed_line)
            fixed_line = re.sub(r'\(\s*:\s*\)', '()', fixed_line)
            
            # Fix any remaining JSX issues
            fixed_line = re.sub(r'<\s*(\w+)\s*;', r'<\1', fixed_line)
            fixed_line = re.sub(r';\s*(\w+)\s*>', r'\1>', fixed_line)
            
            # Fix any remaining import/export issues
            if fixed_line.strip().startswith('import') and ';' in fixed_line and not fixed_line.strip().endswith(';'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
            
            if fixed_line.strip().startswith('export') and ';' in fixed_line and not fixed_line.strip().endswith(';'):
                fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)

    def validate_and_force_fix_files(self, generated_files: Dict[str, str]) -> Dict[str, str]:
        """Validate all files and force fix any remaining syntax errors before saving."""
        logger.info("🔍 Final validation and force fixing of all files...")
        
        fixed_files = {}
        
        for filename, content in generated_files.items():
            logger.info(f"🔧 Validating and fixing {filename}")
            
            # Apply aggressive fixes
            fixed_content = self.force_syntax_correction(content, filename)
            
            # Additional validation for specific file types
            if filename.endswith('.tsx'):
                # Ensure proper TypeScript syntax
                fixed_content = self.ensure_valid_typescript(fixed_content, filename)
            
            # Log if changes were made
            if fixed_content != content:
                logger.info(f"✅ Fixed syntax errors in {filename}")
                # Log the specific fixes
                original_lines = content.split('\n')
                fixed_lines = fixed_content.split('\n')
                
                for i, (orig, fixed) in enumerate(zip(original_lines, fixed_lines)):
                    if orig != fixed:
                        logger.info(f"  Line {i+1}: {orig.strip()} -> {fixed.strip()}")
            else:
                logger.info(f"✅ {filename} is already syntactically correct")
            
            fixed_files[filename] = fixed_content
        
        return fixed_files
    
    def ensure_valid_typescript(self, content: str, filename: str) -> str:
        """Ensure the content is valid TypeScript/TSX syntax."""
        import re
        
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            # CRITICAL: Fix any remaining function parameter issues
            # This is the most common error we're seeing
            if 'function' in fixed_line and '(' in fixed_line and ')' in fixed_line:
                # Fix function declarations with invalid parameters
                fixed_line = re.sub(r'function\s+(\w+)\s*\(\s*:\s*any\s*\)', r'function \1()', fixed_line)
                fixed_line = re.sub(r'export\s+default\s+function\s+(\w+)\s*\(\s*:\s*any\s*\)', r'export default function \1()', fixed_line)
                
                # Fix function declarations with missing parameters
                fixed_line = re.sub(r'function\s+(\w+)\s*\(\s*\)', r'function \1()', fixed_line)
                fixed_line = re.sub(r'export\s+default\s+function\s+(\w+)\s*\(\s*\)', r'export default function \1()', fixed_line)
            
            # Fix any remaining type annotation issues
            if '}: {' in fixed_line and '}: any)' in fixed_line:
                fixed_line = fixed_line.replace('}: any)', ')')
            
            # Fix any remaining JSX issues
            if '<' in fixed_line and '>' in fixed_line and ';' in fixed_line:
                if not fixed_line.strip().startswith('//'):
                    fixed_line = fixed_line.replace('; ', ' ').replace(' ;', ' ')
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)

def main():
    """Main entry point for the AICoder application."""
    print("🚀 AICoder - AI-Powered Code Generation System")
    print("=" * 60)
    
    # Initialize the workflow
    workflow = AICoderWorkflow()
    
    # Get user input
    print("\n📝 Enter your project description:")
    print("   (e.g., 'Create a simple calculator with add, subtract, multiply, divide functions')")
    print("   (or 'quit' to exit)")
    
    while True:
        try:
            user_prompt = input("\n🎯 Your request: ").strip()
            
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_prompt:
                print("⚠️  Please enter a project description")
                continue
            
            print(f"\n🔄 Processing: {user_prompt}")
            print("   This may take a few moments...")
            
            # Run the complete workflow
            result = workflow.run_complete_workflow(user_prompt)
            
            if result["success"]:
                print("\n✅ Project generated successfully!")
                print(f"📁 Project: {result['project_name']}")
                print(f"📄 Files: {', '.join(result['generated_files'])}")
                
                # Show validation results
                validation = result["validation"]
                if validation["issues"]:
                    print(f"\n⚠️  Issues found:")
                    for issue in validation["issues"]:
                        print(f"   - {issue}")
                
                if validation["suggestions"]:
                    print(f"\n💡 Suggestions:")
                    for suggestion in validation["suggestions"]:
                        print(f"   - {suggestion}")
                
                # Show TSX-specific validation results
                if "tsx_validation" in validation:
                    tsx_val = validation["tsx_validation"]
                    if tsx_val["compilation_errors"]:
                        print(f"\n❌ TSX Compilation Errors:")
                        for error in tsx_val["compilation_errors"]:
                            print(f"   - {error}")
                    
                    if tsx_val["warnings"]:
                        print(f"\n⚠️  TSX Warnings:")
                        for warning in tsx_val["warnings"]:
                            print(f"   - {warning}")
                    
                    if tsx_val["success"]:
                        print(f"\n✅ TSX compilation validation passed!")
                
                # Show code quality validation results
                if "quality_validation" in validation:
                    quality_val = validation["quality_validation"]
                    if quality_val["issues"]:
                        print(f"\n🔍 Code Quality Issues:")
                        for issue in quality_val["issues"][:5]:
                            print(f"   - {issue}")
                    
                    if quality_val["warnings"]:
                        print(f"\n⚠️  Code Quality Warnings:")
                        for warning in quality_val["warnings"][:3]:
                            print(f"   - {warning}")
                    
                    if quality_val["suggestions"]:
                        print(f"\n💡 Code Quality Suggestions:")
                        for suggestion in quality_val["suggestions"][:3]:
                            print(f"   - {suggestion}")
                    
                    if quality_val["success"]:
                        print(f"\n✅ Code quality validation passed!")
                
                # Show actual compilation results
                if "compilation_result" in validation:
                    comp_result = validation["compilation_result"]
                    if comp_result["success"]:
                        print(f"\n🎉 Website compiles successfully!")
                    else:
                        print(f"\n❌ Website compilation failed:")
                        for error in comp_result["errors"][:5]:  # Show first 5 errors
                            print(f"   - {error}")
                        
                        if comp_result["warnings"]:
                            print(f"\n⚠️  Compilation Warnings:")
                            for warning in comp_result["warnings"][:3]:
                                print(f"   - {warning}")
                
                # Show the correct path based on project type
                output_format = workflow.config.get("output_format", "python")
                if output_format == "tsx":
                    print(f"\n📂 Files saved to: {workflow.output_dir}")
                else:
                    print(f"\n📂 Files saved to: {workflow.output_dir}/{result['project_name']}")
                
            else:
                print(f"\n❌ Failed to generate project: {result.get('error', 'Unknown error')}")
            
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            logger.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    main()
