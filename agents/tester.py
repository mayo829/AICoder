"""
Tester Agent

This agent is responsible for testing, validating, and deploying code. It runs tests,
checks for errors, validates code quality, and provides feedback on deployment readiness.
"""

from typing import Dict, Any, List, Optional
import logging
import subprocess
import tempfile
import os
import json
import re
from pathlib import Path
from services.llm import generate_agent_response

# Configure logging
logger = logging.getLogger(__name__)

# LLM service is imported and used via generate_agent_response function

class TestRunner:
    """Handles test execution and validation"""
    
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        self.test_results = []
    
    def run_syntax_check(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Run syntax check on the provided code.
        
        Args:
            code: Code to check
            language: Programming language
            
        Returns:
            Syntax check results
        """
        try:
            if language.lower() == "python":
                return self._check_python_syntax(code)
            elif language.lower() == "javascript":
                return self._check_javascript_syntax(code)
            elif language.lower() == "typescript":
                return self._check_typescript_syntax(code)
            else:
                return {"is_valid": True, "errors": [], "warnings": ["Language not supported for syntax checking"]}
        except Exception as e:
            logger.error(f"Error in syntax check: {str(e)}")
            return {"is_valid": False, "errors": [str(e)], "warnings": []}
    
    def _check_python_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax"""
        try:
            # Write code to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_code.py")
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run Python syntax check
            result = subprocess.run(
                ["python", "-m", "py_compile", temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "is_valid": result.returncode == 0,
                "errors": result.stderr.split('\n') if result.stderr else [],
                "warnings": []
            }
        except subprocess.TimeoutExpired:
            return {"is_valid": False, "errors": ["Syntax check timed out"], "warnings": []}
        except Exception as e:
            return {"is_valid": False, "errors": [str(e)], "warnings": []}
    
    def _check_javascript_syntax(self, code: str) -> Dict[str, Any]:
        """Check JavaScript syntax"""
        try:
            # Write code to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_code.js")
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run Node.js syntax check
            result = subprocess.run(
                ["node", "--check", temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "is_valid": result.returncode == 0,
                "errors": result.stderr.split('\n') if result.stderr else [],
                "warnings": []
            }
        except subprocess.TimeoutExpired:
            return {"is_valid": False, "errors": ["Syntax check timed out"], "warnings": []}
        except Exception as e:
            return {"is_valid": False, "errors": [str(e)], "warnings": []}
    
    def _check_typescript_syntax(self, code: str) -> Dict[str, Any]:
        """Check TypeScript syntax"""
        try:
            # Write code to temporary file
            temp_file = os.path.join(self.temp_dir, "temp_code.ts")
            with open(temp_file, 'w') as f:
                f.write(code)
            
            # Run TypeScript compiler check
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", temp_file],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            return {
                "is_valid": result.returncode == 0,
                "errors": result.stderr.split('\n') if result.stderr else [],
                "warnings": []
            }
        except subprocess.TimeoutExpired:
            return {"is_valid": False, "errors": ["Syntax check timed out"], "warnings": []}
        except Exception as e:
            return {"is_valid": False, "errors": [str(e)], "warnings": []}

def tester_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tester node that validates and tests generated code.
    
    Args:
        state: The current state containing code to test
        
    Returns:
        Updated state with testing results
    """
    try:
        # Extract relevant information from state
        generated_code = state.get("generated_code", "")
        file_structure = state.get("file_structure", {})
        requirements = state.get("requirements", "")
        language = detect_language(generated_code)
        
        # Initialize test runner
        test_runner = TestRunner()
        
        # Run comprehensive testing
        test_results = run_comprehensive_tests(test_runner, generated_code, language, requirements)
        
        # Log test results
        logger.info("🧪 Tester Raw Output:")
        logger.info("-" * 50)
        logger.info(f"Test Results: {test_results}")
        logger.info("-" * 50)
        
        # Generate test recommendations
        recommendations = generate_test_recommendations(test_results, requirements)
        
        # Update state with testing results
        updated_state = state.copy()
        updated_state["test_results"] = test_results
        updated_state["testing_status"] = "completed"
        updated_state["test_recommendations"] = recommendations
        updated_state["deployment_ready"] = test_results["overall_status"] == "pass"
        
        # Log testing summary
        logger.info("🧪 Tester Summary:")
        logger.info(f"  Overall Status: {test_results.get('overall_status', 'unknown')}")
        logger.info(f"  Score: {test_results.get('score', 0.0)}")
        logger.info(f"  Syntax Check: {test_results.get('syntax_check', {}).get('is_valid', False)}")
        logger.info(f"  Code Quality Score: {test_results.get('code_quality', {}).get('score', 0.0)}")
        logger.info(f"  Deployment Ready: {updated_state['deployment_ready']}")
        
        logger.info("✅ Testing completed successfully")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in tester node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["testing_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def run_comprehensive_tests(test_runner: TestRunner, code: str, language: str, requirements: str) -> Dict[str, Any]:
    """
    Run comprehensive tests on the generated code.
    
    Args:
        test_runner: Test runner instance
        code: Code to test
        language: Programming language
        requirements: Project requirements
        
    Returns:
        Comprehensive test results
    """
    test_results = {
        "syntax_check": {},
        "code_quality": {},
        "security_analysis": {},
        "performance_check": {},
        "deployment_check": {},
        "overall_status": "fail",
        "score": 0.0
    }
    
    try:
        # 1. Syntax Check
        test_results["syntax_check"] = test_runner.run_syntax_check(code, language)
        
        # 2. Code Quality Analysis
        test_results["code_quality"] = analyze_code_quality(code, language)
        
        # 3. Security Analysis
        test_results["security_analysis"] = analyze_security(code, language)
        
        # 4. Performance Check
        test_results["performance_check"] = check_performance(code, language)
        
        # 5. Deployment Check
        test_results["deployment_check"] = check_deployment_readiness(code, language, requirements)
        
        # Calculate overall status and score
        test_results["overall_status"], test_results["score"] = calculate_overall_status(test_results)
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error in comprehensive testing: {str(e)}")
        test_results["overall_status"] = "fail"
        test_results["error"] = str(e)
        return test_results

def detect_language(code: str) -> str:
    """
    Detect the programming language from the code.
    
    Args:
        code: Code to analyze
        
    Returns:
        Detected language
    """
    # Simple language detection based on code patterns
    if "def " in code or "import " in code or "class " in code:
        return "python"
    elif "function " in code or "const " in code or "let " in code:
        if "interface " in code or "type " in code:
            return "typescript"
        else:
            return "javascript"
    elif "public class" in code or "private " in code:
        return "java"
    else:
        return "python"  # Default

def analyze_code_quality(code: str, language: str) -> Dict[str, Any]:
    """
    Analyze code quality and provide metrics.
    
    Args:
        code: Code to analyze
        language: Programming language
        
    Returns:
        Code quality analysis results
    """
    try:
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        metrics = {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "comment_ratio": calculate_comment_ratio(lines, language),
            "function_count": count_functions(code, language),
            "complexity": calculate_complexity(code, language),
            "naming_conventions": check_naming_conventions(code, language),
            "documentation": check_documentation(code, language)
        }
        
        # Calculate quality score
        quality_score = calculate_quality_score(metrics)
        
        return {
            "metrics": metrics,
            "score": quality_score,
            "is_acceptable": quality_score >= 0.7
        }
        
    except Exception as e:
        logger.error(f"Error in code quality analysis: {str(e)}")
        return {"error": str(e), "score": 0.0, "is_acceptable": False}

def analyze_security(code: str, language: str) -> Dict[str, Any]:
    """
    Analyze code for security vulnerabilities.
    
    Args:
        code: Code to analyze
        language: Programming language
        
    Returns:
        Security analysis results
    """
    security_issues = []
    
    # Common security patterns to check
    security_patterns = {
        "sql_injection": [r"execute\s*\(\s*[\"'].*\+\s*\w+", r"query\s*\(\s*[\"'].*\+\s*\w+"],
        "xss": [r"innerHTML\s*=", r"document\.write\s*\("],
        "hardcoded_secrets": [r"password\s*=\s*[\"'][^\"']+[\"']", r"api_key\s*=\s*[\"'][^\"']+[\"']"],
        "unsafe_eval": [r"eval\s*\(", r"exec\s*\("]
    }
    
    for issue_type, patterns in security_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                security_issues.append({
                    "type": issue_type,
                    "severity": "high" if issue_type in ["sql_injection", "unsafe_eval"] else "medium",
                    "matches": matches[:3]  # Limit to first 3 matches
                })
    
    return {
        "issues": security_issues,
        "is_secure": len(security_issues) == 0,
        "risk_level": "high" if any(issue["severity"] == "high" for issue in security_issues) else "low"
    }

def check_performance(code: str, language: str) -> Dict[str, Any]:
    """
    Check code for performance issues.
    
    Args:
        code: Code to analyze
        language: Programming language
        
    Returns:
        Performance analysis results
    """
    performance_issues = []
    
    # Performance anti-patterns
    performance_patterns = {
        "nested_loops": [r"for\s*\([^)]+\)\s*\{[^}]*for\s*\([^)]+\)"],
        "inefficient_queries": [r"SELECT\s*\*\s*FROM", r"WHERE\s+1\s*=\s*1"],
        "memory_leaks": [r"setInterval\s*\(", r"addEventListener\s*\("]
    }
    
    for issue_type, patterns in performance_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                performance_issues.append({
                    "type": issue_type,
                    "severity": "medium",
                    "matches": matches[:3]
                })
    
    return {
        "issues": performance_issues,
        "is_performant": len(performance_issues) == 0,
        "optimization_needed": len(performance_issues) > 2
    }

def check_deployment_readiness(code: str, language: str, requirements: str) -> Dict[str, Any]:
    """
    Check if code is ready for deployment.
    
    Args:
        code: Code to analyze
        language: Programming language
        requirements: Project requirements
        
    Returns:
        Deployment readiness results
    """
    readiness_checks = {
        "has_main_entry": check_main_entry(code, language),
        "has_error_handling": check_error_handling(code, language),
        "has_logging": check_logging(code, language),
        "has_configuration": check_configuration(code, language),
        "meets_requirements": check_requirements_compliance(code, requirements)
    }
    
    passed_checks = sum(1 for check in readiness_checks.values() if check)
    total_checks = len(readiness_checks)
    
    return {
        "checks": readiness_checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
        "readiness_score": passed_checks / total_checks if total_checks > 0 else 0.0,
        "is_ready": passed_checks >= total_checks * 0.8  # 80% threshold
    }

def calculate_overall_status(test_results: Dict[str, Any]) -> tuple[str, float]:
    """
    Calculate overall test status and score.
    
    Args:
        test_results: All test results
        
    Returns:
        Tuple of (status, score)
    """
    scores = []
    
    # Syntax check (critical)
    if test_results["syntax_check"].get("is_valid", False):
        scores.append(1.0)
    else:
        return "fail", 0.0
    
    # Code quality (important)
    quality_score = test_results["code_quality"].get("score", 0.0)
    scores.append(quality_score)
    
    # Security (critical)
    if test_results["security_analysis"].get("is_secure", False):
        scores.append(1.0)
    else:
        scores.append(0.5)  # Partial score for security issues
    
    # Performance (important)
    if test_results["performance_check"].get("is_performant", False):
        scores.append(1.0)
    else:
        scores.append(0.7)  # Partial score for performance issues
    
    # Deployment readiness (important)
    readiness_score = test_results["deployment_check"].get("readiness_score", 0.0)
    scores.append(readiness_score)
    
    # Calculate weighted average
    weights = [0.3, 0.2, 0.25, 0.15, 0.1]  # Syntax, Quality, Security, Performance, Deployment
    final_score = sum(score * weight for score, weight in zip(scores, weights))
    
    if final_score >= 0.8:
        status = "pass"
    elif final_score >= 0.6:
        status = "warn"
    else:
        status = "fail"
    
    return status, final_score

def generate_test_recommendations(test_results: Dict[str, Any], requirements: str) -> List[str]:
    """
    Generate recommendations based on test results using LLM service.
    
    Args:
        test_results: Test results
        requirements: Project requirements
        
    Returns:
        List of recommendations
    """
    try:
        # Build context for LLM
        context = {
            "test_results": test_results,
            "requirements": requirements,
            "overall_status": test_results.get("overall_status", "fail"),
            "score": test_results.get("score", 0.0)
        }
        
        # Create prompt for LLM
        prompt = f"""
        Based on the following test results, provide specific, actionable recommendations for improving the code:
        
        Test Results Summary:
        - Overall Status: {test_results.get('overall_status', 'fail')}
        - Overall Score: {test_results.get('score', 0.0):.2f}
        - Syntax Check: {'PASS' if test_results.get('syntax_check', {}).get('is_valid', False) else 'FAIL'}
        - Code Quality Score: {test_results.get('code_quality', {}).get('score', 0.0):.2f}
        - Security Analysis: {'SECURE' if test_results.get('security_analysis', {}).get('is_secure', False) else 'INSECURE'}
        - Performance Check: {'PASS' if test_results.get('performance_check', {}).get('is_performant', False) else 'FAIL'}
        - Deployment Readiness: {test_results.get('deployment_check', {}).get('readiness_score', 0.0):.2f}
        
        Requirements: {requirements}
        
        Please provide 3-5 specific, actionable recommendations to improve the code quality, security, and deployment readiness. Focus on the most critical issues first.
        """
        
        # Generate recommendations using centralized LLM service
        llm_response = generate_agent_response("tester", prompt, context=context)
        
        # Parse the response into a list of recommendations
        recommendations = parse_recommendations(llm_response)
        
        # Add fallback recommendations if LLM fails
        if not recommendations:
            recommendations = generate_fallback_recommendations(test_results)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating LLM recommendations: {str(e)}")
        # Fallback to basic recommendations
        return generate_fallback_recommendations(test_results)

def parse_recommendations(llm_response: str) -> List[str]:
    """
    Parse LLM response into structured recommendations.
    
    Args:
        llm_response: Raw response from LLM
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Split by common list indicators
    lines = llm_response.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove common list prefixes
        for prefix in ['- ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '• ']:
            if line.startswith(prefix):
                line = line[len(prefix):]
                break
        
        # Add non-empty recommendations
        if line and len(line) > 10:  # Minimum meaningful length
            recommendations.append(line)
    
    return recommendations[:5]  # Limit to 5 recommendations

def generate_fallback_recommendations(test_results: Dict[str, Any]) -> List[str]:
    """
    Generate basic recommendations as fallback.
    
    Args:
        test_results: Test results
        
    Returns:
        List of basic recommendations
    """
    recommendations = []
    
    # Syntax issues
    if not test_results["syntax_check"].get("is_valid", False):
        recommendations.append("Fix syntax errors before proceeding")
    
    # Code quality issues
    quality_score = test_results["code_quality"].get("score", 0.0)
    if quality_score < 0.7:
        recommendations.append("Improve code quality and documentation")
    
    # Security issues
    if not test_results["security_analysis"].get("is_secure", False):
        recommendations.append("Address security vulnerabilities")
    
    # Performance issues
    if test_results["performance_check"].get("optimization_needed", False):
        recommendations.append("Optimize code for better performance")
    
    # Deployment readiness
    readiness_score = test_results["deployment_check"].get("readiness_score", 0.0)
    if readiness_score < 0.8:
        recommendations.append("Add missing deployment requirements")
    
    return recommendations

# Helper functions for code analysis
def calculate_comment_ratio(lines: List[str], language: str) -> float:
    """Calculate comment to code ratio"""
    comment_lines = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            comment_lines += 1
    return comment_lines / len(lines) if lines else 0.0

def count_functions(code: str, language: str) -> int:
    """Count number of functions"""
    if language == "python":
        return len(re.findall(r'def\s+\w+', code))
    elif language in ["javascript", "typescript"]:
        return len(re.findall(r'function\s+\w+|const\s+\w+\s*=|let\s+\w+\s*=', code))
    return 0

def calculate_complexity(code: str, language: str) -> int:
    """Calculate cyclomatic complexity"""
    complexity = 1  # Base complexity
    complexity += len(re.findall(r'\bif\b|\bwhile\b|\bfor\b|\band\b|\bor\b', code))
    return complexity

def check_naming_conventions(code: str, language: str) -> bool:
    """Check if code follows naming conventions"""
    # Simple check for snake_case in Python, camelCase in JS
    if language == "python":
        return not re.search(r'[A-Z][a-z]+[A-Z]', code)  # No camelCase
    elif language in ["javascript", "typescript"]:
        return not re.search(r'[a-z]+_[a-z]+', code)  # No snake_case
    return True

def check_documentation(code: str, language: str) -> bool:
    """Check if code has adequate documentation"""
    doc_patterns = {
        "python": r'""".*"""|\'\'\'.*?\'\'\'',
        "javascript": r'/\*\*.*?\*/|//.*',
        "typescript": r'/\*\*.*?\*/|//.*'
    }
    pattern = doc_patterns.get(language, r'//.*|/\*.*?\*/')
    return bool(re.search(pattern, code, re.DOTALL))

def calculate_quality_score(metrics: Dict[str, Any]) -> float:
    """Calculate overall quality score"""
    scores = []
    
    # Comment ratio (target: 0.1-0.3)
    comment_ratio = metrics["comment_ratio"]
    if 0.1 <= comment_ratio <= 0.3:
        scores.append(1.0)
    elif comment_ratio > 0:
        scores.append(0.5)
    else:
        scores.append(0.0)
    
    # Function count (target: > 0)
    if metrics["function_count"] > 0:
        scores.append(1.0)
    else:
        scores.append(0.0)
    
    # Complexity (target: < 10)
    if metrics["complexity"] < 10:
        scores.append(1.0)
    elif metrics["complexity"] < 20:
        scores.append(0.5)
    else:
        scores.append(0.0)
    
    # Naming conventions
    scores.append(1.0 if metrics["naming_conventions"] else 0.0)
    
    # Documentation
    scores.append(1.0 if metrics["documentation"] else 0.0)
    
    return sum(scores) / len(scores) if scores else 0.0

def check_main_entry(code: str, language: str) -> bool:
    """Check if code has a main entry point"""
    patterns = {
        "python": r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        "javascript": r'function\s+main|const\s+main|let\s+main',
        "typescript": r'function\s+main|const\s+main|let\s+main'
    }
    pattern = patterns.get(language, r'')
    return bool(re.search(pattern, code, re.IGNORECASE))

def check_error_handling(code: str, language: str) -> bool:
    """Check if code has error handling"""
    patterns = {
        "python": r'try:|except:|raise\s+',
        "javascript": r'try\s*\{|catch\s*\(|throw\s+',
        "typescript": r'try\s*\{|catch\s*\(|throw\s+'
    }
    pattern = patterns.get(language, r'')
    return bool(re.search(pattern, code, re.IGNORECASE))

def check_logging(code: str, language: str) -> bool:
    """Check if code has logging"""
    patterns = {
        "python": r'logging\.|print\s*\(',
        "javascript": r'console\.|logger\.',
        "typescript": r'console\.|logger\.'
    }
    pattern = patterns.get(language, r'')
    return bool(re.search(pattern, code, re.IGNORECASE))

def check_configuration(code: str, language: str) -> bool:
    """Check if code has configuration handling"""
    patterns = {
        "python": r'config|settings|env|\.env',
        "javascript": r'config|settings|env|process\.env',
        "typescript": r'config|settings|env|process\.env'
    }
    pattern = patterns.get(language, r'')
    return bool(re.search(pattern, code, re.IGNORECASE))

def check_requirements_compliance(code: str, requirements: str) -> bool:
    """Check if code meets the specified requirements"""
    # Simple keyword matching - could be enhanced with more sophisticated analysis
    requirement_words = set(requirements.lower().split())
    code_words = set(code.lower().split())
    overlap = len(requirement_words.intersection(code_words))
    return overlap > 0  # At least some overlap