# Fixed implementation of workflowbond7.py

from typing import TypedDict, Dict, Any, List, Annotated, Literal
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
        
        # Fix: Apply system prompt differently
        if system_prompt:
            # Use messages method instead of system_message binding
            return model.with_messages([SystemMessage(content=system_prompt)])
        
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

@traceable(project_name="007-productivity-agent")
def process_input(state: AgentState):
    """Process user input and determine next action"""
    
    # Get the latest message from the user
    latest_message = state["messages"][-1]
    
    # If we're still in the introduction phase and don't know the user's name
    if state["user"].get("name") is None and isinstance(latest_message, HumanMessage):
        # Extract name from message
        name = latest_message.content.strip()
        if len(name) > 0:
            # Update user info
            return {
                "user": {"name": name},
                "messages": [AIMessage(content=f"Nice to meet you, {name}! How can I help you today?")],
                "current_step": "process_input"
            }
    
    # Otherwise, determine what the user wants
    model = _get_model("openai")
    if not model:
        # Fallback if model not available
        return {
            "messages": [AIMessage(content="I'm sorry, but I'm having trouble processing your request right now. Please try again later.")],
            "current_step": "end_session"
        }
    
    # Analyze user intent
    system_prompt = """You are analyzing user input to determine their intent.
Categories:
- add_todo: User wants to add a task to their todo list
- view_todos: User wants to see their todo list
- general_question: User has a general question
- end_conversation: User wants to end the conversation

Format your response as a JSON object with two fields:
- "intent": One of the categories above
- "details": Additional details extracted from the message

Example:
{"intent": "add_todo", "details": "Buy milk tomorrow"}"""
    
    # Fix: Create intent analyzer differently
    intent_analyzer = _get_model("openai")
    
    # Get user intent - Fixed approach
    messages_for_intent = [SystemMessage(content=system_prompt), latest_message]
    intent_response = intent_analyzer.invoke(messages_for_intent)
    
    try:
        intent_data = json.loads(intent_response.content)
        intent = intent_data.get("intent", "general_question")
        details = intent_data.get("details", "")
        
        # Add the intent to skills used
        skills_used = state["skills_used"] 
        if intent not in skills_used:
            skills_used.append(intent)
        
        # Route to appropriate action
        return {
            "skills_used": skills_used,
            "current_step": intent
        }
    except Exception as e:
        print(f"Error parsing intent: {str(e)}")
        # Default to general question if parsing fails
        return {
            "current_step": "general_question"
        }

@traceable(project_name="007-productivity-agent")
def add_todo(state: AgentState):
    """Add a task to the todo list"""
    
    latest_message = state["messages"][-1].content
    
    # Extract task from message or use entire message
    todos = state["todos"]
    todos.append({"task": latest_message, "created_at": datetime.now().isoformat()})
    
    return {
        "todos": todos,
        "messages": [AIMessage(content=f"I've added \"{latest_message}\" to your todo list. Is there anything else you'd like me to do?")],
        "current_step": "process_input"
    }

@traceable(project_name="007-productivity-agent")
def view_todos(state: AgentState):
    """Show the todo list"""
    
    todos = state["todos"]
    
    if not todos:
        response = "You don't have any tasks in your todo list yet. Would you like to add one?"
    else:
        response = "Here's your current todo list:\n"
        for i, todo in enumerate(todos, 1):
            response += f"{i}. {todo['task']}\n"
        response += "\nIs there anything else you'd like me to do?"
    
    return {
        "messages": [AIMessage(content=response)],
        "current_step": "process_input"
    }

@traceable(project_name="007-productivity-agent")
def general_question(state: AgentState):
    """Handle general questions"""
    
    # Get all messages
    all_messages = state["messages"]
    
    # Use the model to generate a response
    model = _get_model("openai")
    if not model:
        return {
            "messages": [AIMessage(content="I'm sorry, but I'm having trouble answering your question right now. Please try again later.")],
            "current_step": "process_input"
        }
    
    # Generate response
    response = model.invoke(all_messages)
    
    return {
        "messages": [response],
        "current_step": "process_input"
    }

@traceable(project_name="007-productivity-agent")
def end_conversation(state: AgentState):
    """End the conversation"""
    
    # Create a summary of what was accomplished
    tasks_added = len(state["todos"])
    skills_used = state["skills_used"]
    
    farewell = f"It was great helping you today! "
    if tasks_added > 0:
        farewell += f"I've added {tasks_added} tasks to your todo list. "
    farewell += "Feel free to come back anytime you need assistance with your productivity."
    
    return {
        "messages": [AIMessage(content=farewell)],
        "current_step": END
    }

@traceable(project_name="007-productivity-agent")
def end_session(state: AgentState):
    """End session due to error or other issue"""
    return {
        "current_step": END
    }

# Define the workflow graph
def create_agent_graph():
    """Create the workflow graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("initialize_agent", initialize_agent)
    workflow.add_node("generate_greeting", generate_greeting)
    workflow.add_node("process_input", process_input)
    workflow.add_node("add_todo", add_todo)
    workflow.add_node("view_todos", view_todos)
    workflow.add_node("general_question", general_question)
    workflow.add_node("end_conversation", end_conversation)
    workflow.add_node("end_session", end_session)
    
    # Define edges
    workflow.add_edge("validate_input", "initialize_agent")
    workflow.add_edge("initialize_agent", "generate_greeting")
    workflow.add_edge("generate_greeting", "process_input")
    
    # From process_input, go to specific handlers
    workflow.add_conditional_edges(
        "process_input",
        lambda state: state["current_step"],
        {
            "add_todo": "add_todo",
            "view_todos": "view_todos", 
            "general_question": "general_question",
            "end_conversation": "end_conversation",
            "end_session": "end_session"
        }
    )
    
    # Return to process_input after handling specific requests
    workflow.add_edge("add_todo", "process_input")
    workflow.add_edge("view_todos", "process_input")
    workflow.add_edge("general_question", "process_input")
    
    # Set entry point
    workflow.set_entry_point("validate_input")
    
    return workflow

# Create the compiled application
app = create_agent_graph().compile()

# Main function for local testing
def main():
    """Run the agent workflow for local testing"""
    
    workflow = create_agent_graph().compile()
    
    # Initial empty state
    state = {"messages": []}
    
    # Print welcome
    print("\n=== 007 Productivity Agent ===\n")
    print("Type 'exit' to end the conversation.\n")
    
    # Get initial response from agent
    result = workflow.invoke(state)
    
    # Print agent's greeting
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            print(f"Agent: {message.content}")
    
    # Main conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nExiting conversation. Goodbye!")
            break
        
        # Add user message to state
        state = result.copy()
        state["messages"].append(HumanMessage(content=user_input))
        
        # Invoke workflow
        try:
            result = workflow.invoke(state)
            
            # Print agent's response
            for message in result["messages"]:
                if isinstance(message, AIMessage):
                    print(f"Agent: {message.content}")
            
            # Check if workflow ended
            if result["current_step"] == END:
                break
        except Exception as e:
            print(f"\nError processing your request: {str(e)}")
            print("Let's try again.")

if __name__ == "__main__":
    main()