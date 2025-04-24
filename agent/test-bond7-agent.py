# test-bond7-agent.py
# A simple script to test the 007 productivity agent locally

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent workflow
try:
    from workflowbond7 import main as run_agent
except ImportError:
    print("Could not import from workflowbond7.py. Make sure the file exists in the current directory.")
    sys.exit(1)

def check_env():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in a .env file or in your environment.")
        print("You can use .env-example as a template.")
        return False
    
    return True

def main():
    """Main function to run the test"""
    print("\n🚀 Starting 007 Productivity Agent Test\n")
    
    # Check environment variables
    if not check_env():
        return
    
    # Run the agent
    try:
        run_agent()
    except Exception as e:
        print(f"\n❌ Error running agent: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()