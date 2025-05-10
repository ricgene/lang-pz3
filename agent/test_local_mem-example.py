#!/usr/bin/env python
import os
from pathlib import Path
from dotenv import load_dotenv
from standalone_bond7_agent import AgentState, process_input
from langchain_core.messages import HumanMessage, AIMessage

def test_memory_persistence():
    """Test memory persistence with a sample user"""
    
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # Verify OpenAI API key is loaded
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    print("✅ Environment variables loaded successfully")
    
    # Initialize state with user email
    state = AgentState()
    state["user"]["email"] = "test@example.com"
    
    # First interaction - name introduction
    print("\n=== First Interaction ===")
    # Add a greeting message first
    state["messages"].append(AIMessage(content="Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"))
    state["messages"].append(HumanMessage(content="My name is Test User"))
    state = process_input(state)
    
    # Second interaction - verify memory
    print("\n=== Second Interaction ===")
    state["messages"].append(HumanMessage(content="What's my name?"))
    state = process_input(state)
    
    # Create new state to test persistence
    print("\n=== Testing Persistence ===")
    new_state = AgentState()
    new_state["user"]["email"] = "test@example.com"
    new_state["messages"].append(HumanMessage(content="Do you remember my name?"))
    new_state = process_input(new_state)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_memory_persistence() 