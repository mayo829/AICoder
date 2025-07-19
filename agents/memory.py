"""
Memory Agent

This agent is the long-term brain of the system. It helps other agents be aware of
past decisions, codebase state, and learned best practices. It manages persistent
memory storage and retrieval for context-aware decision making.
"""

from typing import Dict, Any, List, Optional
import logging
import json
import hashlib
from datetime import datetime, timedelta
import os
from services.llm import generate_agent_response

# Configure logging
logger = logging.getLogger(__name__)

# LLM service is imported and used via generate_agent_response function

class MemoryManager:
    """Manages persistent memory storage and retrieval"""
    
    def __init__(self, storage_path: str = "memory_storage"):
        self.storage_path = storage_path
        self.memory_file = os.path.join(storage_path, "memory.json")
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        """Ensure the storage directory and file exist"""
        os.makedirs(self.storage_path, exist_ok=True)
        if not os.path.exists(self.memory_file):
            self.save_memory({"memories": [], "metadata": {"created": datetime.now().isoformat()}})
    
    def save_memory(self, memory_data: Dict[str, Any]):
        """Save memory data to persistent storage"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def load_memory(self) -> Dict[str, Any]:
        """Load memory data from persistent storage"""
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
            return {"memories": [], "metadata": {"created": datetime.now().isoformat()}}

def memory_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Memory node that manages and retrieves context from long-term memory.
    
    Args:
        state: The current state containing information to store/retrieve
        
    Returns:
        Updated state with memory context
    """
    try:
        # Initialize memory manager
        memory_manager = MemoryManager()
        
        # Extract relevant information from state
        user_input = state.get("user_input", "")
        current_context = state.get("context", "")
        agent_results = state.get("agent_results", {})
        project_id = state.get("project_id", "default")
        
        # Store new information in memory
        store_in_memory(memory_manager, state)
        
        # Retrieve relevant context from memory
        relevant_context = retrieve_relevant_context(memory_manager, user_input, current_context)
        
        # Update state with memory context
        updated_state = state.copy()
        updated_state["memory_context"] = relevant_context
        updated_state["memory_status"] = "completed"
        updated_state["context"] = merge_contexts(current_context, relevant_context)
        
        logger.info("Memory processing completed successfully")
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in memory node: {str(e)}")
        # Update state with error information
        updated_state = state.copy()
        updated_state["memory_status"] = "failed"
        updated_state["error"] = str(e)
        return updated_state

def store_in_memory(memory_manager: MemoryManager, state: Dict[str, Any]):
    """
    Store relevant information from current state in memory.
    
    Args:
        memory_manager: Memory manager instance
        state: Current state to store
    """
    try:
        # Load existing memory
        memory_data = memory_manager.load_memory()
        
        # Create memory entry
        memory_entry = {
            "id": generate_memory_id(state),
            "timestamp": datetime.now().isoformat(),
            "project_id": state.get("project_id", "default"),
            "user_input": state.get("user_input", ""),
            "context": state.get("context", ""),
            "agent_results": state.get("agent_results", {}),
            "workflow_status": state.get("workflow_status", ""),
            "tags": extract_tags(state),
            "importance": calculate_importance(state)
        }
        
        # Add to memories
        memory_data["memories"].append(memory_entry)
        
        # Limit memory size (keep last 1000 entries)
        if len(memory_data["memories"]) > 1000:
            memory_data["memories"] = memory_data["memories"][-1000:]
        
        # Save updated memory
        memory_manager.save_memory(memory_data)
        
        logger.info(f"Stored memory entry: {memory_entry['id']}")
        
    except Exception as e:
        logger.error(f"Error storing in memory: {str(e)}")

def retrieve_relevant_context(memory_manager: MemoryManager, user_input: str, current_context: str) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context from memory based on current input and context.
    
    Args:
        memory_manager: Memory manager instance
        user_input: Current user input
        current_context: Current context
        
    Returns:
        List of relevant memory entries
    """
    try:
        # Load memory
        memory_data = memory_manager.load_memory()
        
        # Use LLM to enhance context retrieval
        enhanced_context = enhance_context_retrieval(user_input, current_context, memory_data)
        
        # Find relevant memories with enhanced understanding
        relevant_memories = []
        for memory in memory_data.get("memories", []):
            relevance_score = calculate_enhanced_relevance(memory, enhanced_context)
            if relevance_score > 0.3:  # Threshold for relevance
                memory["relevance_score"] = relevance_score
                relevant_memories.append(memory)
        
        # Sort by relevance and recency
        relevant_memories.sort(key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True)
        
        # Return top 10 most relevant memories
        return relevant_memories[:10]
        
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return []

def enhance_context_retrieval(user_input: str, current_context: str, memory_data: Dict[str, Any]) -> str:
    """
    Use LLM to enhance context retrieval by understanding semantic relationships.
    
    Args:
        user_input: Current user input
        current_context: Current context
        memory_data: All memory data
        
    Returns:
        Enhanced context understanding
    """
    try:
        # Create a summary of available memories for LLM analysis
        memory_summary = "Available memory entries:\n"
        for i, memory in enumerate(memory_data.get("memories", [])[:20]):  # Limit to recent 20
            memory_summary += f"{i+1}. {memory.get('user_input', '')[:100]}... (Tags: {', '.join(memory.get('tags', []))})\n"
        
        prompt = f"""
        Analyze the current user input and context to identify what type of information would be most relevant from the available memory entries.
        
        Current User Input: {user_input}
        Current Context: {current_context}
        
        {memory_summary}
        
        Based on this analysis, what are the key concepts, technologies, or patterns that should be considered when retrieving relevant context? Focus on semantic relationships rather than just keyword matching.
        """
        
        # Get enhanced understanding from LLM
        enhanced_understanding = generate_agent_response("memory", prompt)
        
        return f"{user_input} {current_context} {enhanced_understanding}"
        
    except Exception as e:
        logger.error(f"Error enhancing context retrieval: {str(e)}")
        return f"{user_input} {current_context}"

def calculate_enhanced_relevance(memory: Dict[str, Any], enhanced_context: str) -> float:
    """
    Calculate enhanced relevance score using LLM understanding.
    
    Args:
        memory: Memory entry
        enhanced_context: Enhanced context understanding
        
    Returns:
        Enhanced relevance score (0.0 to 1.0)
    """
    try:
        # Use LLM to calculate semantic relevance
        prompt = f"""
        Calculate the relevance between the current context and a memory entry.
        
        Current Context: {enhanced_context}
        Memory Entry: {memory.get('user_input', '')} - {memory.get('context', '')}
        Memory Tags: {', '.join(memory.get('tags', []))}
        
        Rate the relevance from 0.0 to 1.0, where:
        - 0.0 = Completely irrelevant
        - 0.5 = Somewhat related
        - 1.0 = Highly relevant
        
        Consider semantic relationships, not just keyword matches.
        Return only the numerical score.
        """
        
        try:
            relevance_response = generate_agent_response("memory", prompt)
            # Try to extract numerical score from response
            import re
            score_match = re.search(r'0\.\d+|1\.0', relevance_response)
            if score_match:
                return float(score_match.group())
        except:
            pass
        
        # Fallback to keyword-based relevance
        return calculate_relevance(memory, enhanced_context)
        
    except Exception as e:
        logger.error(f"Error calculating enhanced relevance: {str(e)}")
        return calculate_relevance(memory, enhanced_context)

def calculate_relevance(memory: Dict[str, Any], search_query: str) -> float:
    """
    Calculate relevance score between memory and search query.
    
    Args:
        memory: Memory entry
        search_query: Search query
        
    Returns:
        Relevance score (0.0 to 1.0)
    """
    try:
        # Simple keyword-based relevance calculation
        query_words = set(search_query.lower().split())
        memory_text = f"{memory.get('user_input', '')} {memory.get('context', '')}".lower()
        memory_words = set(memory_text.split())
        
        if not query_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(query_words.intersection(memory_words))
        union = len(query_words.union(memory_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
        
    except Exception as e:
        logger.error(f"Error calculating relevance: {str(e)}")
        return 0.0

def generate_memory_id(state: Dict[str, Any]) -> str:
    """
    Generate a unique ID for memory entry.
    
    Args:
        state: Current state
        
    Returns:
        Unique memory ID
    """
    content = f"{state.get('user_input', '')}{state.get('timestamp', '')}{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def extract_tags(state: Dict[str, Any]) -> List[str]:
    """
    Extract tags from state for better memory organization.
    
    Args:
        state: Current state
        
    Returns:
        List of tags
    """
    tags = []
    
    # Extract tags from user input
    user_input = state.get("user_input", "").lower()
    if "api" in user_input:
        tags.append("api")
    if "database" in user_input:
        tags.append("database")
    if "frontend" in user_input or "ui" in user_input:
        tags.append("frontend")
    if "backend" in user_input:
        tags.append("backend")
    if "test" in user_input:
        tags.append("testing")
    
    # Extract tags from workflow status
    workflow_status = state.get("workflow_status", "")
    if workflow_status:
        tags.append(workflow_status)
    
    return list(set(tags))

def calculate_importance(state: Dict[str, Any]) -> float:
    """
    Calculate importance score for memory entry.
    
    Args:
        state: Current state
        
    Returns:
        Importance score (0.0 to 1.0)
    """
    importance = 0.5  # Base importance
    
    # Increase importance for completed workflows
    if state.get("workflow_status") == "completed":
        importance += 0.3
    
    # Increase importance for error states (for learning)
    if state.get("error"):
        importance += 0.2
    
    # Increase importance for complex inputs
    user_input = state.get("user_input", "")
    if len(user_input) > 100:
        importance += 0.1
    
    return min(importance, 1.0)

def merge_contexts(current_context: str, memory_context: List[Dict[str, Any]]) -> str:
    """
    Merge current context with retrieved memory context.
    
    Args:
        current_context: Current context
        memory_context: Retrieved memory context
        
    Returns:
        Merged context
    """
    if not memory_context:
        return current_context
    
    # Build context from relevant memories
    memory_summary = "Previous relevant context:\n"
    for memory in memory_context[:3]:  # Top 3 most relevant
        memory_summary += f"- {memory.get('user_input', '')[:100]}...\n"
    
    return f"{current_context}\n\n{memory_summary}"

def cleanup_old_memories(memory_manager: MemoryManager, days_to_keep: int = 30):
    """
    Clean up old memory entries.
    
    Args:
        memory_manager: Memory manager instance
        days_to_keep: Number of days to keep memories
    """
    try:
        memory_data = memory_manager.load_memory()
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Filter out old memories
        filtered_memories = []
        for memory in memory_data.get("memories", []):
            try:
                memory_date = datetime.fromisoformat(memory["timestamp"])
                if memory_date > cutoff_date or memory.get("importance", 0) > 0.8:
                    filtered_memories.append(memory)
            except:
                # Keep memories with invalid dates
                filtered_memories.append(memory)
        
        memory_data["memories"] = filtered_memories
        memory_manager.save_memory(memory_data)
        
        logger.info(f"Cleaned up old memories. Kept {len(filtered_memories)} entries.")
        
    except Exception as e:
        logger.error(f"Error cleaning up memories: {str(e)}")