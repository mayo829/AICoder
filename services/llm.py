"""
LLM Service

Centralized language model service for the AICoder multi-agent system.
Provides a unified interface for all agents to interact with ChatGPT and Claude.
"""

from typing import Dict, Any, List, Optional, Union
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import logging
import os
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

@dataclass
class LLMConfig:
    """Configuration for LLM instances"""
    provider: LLMProvider
    model: str
    temperature: float = 0.1
    max_tokens: int = 4000
    base_url: Optional[str] = None
    timeout: int = 30

class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    def generate_response(self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]], **kwargs) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        pass

class OpenAIService(BaseLLMService):
    """OpenAI LLM service implementation"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=config.api_key or os.getenv("OPENAI_API_KEY"),
            base_url=config.base_url,
            timeout=config.timeout
        )
    
    def generate_response(self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]], **kwargs) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.llm.invoke(messages, **kwargs)
            return response.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

class AnthropicService(BaseLLMService):
    """Anthropic LLM service implementation"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = ChatAnthropic(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            timeout=config.timeout
        )
    
    def generate_response(self, messages: List[Union[HumanMessage, AIMessage, SystemMessage]], **kwargs) -> str:
        """Generate response using Anthropic"""
        try:
            response = self.llm.invoke(messages, **kwargs)
            return response.content
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information"""
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }

class LLMServiceManager:
    """
    Centralized LLM service manager for the AICoder system.
    
    Provides a unified interface for all agents to interact with ChatGPT and Claude,
    with support for configurations and fallback strategies.
    """
    
    def __init__(self):
        self.services: Dict[str, BaseLLMService] = {}
        self.default_service: Optional[str] = None
        self.fallback_chain: List[str] = []
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """Initialize ChatGPT and Claude services based on environment"""
        try:
            # Try OpenAI first
            if os.getenv("OPENAI_API_KEY"):
                openai_config = LLMConfig(
                    provider=LLMProvider.OPENAI,
                    model="gpt-4-turbo-preview",
                    temperature=0.1,
                    max_tokens=4000
                )
                self.add_service("openai", OpenAIService(openai_config))
                self.default_service = "openai"
                self.fallback_chain.append("openai")
            
            # Try Claude as fallback
            if os.getenv("ANTHROPIC_API_KEY"):
                anthropic_config = LLMConfig(
                    provider=LLMProvider.ANTHROPIC,
                    model="claude-3-sonnet-20240229",
                    temperature=0.1,
                    max_tokens=4000
                )
                self.add_service("anthropic", AnthropicService(anthropic_config))
                if not self.default_service:
                    self.default_service = "anthropic"
                self.fallback_chain.append("anthropic")
            

            
            if not self.default_service:
                logger.warning("No LLM services configured. Please set up API keys.")
                
        except Exception as e:
            logger.error(f"Error initializing LLM services: {str(e)}")
    
    def add_service(self, name: str, service: BaseLLMService):
        """Add a new LLM service"""
        self.services[name] = service
        logger.info(f"Added LLM service: {name}")
    
    def get_service(self, name: Optional[str] = None) -> Optional[BaseLLMService]:
        """Get a specific LLM service by name"""
        service_name = name or self.default_service
        return self.services.get(service_name)
    
    def generate_response(self, 
                         prompt: str, 
                         system_message: Optional[str] = None,
                         service_name: Optional[str] = None,
                         **kwargs) -> str:
        """
        Generate a response using the specified or default LLM service.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message
            service_name: Specific service to use
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Generated response
        """
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        messages.append(HumanMessage(content=prompt))
        
        # Try the specified service first
        if service_name:
            service = self.get_service(service_name)
            if service:
                try:
                    return service.generate_response(messages, **kwargs)
                except Exception as e:
                    logger.warning(f"Service {service_name} failed: {str(e)}")
        
        # Try fallback chain
        for fallback_service in self.fallback_chain:
            if fallback_service != service_name:  # Don't retry the same service
                try:
                    service = self.get_service(fallback_service)
                    if service:
                        return service.generate_response(messages, **kwargs)
                except Exception as e:
                    logger.warning(f"Fallback service {fallback_service} failed: {str(e)}")
                    continue
        
        # If all services fail, return error message
        error_msg = "All LLM services are currently unavailable. Please check your API keys and network connection."
        logger.error(error_msg)
        return error_msg
    
    def generate_agent_response(self, 
                               agent_name: str,
                               prompt: str,
                               context: Optional[Dict[str, Any]] = None,
                               **kwargs) -> str:
        """
        Generate a response optimized for a specific agent.
        
        Args:
            agent_name: Name of the agent making the request
            prompt: The prompt for the agent
            context: Additional context for the agent
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        # Agent-specific system messages optimized for ChatGPT and Claude
        agent_system_messages = {
            "enhancer": "You are an expert at enhancing user prompts and improving user interactions. Focus on clarity, completeness, and actionable improvements. Use ChatGPT/Claude's strengths in understanding context and providing detailed responses.",
            "planner": "You are an expert software architect and project planner. Create comprehensive, well-structured plans that follow best practices. Leverage ChatGPT/Claude's analytical capabilities for thorough planning.",
            "coder": "You are an expert software developer. Generate high-quality, production-ready code that follows best practices and design patterns. Use ChatGPT/Claude's code generation and analysis capabilities effectively.",
            "tester": "You are an expert in software testing and quality assurance. Provide thorough analysis and actionable recommendations. Utilize ChatGPT/Claude's attention to detail for comprehensive testing strategies.",
            "memory": "You are an expert at managing and retrieving contextual information. Focus on relevance and usefulness. Use ChatGPT/Claude's memory and context retention capabilities.",
            "orchestrator": "You are an expert at coordinating workflows and managing system state. Focus on efficiency and reliability. Leverage ChatGPT/Claude's reasoning abilities for optimal coordination.",
            "toolbox": "You are an expert at providing utility functions and development tools. Focus on practicality and reusability. Use ChatGPT/Claude's knowledge base for effective tool recommendations."
        }
        
        system_message = agent_system_messages.get(agent_name, "You are a helpful AI assistant.")
        
        # Add context to system message if provided
        if context:
            context_str = json.dumps(context, indent=2)
            system_message += f"\n\nContext: {context_str}"
        
        return self.generate_response(prompt, system_message, **kwargs)
    
    def get_available_services(self) -> List[Dict[str, Any]]:
        """Get information about all available services"""
        services_info = []
        for name, service in self.services.items():
            try:
                info = service.get_model_info()
                info["name"] = name
                info["status"] = "available"
                services_info.append(info)
            except Exception as e:
                services_info.append({
                    "name": name,
                    "status": "error",
                    "error": str(e)
                })
        return services_info
    
    def test_service(self, service_name: str) -> Dict[str, Any]:
        """Test a specific LLM service"""
        service = self.get_service(service_name)
        if not service:
            return {"status": "error", "message": f"Service {service_name} not found"}
        
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'Test successful' if you can see this."
            response = service.generate_response([HumanMessage(content=test_prompt)])
            
            return {
                "status": "success",
                "response": response,
                "service_info": service.get_model_info()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "service_info": service.get_model_info()
            }

# Global LLM service manager instance
llm_manager = LLMServiceManager()

def get_llm_service() -> LLMServiceManager:
    """Get the global LLM service manager"""
    return llm_manager

def generate_response(prompt: str, **kwargs) -> str:
    """Convenience function to generate a response"""
    return llm_manager.generate_response(prompt, **kwargs)

def generate_agent_response(agent_name: str, prompt: str, **kwargs) -> str:
    """Convenience function to generate an agent-specific response"""
    return llm_manager.generate_agent_response(agent_name, prompt, **kwargs)
