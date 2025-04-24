#!/usr/bin/env python
"""
Standalone 007 Productivity Agent
This script contains the complete agent implementation in a single file.
"""

import argparse
import os
import sys
import time
from typing import Dict, List, Any, TypedDict, Annotated
from functools import lru_cache

# Langchain/OpenAI imports with error handling
try:
    from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
    from langchain_openai import ChatOpenAI
    IMPORTS_AVAILABLE = True
except ImportError:
    print("Warning: langchain/openai packages not available. Will use mock mode only.")
    # Define minimal classes for mocked mode
    class BaseMessage:
        def __init__(self, content):
            self.content = content
            self.type = "base"
    
    class SystemMessage(BaseMessage):
        def __init__(self, content):
            super().__init__(content)
            self.type = "system"
    
    class HumanMessage(BaseMessage):
        def __init__(self, content):
            super().__init__(content)
            self.type = "human"
    
    class AIMessage(BaseMessage):
        def __init__(self, content):
            super().__init__(content)
            self.type = "ai"
    
    IMPORTS_AVAILABLE = False

# Agent State Definition
class AgentState(dict):
    """Simplified AgentState that behaves like a dict but with typing"""
    def __init__(self):
        super().__init__({
            "user": {"name": None},
            "todos": [],
            "current_step": "initialize_agent",
            "messages": [],
            "skills_used": []
        })

# Mock Language Model for testing
class MockLanguageModel:
    """A mock model that logs calls and returns predefined responses"""
    
    def __init__(self, name):
        self.name = name
        self.call_count = 0
        # Predefined responses for different contexts
        self.responses = {
            "greeting": "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?",
            "name_intro": "Nice to meet you, {name}! How can I help you today? I can help with tasks, finding information, and more.",
            "task_added": "I've added that task to your list. Is there anything else you'd like me to help you with?",
            "fallback": "I understand. How can I assist you further?",
            "name_recall": "Your name is {name}. Is there anything else I can help you with?"
        }
    
    def __call__(self, messages, *args, **kwargs):
        """Make the object callable like a real LLM"""
        self.call_count += 1
        print(f"🔍 MOCK MODEL ({self.name}) CALLED (call #{self.call_count})")
        print(f"📥 Input messages: {len(messages)} message(s)")
        
        # Get the last message to help with context detection
        last_msg = None
        if messages and len(messages) > 0:
            last_msg = messages[-1]
            last_content = getattr(last_msg, 'content', str(last_msg))
            print(f"📄 Last message content (sample): {last_content[:100]}...")
        
        # Extract user name from system prompt if available
        user_name = "user"
        for msg in messages:
            if getattr(msg, 'type', '') == 'system':
                content = getattr(msg, 'content', '')
                if "user's name is " in content:
                    name_parts = content.split("user's name is ")
                    if len(name_parts) > 1:
                        name_part = name_parts[1].split(".")[0].strip()
                        if name_part and name_part.lower() != "unknown":
                            user_name = name_part
        
        # Determine which response to use based on message content
        response_key = "fallback"
        
        # Check for specific contexts
        if last_msg and isinstance(last_msg, HumanMessage):
            content = last_msg.content.lower()
            
            # Name recall request
            if "what" in content and "name" in content:
                response_key = "name_recall"
                
            # Task related
            elif any(word in content for word in ["task", "todo", "reminder", "schedule"]):
                response_key = "task_added"
                
            # First message after greeting (likely name introduction)
            elif len(messages) == 3 and messages[0].type == "system" and messages[1].type == "ai":
                response_key = "name_intro"
        
        # Get the response template and format it if needed
        response_template = self.responses[response_key]
        if "{name}" in response_template:
            response_text = response_template.format(name=user_name)
        else:
            response_text = response_template
            
        print(f"📤 Responding with: {response_key} -> {response_text[:50]}...")
        
        # Create a response object similar to what the real model would return
        return AIMessage(content=response_text)
    
    def bind(self, system_message=None):
        """Support the bind method that real models have"""
        print(f"🔄 Mock model bind called with system message: {system_message[:50] if system_message else 'None'}")
        return self

# Model initialization with caching
@lru_cache(maxsize=4)
def get_model(model_name: str = "openai", system_prompt: str = None, mocked: bool = False):
    """Get a language model, with improved logging for mocked vs real mode"""
    print(f"📝 get_model called with: model_name={model_name}, mocked={mocked}")
    
    if mocked or not IMPORTS_AVAILABLE:
        print("🔄 Using MOCKED model implementation")
        return MockLanguageModel(model_name)
    
    try:
        if model_name == "openai":
            print("🔌 Initializing REAL OpenAI model (gpt-4o)")
            model = ChatOpenAI(temperature=0, model_name="gpt-4o")
            
            if system_prompt:
                print(f"🧠 Binding system prompt: {system_prompt[:50]}...")
                model = model.bind(system_message=system_prompt)
            
            return model
        else:
            raise ValueError(f"Unsupported model type: {model_name}")
    except Exception as e:
        print(f"❌ Error initializing OpenAI model: {str(e)}")
        print("⚠️ Falling back to mock model")
        return MockLanguageModel(f"error-fallback-{model_name}")

# Agent functions
def initialize_agent(state: AgentState):
    """Initialize the agent state"""
    print("🏁 Entering initialize_agent function")
    return {
        "current_step": "generate_greeting"
    }

def generate_greeting(state: AgentState):
    """Generate the initial greeting for the user with enhanced logging"""
    print("🏁 Entering generate_greeting function")
    
    # Check if we know the user's name
    user_name = state["user"].get("name")
    print(f"📊 User name from state: {user_name}")
    
    # Determine if we're in mocked mode
    is_mocked = os.environ.get("MOCK_MODE", "False").lower() == "true"
    print(f"⚙️ generate_greeting: Mocked mode = {is_mocked}")
    
    # Construct the system prompt
    system_prompt = """You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
Your current skills:
1. Remember and manage to-do items
2. Call external services to shop for what the user wants and provide information
3. Remember the user's name and preferences

Your first message should ask for the user's name if you don't know it yet."""
    
    # Get the model (real or mocked)
    model = get_model("openai", system_prompt, mocked=is_mocked)
    print(f"📊 Got model: {type(model).__name__}")
    
    # Initial message to start the conversation
    initial_message = SystemMessage(content=system_prompt)
    
    # Determine greeting message
    try:
        print("🚀 Calling model to generate greeting")
        # We only have a system message at this point
        messages = [initial_message]
        
        start_time = time.time()
        response = model(messages)
        end_time = time.time()
        
        print(f"✅ Greeting generated in {end_time - start_time:.2f}s")
        greeting = response.content
    except Exception as e:
        print(f"❌ Error generating greeting: {str(e)}")
        # Fallback greeting on error
        if user_name:
            greeting = f"Hello {user_name}! I'm 007, your personal productivity agent. How can I help you today?"
        else:
            greeting = "Hello! I'm 007, your personal productivity agent. I don't think we've met before. What's your name?"
    
    print(f"💬 Greeting message: {greeting}")
    
    # Add the messages
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    print(f"✅ generate_greeting complete, returning {len(messages)} messages")
    return {
        "messages": messages,
        "current_step": "process_input"
    }

def process_input(state: AgentState):
    """Process user input and generate a response using the language model"""
    print("🏁 Entering process_input function")
    
    # Get current messages
    messages = state.get("messages", [])
    print(f"📊 Current message count: {len(messages)}")
    
    # Find the last human message
    last_human_message = None
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            last_human_message = message
            break
    
    if not last_human_message:
        print("⚠️ No human message found in state")
        return state
    
    print(f"👤 Last human message: {last_human_message.content[:100]}...")
    
    # Check if this is a name introduction
    is_name_introduction = False
    if len(messages) >= 2:
        # The previous ai message was asking for name, and this is the first human response
        prev_ai_message = None
        for msg in reversed(messages[:-1]):  # All but the last message (which is the human's)
            if isinstance(msg, AIMessage):
                prev_ai_message = msg
                break
        
        if prev_ai_message and "what's your name" in prev_ai_message.content.lower():
            is_name_introduction = True
            print("🔍 Detected name introduction context")
    
    # Process name introduction if detected
    if is_name_introduction:
        # Extract name
        name_parts = last_human_message.content.split("my name is ")
        if len(name_parts) > 1:
            name = name_parts[1].strip()
        else:
            name = last_human_message.content.strip()
        
        # Update user name in state
        state["user"]["name"] = name
        print(f"📊 Updated user name to: {name}")
    
    # Determine if we're in mocked mode
    is_mocked = os.environ.get("MOCK_MODE", "False").lower() == "true"
    print(f"⚙️ process_input: Mocked mode = {is_mocked}")
    
    # Get user name if available
    user_name = state["user"].get("name", "")
    
    # Prepare system prompt for model
    system_prompt = f"""You are 007, a personal productivity agent.
You help users manage their tasks, find information, and boost their productivity.
You have a friendly, helpful tone.
The user's name is {user_name if user_name else 'unknown'}.
Keep your responses concise and focused.

If the user asks about their name, make sure to tell them their name is {user_name if user_name else 'unknown'}.
If the user asks about tasks, offer to create a task for them."""
    
    # Get model
    try:
        print("🚀 Calling model to generate response")
        model = get_model("openai", system_prompt, mocked=is_mocked)
        
        start_time = time.time()
        response = model(messages)
        end_time = time.time()
        
        print(f"✅ Response generated in {end_time - start_time:.2f}s")
        print(f"💬 Response content: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Error calling model: {str(e)}")
        response = AIMessage(content="I understand. Is there anything specific you'd like help with today?")
    
    # Add the response to messages
    messages.append(response)
    
    # Skills tracking - simple version
    skills_used = state.get("skills_used", [])
    if last_human_message and "task" in last_human_message.content.lower():
        if "task_management" not in skills_used:
            skills_used.append("task_management")
    
    # Update the state with new messages and other changes
    return {
        **state,
        "messages": messages,
        "skills_used": skills_used,
        "current_step": "process_input"  # Loop back to handle next input
    }

def run_agent():
    """Run the 007 agent interactively"""
    # Initialize state
    state = AgentState()
    state = {**state, **initialize_agent(state)}
    state = {**state, **generate_greeting(state)}
    
    # Print the initial greeting
    messages = state.get("messages", [])
    if messages:
        for message in messages:
            if message.type == "ai":
                print(f"Agent: {message.content}")
    
    # Interactive loop
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Agent: Goodbye!")
                break
            
            # Add user input to messages
            state["messages"].append(HumanMessage(content=user_input))
            
            # Process user input
            updated_state = process_input(state)
            state = {**state, **updated_state}
            
            # Display the agent's response
            messages = state.get("messages", [])
            if messages:
                last_ai_message = None
                for message in reversed(messages):
                    if message.type == "ai":
                        last_ai_message = message
                        break
                
                if last_ai_message:
                    print(f"Agent: {last_ai_message.content}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the 007 Productivity Agent")
    parser.add_argument("--mocked", action="store_true", 
                        help="Run with mocked models instead of real API calls")
    args = parser.parse_args()
    
    # Set the environment variable based on the flag
    if args.mocked:
        os.environ["MOCK_MODE"] = "True"
        print("🚀 Starting 007 Productivity Agent with Mocked Implementation")
        print("=== 007 Productivity Agent (Mocked Mode) ===")
        print("Using predefined inputs for testing.")
    else:
        os.environ["MOCK_MODE"] = "False"
        print("🚀 Starting 007 Productivity Agent with OpenAI Integration")
        print("=== 007 Productivity Agent (Live Mode) ===")
        print("Using real OpenAI API for all model calls.")
    
    # Run the agent
    run_agent()