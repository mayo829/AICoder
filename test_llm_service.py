#!/usr/bin/env python3
"""
Test script for the centralized LLM service.

This script demonstrates the benefits of using the centralized LLM service
instead of direct ChatGPT integration in each agent.
"""

import os
import sys
from services.llm import get_llm_service, generate_agent_response, generate_response

def test_llm_service():
    """Test the LLM service functionality"""
    print("🧪 Testing AICoder LLM Service")
    print("=" * 50)
    
    # Get the LLM service manager
    llm_manager = get_llm_service()
    
    # Test 1: Check available services
    print("\n1. Available LLM Services:")
    services = llm_manager.get_available_services()
    for service in services:
        print(f"   - {service['name']}: {service['status']}")
        if service['status'] == 'available':
            print(f"     Model: {service.get('model', 'Unknown')}")
            print(f"     Provider: {service.get('provider', 'Unknown')}")
    
    # Test 2: Test basic response generation
    print("\n2. Testing Basic Response Generation:")
    test_prompt = "What is the capital of France?"
    try:
        response = generate_response(test_prompt)
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Test agent-specific responses
    print("\n3. Testing Agent-Specific Responses:")
    agents = ["enhancer", "planner", "coder", "tester", "memory", "orchestrator", "toolbox"]
    
    for agent in agents:
        print(f"\n   Testing {agent} agent:")
        agent_prompt = f"Hello, I'm the {agent} agent. What should I focus on?"
        try:
            response = generate_agent_response(agent, agent_prompt)
            print(f"   Response: {response[:80]}...")
        except Exception as e:
            print(f"   Error: {str(e)}")
    
    # Test 4: Test service fallback (if multiple services available)
    print("\n4. Testing Service Fallback:")
    if len(services) > 1:
        print("   Multiple services available - testing fallback mechanism")
        # This would be tested in a real scenario where one service fails
        print("   Fallback chain:", llm_manager.fallback_chain)
    else:
        print("   Only one service available - fallback not needed")
    
    print("\n✅ LLM Service Test Complete!")

def demonstrate_benefits():
    """Demonstrate the benefits of centralized LLM service"""
    print("\n🎯 Benefits of Centralized LLM Service")
    print("=" * 50)
    
    benefits = [
        {
            "title": "Modularity",
            "description": "All LLM interactions go through a single service",
            "advantages": [
                "Easy to change LLM providers",
                "Consistent interface across all agents",
                "Centralized configuration management"
            ]
        },
        {
            "title": "Scalability",
            "description": "Support for multiple LLM providers and fallback strategies",
            "advantages": [
                "Automatic fallback if one service fails",
                "Load balancing across multiple providers",
                "Easy to add new LLM providers"
            ]
        },
        {
            "title": "Maintainability",
            "description": "Single point of maintenance for LLM-related code",
            "advantages": [
                "Bug fixes apply to all agents",
                "Feature updates benefit entire system",
                "Easier testing and debugging"
            ]
        },
        {
            "title": "Cost Management",
            "description": "Centralized control over LLM usage and costs",
            "advantages": [
                "Monitor usage across all agents",
                "Implement rate limiting and quotas",
                "Optimize for cost vs performance"
            ]
        },
        {
            "title": "Agent Specialization",
            "description": "Agent-specific system messages and optimizations",
            "advantages": [
                "Tailored responses for each agent type",
                "Context-aware prompting",
                "Better performance for specific tasks"
            ]
        }
    ]
    
    for benefit in benefits:
        print(f"\n📋 {benefit['title']}")
        print(f"   {benefit['description']}")
        print("   Advantages:")
        for advantage in benefit['advantages']:
            print(f"   - {advantage}")

def show_usage_examples():
    """Show usage examples for the LLM service"""
    print("\n💡 Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "scenario": "Basic response generation",
            "code": """
from services.llm import generate_response

response = generate_response("What is Python?")
print(response)
            """,
            "use_case": "Simple text generation"
        },
        {
            "scenario": "Agent-specific response",
            "code": """
from services.llm import generate_agent_response

# For the coder agent
code_response = generate_agent_response("coder", "Create a Python function to calculate factorial")

# For the planner agent  
plan_response = generate_agent_response("planner", "Plan a web application architecture")
            """,
            "use_case": "Agent-optimized responses"
        },
        {
            "scenario": "Service management",
            "code": """
from services.llm import get_llm_service

llm_manager = get_llm_service()
services = llm_manager.get_available_services()
test_result = llm_manager.test_service("openai")
            """,
            "use_case": "Service monitoring and testing"
        }
    ]
    
    for example in examples:
        print(f"\n🔧 {example['scenario']}")
        print(f"   Use case: {example['use_case']}")
        print("   Code:")
        print(example['code'])

if __name__ == "__main__":
    print("🚀 AICoder LLM Service Demonstration")
    print("=" * 60)
    
    # Check if API keys are set
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY")
    }
    
    print("\n🔑 API Key Status:")
    for provider, key in api_keys.items():
        status = "✅ Set" if key else "❌ Not set"
        print(f"   {provider}: {status}")
    
    if not any(api_keys.values()):
        print("\n⚠️  No API keys found. Please set at least one of:")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY") 
        print("   - GOOGLE_API_KEY")
        print("\n   Example: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Run tests and demonstrations
    test_llm_service()
    demonstrate_benefits()
    show_usage_examples()
    
    print("\n🎉 Demonstration Complete!")
    print("\nThe centralized LLM service provides better modularity, scalability,")
    print("and maintainability compared to direct ChatGPT integration in each agent.") 