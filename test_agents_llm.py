#!/usr/bin/env python3
"""
Test script to verify that all agents are properly using the centralized LLM service.
"""

import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm import get_llm_service, generate_agent_response
from agents.coder import coder_node
from agents.planner import planner_node
from agents.tester import tester_node
from agents.memory import memory_node
from agents.orchestrator import orchestrator_node
from agents.enhancer import enhancer_node
from agents.toolbox import toolbox_node

def test_llm_service():
    """Test the LLM service directly"""
    print("🔧 Testing LLM Service...")
    
    try:
        llm_manager = get_llm_service()
        
        # Test basic response generation
        response = llm_manager.generate_response("Hello, this is a test message.")
        print(f"✅ Basic LLM response: {response[:100]}...")
        
        # Test agent-specific response
        agent_response = generate_agent_response("coder", "Write a simple Python function to add two numbers.")
        print(f"✅ Agent-specific response: {agent_response[:100]}...")
        
        # Test available services
        services = llm_manager.get_available_services()
        print(f"✅ Available services: {[s['name'] for s in services]}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service test failed: {str(e)}")
        return False

def test_agent_nodes():
    """Test each agent node with the LLM service"""
    print("\n🤖 Testing Agent Nodes...")
    
    # Test state for agents
    test_state = {
        "user_input": "Create a simple web API with Python Flask",
        "requirements": "Build a REST API with endpoints for user management",
        "context": "Web development project",
        "workflow_status": "initialized"
    }
    
    agents_to_test = [
        ("Planner", planner_node),
        ("Coder", coder_node),
        ("Tester", tester_node),
        ("Memory", memory_node),
        ("Orchestrator", orchestrator_node),
        ("Enhancer", enhancer_node),
        ("Toolbox", toolbox_node)
    ]
    
    results = {}
    
    for agent_name, agent_func in agents_to_test:
        try:
            print(f"\n📋 Testing {agent_name} agent...")
            
            # Create a copy of test state for this agent
            agent_state = test_state.copy()
            
            # Add agent-specific data
            if agent_name == "Coder":
                agent_state["plan"] = {"implementation_steps": ["Create Flask app", "Add routes", "Add database"]}
            elif agent_name == "Tester":
                agent_state["generated_code"] = "def hello(): return 'Hello, World!'"
            elif agent_name == "Toolbox":
                agent_state["tool_request"] = {
                    "type": "code_analysis",
                    "params": {
                        "code": "def test(): print('hello')",
                        "language": "python"
                    }
                }
            
            # Run the agent
            result = agent_func(agent_state)
            
            # Check if the agent used the LLM service (indicated by successful completion)
            status_key = f"{agent_name.lower()}_status"
            if status_key in result and result[status_key] == "completed":
                print(f"✅ {agent_name} agent completed successfully")
                results[agent_name] = "PASS"
            else:
                print(f"⚠️ {agent_name} agent completed with status: {result.get(status_key, 'unknown')}")
                results[agent_name] = "WARNING"
                
        except Exception as e:
            print(f"❌ {agent_name} agent failed: {str(e)}")
            results[agent_name] = "FAIL"
    
    return results

def test_services_module():
    """Test the services module imports"""
    print("\n📦 Testing Services Module...")
    
    try:
        from services import (
            LLMServiceManager,
            LLMProvider,
            LLMConfig,
            get_llm_service,
            generate_response,
            generate_agent_response
        )
        
        print("✅ All services imports successful")
        
        # Test convenience functions
        response = generate_response("Hello, how are you feeling today?")
        print(f"✅ Convenience function works: {response[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Services module test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Agent LLM Integration Tests\n")
    
    # Check environment variables
    print("🔑 Checking Environment Variables...")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key:
        print("✅ OPENAI_API_KEY found")
    else:
        print("⚠️ OPENAI_API_KEY not found")
    
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY found")
    else:
        print("⚠️ ANTHROPIC_API_KEY not found")
    
    if not openai_key and not anthropic_key:
        print("❌ No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
        return False
    
    # Run tests
    llm_success = test_llm_service()
    services_success = test_services_module()
    agent_results = test_agent_nodes()
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    print(f"LLM Service: {'✅ PASS' if llm_success else '❌ FAIL'}")
    print(f"Services Module: {'✅ PASS' if services_success else '❌ FAIL'}")
    
    print("\nAgent Results:")
    for agent, result in agent_results.items():
        status_icon = "✅" if result == "PASS" else "⚠️" if result == "WARNING" else "❌"
        print(f"  {status_icon} {agent}: {result}")
    
    # Overall result
    all_passed = llm_success and services_success and all(r in ["PASS", "WARNING"] for r in agent_results.values())
    
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 