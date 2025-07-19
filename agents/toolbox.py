"""
Toolbox Agent

This agent provides utility functions and tools that can be used by other agents
in the system. It includes file operations, code analysis, formatting, and other
common development tasks.
"""

from typing import Dict, Any, List, Optional, Union
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import logging
import os
import json
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import hashlib
import zipfile
import requests
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    max_tokens=2000
)

class FileManager:
    """Handles file operations and management"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.temp_dir = tempfile.mkdtemp()
    
    def create_file(self, file_path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Create a new file with the specified content.
        
        Args:
            file_path: Path to the file
            content: File content
            overwrite: Whether to overwrite existing file
            
        Returns:
            Operation result
        """
        try:
            full_path = self.base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if full_path.exists() and not overwrite:
                return {
                    "success": False,
                    "error": "File already exists",
                    "path": str(full_path)
                }
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(full_path),
                "size": len(content),
                "created": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read content from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content and metadata
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stat = full_path.stat()
            return {
                "success": True,
                "content": content,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "path": str(full_path)
            }
            
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def update_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """
        Update an existing file with new content.
        
        Args:
            file_path: Path to the file
            content: New content
            
        Returns:
            Operation result
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
            
            # Create backup
            backup_path = full_path.with_suffix(full_path.suffix + '.backup')
            shutil.copy2(full_path, backup_path)
            
            # Update file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(full_path),
                "backup": str(backup_path),
                "size": len(content),
                "updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Operation result
        """
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {"success": False, "error": "File not found"}
            
            # Create backup before deletion
            backup_path = Path(self.temp_dir) / f"deleted_{full_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(full_path, backup_path)
            
            full_path.unlink()
            
            return {
                "success": True,
                "path": str(full_path),
                "backup": str(backup_path),
                "deleted": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, directory: str = ".", pattern: str = "*") -> Dict[str, Any]:
        """
        List files in a directory.
        
        Args:
            directory: Directory to list
            pattern: File pattern to match
            
        Returns:
            List of files
        """
        try:
            full_path = self.base_path / directory
            
            if not full_path.exists():
                return {"success": False, "error": "Directory not found"}
            
            files = []
            for file_path in full_path.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(self.base_path)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "type": file_path.suffix
                    })
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "directory": str(full_path)
            }
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return {"success": False, "error": str(e)}

class CodeAnalyzer:
    """Analyzes and processes code"""
    
    def __init__(self):
        self.supported_languages = ["python", "javascript", "typescript", "java", "cpp", "csharp"]
    
    def analyze_code_structure(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze the structure of code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Code structure analysis
        """
        try:
            analysis = {
                "language": language,
                "lines": len(code.split('\n')),
                "characters": len(code),
                "functions": [],
                "classes": [],
                "imports": [],
                "comments": [],
                "complexity": 0
            }
            
            if language == "python":
                analysis.update(self._analyze_python(code))
            elif language in ["javascript", "typescript"]:
                analysis.update(self._analyze_javascript(code))
            elif language == "java":
                analysis.update(self._analyze_java(code))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing code structure: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_python(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure"""
        functions = re.findall(r'def\s+(\w+)\s*\(', code)
        classes = re.findall(r'class\s+(\w+)', code)
        imports = re.findall(r'import\s+(\w+)|from\s+(\w+)\s+import', code)
        comments = re.findall(r'#.*$', code, re.MULTILINE)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": [imp[0] if imp[0] else imp[1] for imp in imports],
            "comments": comments,
            "function_count": len(functions),
            "class_count": len(classes)
        }
    
    def _analyze_javascript(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code structure"""
        functions = re.findall(r'function\s+(\w+)|const\s+(\w+)\s*=|let\s+(\w+)\s*=', code)
        classes = re.findall(r'class\s+(\w+)', code)
        imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', code)
        comments = re.findall(r'//.*$|/\*.*?\*/', code, re.MULTILINE | re.DOTALL)
        
        return {
            "functions": [func[0] if func[0] else func[1] if func[1] else func[2] for func in functions],
            "classes": classes,
            "imports": imports,
            "comments": comments,
            "function_count": len(functions),
            "class_count": len(classes)
        }
    
    def _analyze_java(self, code: str) -> Dict[str, Any]:
        """Analyze Java code structure"""
        functions = re.findall(r'(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?\w+\s+(\w+)\s*\(', code)
        classes = re.findall(r'class\s+(\w+)', code)
        imports = re.findall(r'import\s+(.+?);', code)
        comments = re.findall(r'//.*$|/\*.*?\*/', code, re.MULTILINE | re.DOTALL)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "comments": comments,
            "function_count": len(functions),
            "class_count": len(classes)
        }
    
    def format_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Format code according to language conventions.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        try:
            if language == "python":
                return self._format_python(code)
            elif language in ["javascript", "typescript"]:
                return self._format_javascript(code)
            else:
                return {"success": False, "error": f"Language {language} not supported for formatting"}
                
        except Exception as e:
            logger.error(f"Error formatting code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _format_python(self, code: str) -> Dict[str, Any]:
        """Format Python code using black"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ["black", "--quiet", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                
                os.unlink(temp_file)
                return {"success": True, "formatted_code": formatted_code}
            else:
                os.unlink(temp_file)
                return {"success": False, "error": "Formatting failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _format_javascript(self, code: str) -> Dict[str, Any]:
        """Format JavaScript/TypeScript code using prettier"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ["npx", "prettier", "--write", temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                with open(temp_file, 'r') as f:
                    formatted_code = f.read()
                
                os.unlink(temp_file)
                return {"success": True, "formatted_code": formatted_code}
            else:
                os.unlink(temp_file)
                return {"success": False, "error": "Formatting failed"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

class DependencyManager:
    """Manages project dependencies"""
    
    def __init__(self):
        self.package_managers = {
            "python": "pip",
            "javascript": "npm",
            "typescript": "npm",
            "java": "maven",
            "csharp": "nuget"
        }
    
    def analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """
        Analyze project dependencies.
        
        Args:
            project_path: Path to the project
            
        Returns:
            Dependency analysis
        """
        try:
            project_path = Path(project_path)
            
            if not project_path.exists():
                return {"success": False, "error": "Project path not found"}
            
            dependencies = {}
            
            # Check for Python dependencies
            requirements_file = project_path / "requirements.txt"
            if requirements_file.exists():
                dependencies["python"] = self._parse_requirements(requirements_file)
            
            # Check for Node.js dependencies
            package_json = project_path / "package.json"
            if package_json.exists():
                dependencies["nodejs"] = self._parse_package_json(package_json)
            
            # Check for Java dependencies
            pom_xml = project_path / "pom.xml"
            if pom_xml.exists():
                dependencies["java"] = self._parse_pom_xml(pom_xml)
            
            return {
                "success": True,
                "dependencies": dependencies,
                "project_path": str(project_path)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_requirements(self, file_path: Path) -> List[Dict[str, str]]:
        """Parse Python requirements.txt file"""
        dependencies = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Simple parsing - could be enhanced
                        if '==' in line:
                            name, version = line.split('==', 1)
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                        else:
                            name, version = line, "latest"
                        
                        dependencies.append({
                            "name": name.strip(),
                            "version": version.strip(),
                            "type": "python"
                        })
        except Exception as e:
            logger.error(f"Error parsing requirements.txt: {str(e)}")
        
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse Node.js package.json file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return {
                "dependencies": data.get("dependencies", {}),
                "devDependencies": data.get("devDependencies", {}),
                "scripts": data.get("scripts", {}),
                "name": data.get("name", ""),
                "version": data.get("version", "")
            }
        except Exception as e:
            logger.error(f"Error parsing package.json: {str(e)}")
            return {}
    
    def _parse_pom_xml(self, file_path: Path) -> Dict[str, Any]:
        """Parse Java pom.xml file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple XML parsing - could be enhanced with proper XML parser
            dependencies = re.findall(r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?<version>(.*?)</version>.*?</dependency>', content, re.DOTALL)
            
            return {
                "dependencies": [
                    {"groupId": dep[0], "artifactId": dep[1], "version": dep[2]}
                    for dep in dependencies
                ]
            }
        except Exception as e:
            logger.error(f"Error parsing pom.xml: {str(e)}")
            return {}

def toolbox_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Toolbox node that provides utility functions and tools.
    
    Args:
        state: The current state containing tool requests
        
    Returns:
        Updated state with tool results
    """
    try:
        # Extract tool request information
        tool_request = state.get("tool_request", {})
        tool_type = tool_request.get("type", "")
        tool_params = tool_request.get("params", {})
        
        # Initialize tools
        file_manager = FileManager()
        code_analyzer = CodeAnalyzer()
        dependency_manager = DependencyManager()
        
        # Process tool request
        if tool_type == "file_operation":
            result = process_file_operation(file_manager, tool_params)
        elif tool_type == "code_analysis":
            result = process_code_analysis(code_analyzer, tool_params)
        elif tool_type == "dependency_analysis":
            result = process_dependency_analysis(dependency_manager, tool_params)
        elif tool_type == "code_formatting":
            result = process_code_formatting(code_analyzer, tool_params)
        else:
            result = {"success": False, "error": f"Unknown tool type: {tool_type}"}
        
        # Update state with tool results
        updated_state = state.copy()
        updated_state["tool_result"] = result
        updated_state["toolbox_status"] = "completed"
        
        logger.info(f"Toolbox operation completed: {tool_type}")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in toolbox node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["toolbox_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def process_file_operation(file_manager: FileManager, params: Dict[str, Any]) -> Dict[str, Any]:
    """Process file operation requests"""
    operation = params.get("operation", "")
    
    if operation == "create":
        return file_manager.create_file(
            params.get("file_path", ""),
            params.get("content", ""),
            params.get("overwrite", False)
        )
    elif operation == "read":
        return file_manager.read_file(params.get("file_path", ""))
    elif operation == "update":
        return file_manager.update_file(
            params.get("file_path", ""),
            params.get("content", "")
        )
    elif operation == "delete":
        return file_manager.delete_file(params.get("file_path", ""))
    elif operation == "list":
        return file_manager.list_files(
            params.get("directory", "."),
            params.get("pattern", "*")
        )
    else:
        return {"success": False, "error": f"Unknown file operation: {operation}"}

def process_code_analysis(code_analyzer: CodeAnalyzer, params: Dict[str, Any]) -> Dict[str, Any]:
    """Process code analysis requests"""
    return code_analyzer.analyze_code_structure(
        params.get("code", ""),
        params.get("language", "python")
    )

def process_dependency_analysis(dependency_manager: DependencyManager, params: Dict[str, Any]) -> Dict[str, Any]:
    """Process dependency analysis requests"""
    return dependency_manager.analyze_dependencies(params.get("project_path", "."))

def process_code_formatting(code_analyzer: CodeAnalyzer, params: Dict[str, Any]) -> Dict[str, Any]:
    """Process code formatting requests"""
    return code_analyzer.format_code(
        params.get("code", ""),
        params.get("language", "python")
    )

# Utility functions for other agents
def generate_file_hash(content: str) -> str:
    """Generate hash for file content"""
    return hashlib.md5(content.encode()).hexdigest()

def validate_file_path(file_path: str) -> bool:
    """Validate file path for security"""
    # Basic validation - could be enhanced
    dangerous_patterns = [
        "..",
        "~",
        "/etc",
        "/var",
        "/usr",
        "C:\\",
        "D:\\"
    ]
    
    file_path_lower = file_path.lower()
    return not any(pattern in file_path_lower for pattern in dangerous_patterns)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def create_project_structure(structure: Dict[str, Any], base_path: str = ".") -> Dict[str, Any]:
    """
    Create project directory structure.
    
    Args:
        structure: Directory structure definition
        base_path: Base path for the project
        
    Returns:
        Creation results
    """
    try:
        file_manager = FileManager(base_path)
        results = []
        
        for item_name, item_config in structure.items():
            if isinstance(item_config, dict):
                # Directory
                dir_path = item_name
                Path(base_path) / dir_path
                
                # Create subdirectories/files
                for sub_item, sub_config in item_config.items():
                    if isinstance(sub_config, str):
                        # File with content
                        file_path = f"{dir_path}/{sub_item}"
                        result = file_manager.create_file(file_path, sub_config)
                        results.append(result)
                    elif isinstance(sub_config, dict):
                        # Nested directory
                        nested_path = f"{dir_path}/{sub_item}"
                        # Recursive call for nested structure
                        nested_results = create_project_structure({sub_item: sub_config}, base_path)
                        results.extend(nested_results)
            else:
                # File with content
                result = file_manager.create_file(item_name, item_config)
                results.append(result)
        
        return {
            "success": True,
            "results": results,
            "created_items": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error creating project structure: {str(e)}")
        return {"success": False, "error": str(e)}
