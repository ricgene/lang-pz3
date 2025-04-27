from typing import TypedDict, Dict, Any, List, Annotated
from langgraph.graph import StateGraph, END
import os
from langsmith.run_helpers import traceable
from datetime import datetime
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph import add_messages
from functools import lru_cache

# Safe environment variable handling
try:
    from langchain_openai import ChatOpenAI
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: Required packages not available")

class WorkflowState(TypedDict):
    customer: dict  # Store customer information
    task: dict     # Store task details
    vendor: dict   # Store vendor information
    messages: Annotated[List[BaseMessage], add_messages]  # For conversation tracking
    current_step: Annotated[str, add_messages]  # For tracking workflow progress
    sentiment: str  # For tracking customer sentiment
    sentiment_attempts: int  # Track number of sentiment analysis attempts

@lru_cache(maxsize=1)
def get_llm():
    """Get the language model with error handling"""
    try:
        return ChatOpenAI(temperature=0, model="gpt-4")
    except Exception as e:
        print(f"Error initializing LLM: {str(e)}")
        return None

def validate_input(state: WorkflowState) -> Dict:
    """Validate and initialize the workflow state"""
    print("\nValidating input...")
    validated_state = state.copy()
    if "customer" not in validated_state:
        validated_state["customer"] = {"name": None}
    if "task" not in validated_state:
        validated_state["task"] = {"description": None, "status": "new"}
    if "vendor" not in validated_state:
        validated_state["vendor"] = {"name": "Dave's Plumbing", "email": "dave@plumbing.com"}
    if "messages" not in validated_state:
        validated_state["messages"] = []
    if "sentiment" not in validated_state:
        validated_state["sentiment"] = "neutral"
    if "sentiment_attempts" not in validated_state:
        validated_state["sentiment_attempts"] = 0
    
    print("Validation complete. Moving to initialize step...")
    return {"current_step": "initialize", **validated_state}

def initialize_workflow(state: WorkflowState) -> Dict:
    """Initialize the workflow with a greeting"""
    print("\nInitializing workflow...")
    system_prompt = """You are a professional project coordinator helping customers with home improvement projects.
You're currently helping with a kitchen faucet installation project.
The vendor is Dave's Plumbing."""

    greeting = "Hello! I'm your project coordinator. I'll help you with your kitchen faucet installation. What's your name?"
    
    messages = [
        SystemMessage(content=system_prompt),
        AIMessage(content=greeting)
    ]
    
    print("Initialization complete. Moving to process_name step...")
    return {
        "messages": messages,
        "current_step": "process_name"
    }

def process_name(state: WorkflowState) -> Dict:
    """Process the user's name and update the conversation flow."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    name = last_message.content.strip()
    
    # Add assistant's response acknowledging the name
    response = f"Thank you, {name}! I'll help you with your kitchen faucet installation. "
    response += "Would you like me to schedule an appointment with Dave's Plumbing for the installation?"
    
    state["messages"].append(AIMessage(content=response))
    
    # Move to human_step to get their response about scheduling
    return {
        "current_step": "human_step",
        "messages": state["messages"]
    }

def process_schedule(state: WorkflowState) -> Dict:
    """Process the user's scheduling response."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # After getting their scheduling preference, thank them and end
    response = "Thank you for letting me know. I'll have Dave's Plumbing contact you to confirm the details. Have a great day!"
    
    state["messages"].append(AIMessage(content=response))
    
    return {
        "current_step": END,
        "messages": state["messages"]
    }

def confirm_end(state: WorkflowState) -> WorkflowState:
    """Confirm if the user needs anything else."""
    print("\nConfirming end...")
    
    # Get the last human message
    human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    if not human_messages:
        print("No human message found, returning to confirm_end")
        return {"current_step": "confirm_end"}
    
    last_message = human_messages[-1].content.strip().lower()
    
    if "yes" in last_message or "yeah" in last_message:
        state["messages"].append(
            AIMessage(content="What else can I help you with regarding your kitchen faucet installation?")
        )
        return {"current_step": "process_additional"}
    
    state["messages"].append(
        AIMessage(content=f"Great! {state['vendor']['name']} will be in touch soon. Have a wonderful day!")
    )
    return {"current_step": "__end__"}

def process_additional(state: WorkflowState) -> WorkflowState:
    """Process any additional requests."""
    print("\nProcessing additional request...")
    
    # Get the last human message
    human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    if not human_messages:
        print("No human message found, returning to process_additional")
        return {"current_step": "process_additional"}
    
    last_message = human_messages[-1].content.strip()
    
    # Add response and end conversation
    state["messages"].append(
        AIMessage(content=f"I'll make sure to pass this information to {state['vendor']['name']}. "
                         "They will address this when they contact you. Is there anything else?")
    )
    
    return {"current_step": "confirm_end"}

def analyze_sentiment(state: WorkflowState) -> Dict:
    """Analyze customer sentiment about scheduling"""
    print("\nAnalyzing sentiment...")
    
    # Check attempt limit
    attempts = state.get("sentiment_attempts", 0)
    if attempts >= 3:  # Limit to 3 attempts
        print("Maximum sentiment analysis attempts reached")
        return {
            "sentiment": "unclear",
            "messages": [AIMessage(content="I'll have Dave's Plumbing contact you to discuss the scheduling details directly. Have a great day!")],
            "current_step": END
        }
    
    if not state.get("messages"):
        print("No messages found, returning to process_name")
        return {"current_step": "process_name"}
    
    # Find the last human message
    last_human_message = None
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            last_human_message = message
            break
    
    if not last_human_message:
        print("No human message found, returning to process_name")
        return {"current_step": "process_name"}
    
    llm = get_llm()
    if not llm:
        print("LLM not available")
        return {
            "messages": [AIMessage(content="I apologize, but I'm having trouble processing your request. Please try again later.")],
            "current_step": END
        }
    
    # Simple sentiment analysis prompt
    sentiment_prompt = [
        SystemMessage(content="Analyze if the user agrees to schedule a consultation for tomorrow. Respond with only: POSITIVE, NEGATIVE, or UNCLEAR"),
        HumanMessage(content=last_human_message.content)
    ]
    
    try:
        print("Performing sentiment analysis...")
        sentiment_response = llm.invoke(sentiment_prompt)
        sentiment = sentiment_response.content.strip().upper()
        print(f"Sentiment detected: {sentiment}")
        
        # Increment attempt counter
        state["sentiment_attempts"] = attempts + 1
        
        if sentiment == "POSITIVE":
            return {
                "sentiment": "positive",
                "sentiment_attempts": state["sentiment_attempts"],
                "messages": [AIMessage(content=f"Great! I'll have Dave's Plumbing contact you to confirm the details. Have a great day!")],
                "current_step": END
            }
        elif sentiment == "NEGATIVE":
            return {
                "sentiment": "negative",
                "sentiment_attempts": state["sentiment_attempts"],
                "messages": [AIMessage(content="I understand. When would be a better time for you?")],
                "current_step": "reschedule"
            }
        else:
            if attempts >= 2:  # On third attempt, end gracefully
                return {
                    "sentiment": "unclear",
                    "sentiment_attempts": state["sentiment_attempts"],
                    "messages": [AIMessage(content="I'll have Dave's Plumbing contact you to discuss the scheduling details directly. Have a great day!")],
                    "current_step": END
                }
            return {
                "sentiment": "unclear",
                "sentiment_attempts": state["sentiment_attempts"],
                "messages": [AIMessage(content="I'm not sure if that's a yes or no. Would you like me to schedule the consultation for tomorrow?")],
                "current_step": "analyze_sentiment"
            }
    except Exception as e:
        print(f"Error in sentiment analysis: {str(e)}")
        return {
            "sentiment_attempts": state["sentiment_attempts"],
            "messages": [AIMessage(content="I'm having trouble understanding. Could you please answer with a simple yes or no?")],
            "current_step": "analyze_sentiment"
        }

def reschedule(state: WorkflowState) -> Dict:
    """Handle rescheduling requests"""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # After getting their preferred time, thank them and end
    response = "Thank you for letting me know. I'll have Dave's Plumbing contact you to confirm the details. Have a great day!"
    
    state["messages"].append(AIMessage(content=response))
    
    return {
        "current_step": END,
        "messages": state["messages"]
    }

def process_notes(state: WorkflowState) -> Dict:
    """Process any specific notes about the installation."""
    if not state.get("messages"):
        return {"current_step": "initialize"}
    
    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return {"current_step": "human_step"}
    
    # Store the notes (you could add them to a task dict if needed)
    notes = last_message.content
    
    response = "Thank you for providing those details. I've noted them for the installation team. "
    response += "That concludes our conversation. Dave's Plumbing will be in touch soon to schedule your installation. "
    response += "Have a great day!"
    
    state["messages"].append(AIMessage(content=response))
    
    return {
        "current_step": "end",
        "messages": state["messages"]
    }

def human_step(state: WorkflowState) -> Dict:
    """Get input from human and update messages."""
    human_input = input("Please enter your message (or press Enter to end): ")
    
    if not human_input.strip():
        return {"current_step": "__end__"}
    
    # Add the human message to current messages
    state["messages"].append(HumanMessage(content=human_input))
    
    # If we're expecting a name, go to process_name
    if state.get("current_step") == "initialize":
        return {"current_step": "process_name", "messages": state["messages"]}
    
    # If we're in scheduling, go to process_schedule
    if len(state["messages"]) > 1 and "schedule" in state["messages"][-2].content.lower():
        return {"current_step": "process_schedule", "messages": state["messages"]}
    
    # Default to process_name for other cases
    return {"current_step": "process_name", "messages": state["messages"]}

def create_workflow():
    """Create the workflow graph"""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("validate", validate_input)
    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("process_name", process_name)
    workflow.add_node("process_schedule", process_schedule)
    workflow.add_node("confirm_end", confirm_end)
    workflow.add_node("process_additional", process_additional)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("reschedule", reschedule)
    workflow.add_node("process_notes", process_notes)
    workflow.add_node("human_step", human_step)
    
    # Add edges with proper flow control
    workflow.set_entry_point("validate")
    workflow.add_edge("validate", "initialize")
    workflow.add_edge("initialize", "human_step")
    workflow.add_edge("human_step", "process_name")
    workflow.add_edge("process_name", "process_schedule")
    workflow.add_edge("process_schedule", "confirm_end")
    workflow.add_edge("confirm_end", "process_additional")
    workflow.add_edge("process_additional", "confirm_end")
    workflow.add_edge("process_schedule", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "reschedule")
    workflow.add_edge("analyze_sentiment", END)
    workflow.add_edge("human_step", "reschedule")
    workflow.add_edge("reschedule", END)
    workflow.add_edge("process_notes", "end")
    workflow.add_edge("end", END)
    
    return workflow.compile()

def main():
    """Run the workflow."""
    print("\nStarting workflow...")
    
    # Initialize state
    state = {
        "customer": {"name": None},
        "task": {
            "description": "Kitchen faucet installation",
            "schedule": None
        },
        "vendor": {
            "name": "Dave's Plumbing",
            "email": "dave@plumbing.com"
        },
        "messages": [],
        "sentiment": "neutral",
        "sentiment_attempts": 0
    }
    
    # Define the workflow graph
    workflow = {
        "validate": validate_input,
        "initialize": initialize_workflow,
        "process_name": process_name,
        "process_schedule": process_schedule,
        "confirm_end": confirm_end,
        "process_additional": process_additional,
        "analyze_sentiment": analyze_sentiment,
        "reschedule": reschedule,
        "process_notes": process_notes,
        "human_step": human_step
    }
    
    current_step = "validate"
    
    while current_step != "__end__":
        print(f"\nCurrent step: {current_step}")
        
        if current_step not in workflow:
            print(f"Error: Invalid step '{current_step}'")
            break
            
        try:
            # Execute the current step
            step_output = workflow[current_step](state)
            print(f"\nStep output: {step_output}")
            
            # Update state with step output
            for key, value in step_output.items():
                if key != "current_step":  # Don't update current_step here
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey in state:
                                if isinstance(state[subkey], list) and isinstance(subvalue, list):
                                    state[subkey].extend(subvalue)
                                elif isinstance(state[subkey], dict) and isinstance(subvalue, dict):
                                    state[subkey].update(subvalue)
                                else:
                                    state[subkey] = subvalue
                    else:
                        state[key] = value
            
            # Update current step
            if "current_step" in step_output:
                current_step = step_output["current_step"]
            
            # Print current messages for debugging
            print(f"\nCurrent messages: {[msg.content for msg in state['messages']]}")
            
        except Exception as e:
            print(f"Error in step '{current_step}': {str(e)}")
            break
    
    print("\nWorkflow completed.")

if __name__ == "__main__":
    main() 