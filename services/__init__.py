"""
Services Module

Centralized services for the AICoder multi-agent system.
Provides LLM service management and other utility services.
"""

from .llm import (
    LLMServiceManager,
    LLMProvider,
    LLMConfig,
    BaseLLMService,
    OpenAIService,
    AnthropicService,
    get_llm_service,
    generate_response,
    generate_agent_response,
    llm_manager
)

__all__ = [
    # LLM Service Classes
    "LLMServiceManager",
    "LLMProvider", 
    "LLMConfig",
    "BaseLLMService",
    "OpenAIService",
    "AnthropicService",
    
    # Convenience Functions
    "get_llm_service",
    "generate_response", 
    "generate_agent_response",
    
    # Global Instance
    "llm_manager"
]

# Version info
__version__ = "1.0.0"
