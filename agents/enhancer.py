"""
Enhancer Agent

This agent is responsible for enhancing user prompts and user-in-loop interactions
to ensure the correct prompt is sent to other agents. It improves clarity, adds
context, and optimizes prompts for better results.
"""

from typing import Dict, Any, List, Optional
import logging
import re
import json
from datetime import datetime
from services.llm import generate_agent_response

# Configure logging
logger = logging.getLogger(__name__)

# LLM service is imported and used via generate_agent_response function

class PromptEnhancer:
    """Handles prompt enhancement and optimization"""
    
    def __init__(self):
        self.enhancement_history = []
        self.common_patterns = {
            "vague_requests": [
                r"make it better",
                r"improve this",
                r"fix it",
                r"do something"
            ],
            "missing_context": [
                r"create a (.*?)",
                r"build a (.*?)",
                r"make a (.*?)"
            ],
            "ambiguous_requirements": [
                r"it should work",
                r"make it functional",
                r"add features"
            ]
        }
    
    def enhance_prompt(self, original_prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance the original prompt with better clarity and context.
        
        Args:
            original_prompt: Original user prompt
            context: Additional context information
            
        Returns:
            Enhanced prompt information
        """
        try:
            # Analyze the original prompt
            analysis = self.analyze_prompt(original_prompt)
            
            # Generate enhanced prompt
            enhanced_prompt = self.generate_enhanced_prompt(original_prompt, analysis, context)
            
            # Validate the enhancement
            validation = self.validate_enhancement(original_prompt, enhanced_prompt)
            
            return {
                "original_prompt": original_prompt,
                "enhanced_prompt": enhanced_prompt,
                "analysis": analysis,
                "validation": validation,
                "enhancement_score": self.calculate_enhancement_score(analysis, validation),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return {
                "original_prompt": original_prompt,
                "enhanced_prompt": original_prompt,
                "error": str(e),
                "enhancement_score": 0.0
            }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze the prompt for clarity, completeness, and potential issues.
        
        Args:
            prompt: Prompt to analyze
            
        Returns:
            Analysis results
        """
        analysis = {
            "clarity_score": 0.0,
            "completeness_score": 0.0,
            "specificity_score": 0.0,
            "issues": [],
            "suggestions": [],
            "detected_intent": "",
            "required_context": []
        }
        
        # Check for vague requests
        for pattern in self.common_patterns["vague_requests"]:
            if re.search(pattern, prompt, re.IGNORECASE):
                analysis["issues"].append("Vague request detected")
                analysis["suggestions"].append("Provide more specific requirements")
                analysis["clarity_score"] -= 0.2
        
        # Check for missing context
        for pattern in self.common_patterns["missing_context"]:
            if re.search(pattern, prompt, re.IGNORECASE):
                analysis["issues"].append("Missing context detected")
                analysis["suggestions"].append("Specify technology stack, requirements, and constraints")
                analysis["completeness_score"] -= 0.2
        
        # Check for ambiguous requirements
        for pattern in self.common_patterns["ambiguous_requirements"]:
            if re.search(pattern, prompt, re.IGNORECASE):
                analysis["issues"].append("Ambiguous requirements detected")
                analysis["suggestions"].append("Define specific functionality and success criteria")
                analysis["specificity_score"] -= 0.2
        
        # Detect intent
        analysis["detected_intent"] = self.detect_intent(prompt)
        
        # Identify required context
        analysis["required_context"] = self.identify_required_context(prompt)
        
        # Calculate scores (normalize to 0-1 range)
        analysis["clarity_score"] = max(0.0, min(1.0, 0.5 + analysis["clarity_score"]))
        analysis["completeness_score"] = max(0.0, min(1.0, 0.5 + analysis["completeness_score"]))
        analysis["specificity_score"] = max(0.0, min(1.0, 0.5 + analysis["specificity_score"]))
        
        return analysis
    
    def generate_enhanced_prompt(self, original_prompt: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate an enhanced version of the original prompt.
        
        Args:
            original_prompt: Original prompt
            analysis: Prompt analysis results
            context: Additional context
            
        Returns:
            Enhanced prompt
        """
        try:
            # Build enhancement prompt for LLM
            enhancement_prompt = f"""
            Original user prompt: {original_prompt}
            
            Analysis:
            - Clarity score: {analysis['clarity_score']:.2f}
            - Completeness score: {analysis['completeness_score']:.2f}
            - Specificity score: {analysis['specificity_score']:.2f}
            - Detected intent: {analysis['detected_intent']}
            - Issues: {', '.join(analysis['issues'])}
            - Required context: {', '.join(analysis['required_context'])}
            
            Available context: {json.dumps(context, indent=2)}
            
            Please enhance this prompt by:
            1. Adding missing context and specifications
            2. Clarifying ambiguous requirements
            3. Making the request more specific and actionable
            4. Including relevant technical details
            5. Adding success criteria and constraints
            
            Return only the enhanced prompt without explanations.
            """
            
            # Generate enhanced prompt using centralized LLM service
            enhanced_prompt = generate_agent_response("enhancer", enhancement_prompt).strip()
            
            # Fallback if LLM fails
            if not enhanced_prompt or enhanced_prompt == original_prompt:
                enhanced_prompt = self.fallback_enhancement(original_prompt, analysis, context)
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error generating enhanced prompt: {str(e)}")
            return self.fallback_enhancement(original_prompt, analysis, context)
    
    def fallback_enhancement(self, original_prompt: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Fallback enhancement method when LLM fails.
        
        Args:
            original_prompt: Original prompt
            analysis: Prompt analysis
            context: Additional context
            
        Returns:
            Enhanced prompt
        """
        enhanced_parts = [original_prompt]
        
        # Add context if available
        if context.get("project_type"):
            enhanced_parts.append(f"Project type: {context['project_type']}")
        
        if context.get("technology_stack"):
            enhanced_parts.append(f"Technology stack: {context['technology_stack']}")
        
        if context.get("requirements"):
            enhanced_parts.append(f"Requirements: {context['requirements']}")
        
        # Add suggestions based on analysis
        if analysis["issues"]:
            enhanced_parts.append(f"Please address: {', '.join(analysis['suggestions'])}")
        
        return "\n\n".join(enhanced_parts)
    
    def validate_enhancement(self, original_prompt: str, enhanced_prompt: str) -> Dict[str, Any]:
        """
        Validate the enhancement quality.
        
        Args:
            original_prompt: Original prompt
            enhanced_prompt: Enhanced prompt
            
        Returns:
            Validation results
        """
        validation = {
            "is_improved": False,
            "improvement_score": 0.0,
            "preserves_intent": True,
            "adds_value": False,
            "issues": []
        }
        
        try:
            # Check if enhancement adds value
            original_length = len(original_prompt.split())
            enhanced_length = len(enhanced_prompt.split())
            
            if enhanced_length > original_length:
                validation["adds_value"] = True
                validation["improvement_score"] += 0.3
            
            # Check if it preserves original intent
            original_keywords = set(re.findall(r'\b\w+\b', original_prompt.lower()))
            enhanced_keywords = set(re.findall(r'\b\w+\b', enhanced_prompt.lower()))
            
            keyword_overlap = len(original_keywords.intersection(enhanced_keywords)) / len(original_keywords) if original_keywords else 0
            if keyword_overlap > 0.7:
                validation["preserves_intent"] = True
                validation["improvement_score"] += 0.4
            
            # Check for specific improvements
            improvements = 0
            if "technology" in enhanced_prompt.lower():
                improvements += 1
            if "requirements" in enhanced_prompt.lower():
                improvements += 1
            if "constraints" in enhanced_prompt.lower():
                improvements += 1
            if "success criteria" in enhanced_prompt.lower():
                improvements += 1
            
            validation["improvement_score"] += improvements * 0.1
            
            # Determine if overall improvement
            validation["is_improved"] = validation["improvement_score"] > 0.5
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating enhancement: {str(e)}")
            validation["issues"].append(str(e))
            return validation
    
    def calculate_enhancement_score(self, analysis: Dict[str, Any], validation: Dict[str, Any]) -> float:
        """
        Calculate overall enhancement score.
        
        Args:
            analysis: Prompt analysis
            validation: Enhancement validation
            
        Returns:
            Enhancement score (0.0 to 1.0)
        """
        try:
            # Weighted average of various scores
            scores = [
                analysis["clarity_score"] * 0.3,
                analysis["completeness_score"] * 0.3,
                analysis["specificity_score"] * 0.2,
                validation["improvement_score"] * 0.2
            ]
            
            return sum(scores)
            
        except Exception as e:
            logger.error(f"Error calculating enhancement score: {str(e)}")
            return 0.0
    
    def detect_intent(self, prompt: str) -> str:
        """
        Detect the user's intent from the prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            Detected intent
        """
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["create", "build", "make", "develop"]):
            return "creation"
        elif any(word in prompt_lower for word in ["fix", "debug", "error", "issue"]):
            return "debugging"
        elif any(word in prompt_lower for word in ["improve", "enhance", "optimize", "better"]):
            return "improvement"
        elif any(word in prompt_lower for word in ["test", "validate", "check"]):
            return "testing"
        elif any(word in prompt_lower for word in ["deploy", "release", "publish"]):
            return "deployment"
        else:
            return "general"
    
    def identify_required_context(self, prompt: str) -> List[str]:
        """
        Identify context that should be added to the prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            List of required context items
        """
        required_context = []
        prompt_lower = prompt.lower()
        
        if "create" in prompt_lower or "build" in prompt_lower:
            required_context.extend(["technology_stack", "requirements", "constraints"])
        
        if "api" in prompt_lower:
            required_context.extend(["endpoints", "data_format", "authentication"])
        
        if "database" in prompt_lower:
            required_context.extend(["database_type", "schema", "relationships"])
        
        if "frontend" in prompt_lower or "ui" in prompt_lower:
            required_context.extend(["design_preferences", "framework", "responsive"])
        
        if "test" in prompt_lower:
            required_context.extend(["test_type", "coverage", "framework"])
        
        return list(set(required_context))

def enhancer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhancer node that improves user prompts and interactions.
    
    Args:
        state: The current state containing user input and context
        
    Returns:
        Updated state with enhanced prompts
    """
    try:
        # Extract relevant information from state
        user_input = state.get("user_input", "")
        context = state.get("context", "")
        memory_context = state.get("memory_context", [])
        project_info = state.get("project_info", {})
        
        # Initialize prompt enhancer
        enhancer = PromptEnhancer()
        
        # Build comprehensive context
        full_context = {
            "context": context,
            "memory_context": memory_context,
            "project_info": project_info,
            "workflow_status": state.get("workflow_status", ""),
            "agent_results": state.get("agent_results", {})
        }
        
        # Enhance the user prompt
        enhancement_result = enhancer.enhance_prompt(user_input, full_context)
        
        # Generate interaction suggestions
        interaction_suggestions = generate_interaction_suggestions(enhancement_result, state)
        
        # Update state with enhancement results
        updated_state = state.copy()
        updated_state["enhanced_prompt"] = enhancement_result["enhanced_prompt"]
        updated_state["prompt_analysis"] = enhancement_result["analysis"]
        updated_state["enhancement_validation"] = enhancement_result["validation"]
        updated_state["enhancement_score"] = enhancement_result["enhancement_score"]
        updated_state["interaction_suggestions"] = interaction_suggestions
        updated_state["enhancement_status"] = "completed"
        
        # Update user input with enhanced version if significantly improved
        if enhancement_result["enhancement_score"] > 0.7:
            updated_state["user_input"] = enhancement_result["enhanced_prompt"]
            updated_state["prompt_enhanced"] = True
        else:
            updated_state["prompt_enhanced"] = False
        
        logger.info("Prompt enhancement completed successfully")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in enhancer node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["enhancement_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def generate_interaction_suggestions(enhancement_result: Dict[str, Any], state: Dict[str, Any]) -> List[str]:
    """
    Generate suggestions for improving user interactions.
    
    Args:
        enhancement_result: Enhancement results
        state: Current state
        
    Returns:
        List of interaction suggestions
    """
    suggestions = []
    
    # Based on enhancement score
    enhancement_score = enhancement_result.get("enhancement_score", 0.0)
    if enhancement_score < 0.5:
        suggestions.append("Consider providing more specific requirements and constraints")
        suggestions.append("Include technology stack preferences if applicable")
    
    # Based on analysis issues
    analysis = enhancement_result.get("analysis", {})
    issues = analysis.get("issues", [])
    
    if "Vague request detected" in issues:
        suggestions.append("Be more specific about what you want to achieve")
    
    if "Missing context detected" in issues:
        suggestions.append("Provide context about your project and requirements")
    
    if "Ambiguous requirements detected" in issues:
        suggestions.append("Define clear success criteria and constraints")
    
    # Based on workflow status
    workflow_status = state.get("workflow_status", "")
    if workflow_status == "planning":
        suggestions.append("Consider providing project scope and timeline")
    elif workflow_status == "coding":
        suggestions.append("Specify coding standards and preferences")
    elif workflow_status == "testing":
        suggestions.append("Define testing requirements and coverage expectations")
    
    return suggestions

def improve_user_feedback(user_feedback: str, context: Dict[str, Any]) -> str:
    """
    Improve user feedback for better agent understanding.
    
    Args:
        user_feedback: Original user feedback
        context: Context information
        
    Returns:
        Improved feedback
    """
    try:
        improvement_prompt = f"""
        User feedback: {user_feedback}
        
        Context: {json.dumps(context, indent=2)}
        
        Please improve this feedback by:
        1. Making it more specific and actionable
        2. Adding context about what was expected vs what was received
        3. Providing clear next steps or requirements
        4. Using technical terminology appropriately
        
        Return only the improved feedback.
        """
        
        return generate_agent_response("enhancer", improvement_prompt).strip()
        
    except Exception as e:
        logger.error(f"Error improving user feedback: {str(e)}")
        return user_feedback

def validate_user_input(user_input: str) -> Dict[str, Any]:
    """
    Validate user input for completeness and clarity.
    
    Args:
        user_input: User input to validate
        
    Returns:
        Validation results
    """
    validation = {
        "is_valid": True,
        "issues": [],
        "suggestions": [],
        "confidence": 0.0
    }
    
    # Check for minimum length
    if len(user_input.strip()) < 10:
        validation["is_valid"] = False
        validation["issues"].append("Input too short")
        validation["suggestions"].append("Provide more details about your request")
    
    # Check for question marks (indicating questions)
    if "?" in user_input:
        validation["confidence"] += 0.2
    
    # Check for technical terms
    technical_terms = ["api", "database", "frontend", "backend", "test", "deploy", "config"]
    found_terms = sum(1 for term in technical_terms if term in user_input.lower())
    validation["confidence"] += found_terms * 0.1
    
    # Check for action verbs
    action_verbs = ["create", "build", "make", "fix", "improve", "test", "deploy"]
    found_verbs = sum(1 for verb in action_verbs if verb in user_input.lower())
    validation["confidence"] += found_verbs * 0.1
    
    validation["confidence"] = min(validation["confidence"], 1.0)
    
    return validation