# First incremental changes to 007-workflow.py

from typing import TypedDict, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
import os
from langsmith.run_helpers import traceable
import json
from datetime import datetime
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import add_messages
from functools import lru_cache
import sys

# Safe environment variable handling
try:
    from langchain_openai import ChatOpenAI
    import openai
except ImportError:
    print("Warning: langchain_openai or openai not available")

# Enhanced State Definition for 007 Productivity Agent
class AgentState(TypedDict):
    user: dict  # Store user information (name, preferences)
    todos: list  # Store todo items
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: str  # For tracking workflow progress
    skills_used: list  # Track which skills were used in the session

# Initialize Models with error handling
@lru_cache(maxsize=4)
def _get_model(model_name: str, system_prompt: str = None):
    try:
        if model_name == "openai":
            model = ChatOpenAI(temperature=0, model_name="gpt-4o")
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
        
        if system_prompt:
            model = model.bind(system_message=system_prompt)
        
        return model
    except Exception as e:
        print(f"Error initializing model: {str(e)}")
        # Return a mock model if initialization fails
        return None

# Node Implementations
@traceable(project_name="007-productivity-agent")
def validate_input(state: AgentState):
    """Validate the input state and initialize if needed"""
    
    # Initialize workflow tracking fields if not present
    if "user" not in state:
        state["user"] = {"name": None}
    if "todos" not in state:
        state["todos"] = []
    if "current_step" not in state:
        state["current_step"] = "initialize_agent"
    if "messages" not in state:
        state["messages"] = []
    if "skills_used" not in state:
        state["skills_used"] = []
        
    return state

@traceable(project_name="007-productivity-agent")
def initialize_agent(state: AgentState):
    """Initialize the agent state"""
    # Just update the current step
    return {
        "current_step": "generate_greeting"
    }

@traceable(project_name="007-productivity-agent")
def generate_greeting(state: AgentState):
    """Generate the initial greeting for the user"""
    
    # Check if we know the user's name
    user_name = state["user"].get("name")
    
    # Construct the greeting message
    if user_name:
        greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you today?"
    else:
        greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    
    # Add the greeting as a system message
    system_prompt = """You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
You initially have some limitations, but those will improve soon.
Your current skills:
1. Remember and manage to-do items
2. Call external services to shop for what the user wants and provide information"""
    
    # Add the messages
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    return {
        "messages": messages,
        "current_step": "process_input"
    }

# Placeholder for the rest of the implementation
# We'll add more in the next steps