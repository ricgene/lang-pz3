import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Run the 007 Agent")
    parser.add_argument("--mocked", action="store_true", 
                        help="Run with mocked models instead of real API calls")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Set the environment variable based on the flag
    if args.mocked:
        os.environ["MOCK_MODE"] = "True"
        print("🚀 Starting 007 Productivity Agent with Mocked Implementation")
        print("=== 007 Productivity Agent (Mocked Mode) ===")
        print("Using predefined inputs for testing. Type your own inputs when mocked inputs run out.")
    else:
        os.environ["MOCK_MODE"] = "False"
        print("🚀 Starting 007 Productivity Agent with OpenAI Integration")
        print("=== 007 Productivity Agent (Live Mode) ===")
        print("Using real OpenAI API for all model calls.")