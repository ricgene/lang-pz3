more claude project directions:
- I am using bash.  I am using pip an requirements.txt, not poetry,
- I am using a venv ( 3.11 )
- my agent graph is in 007-workflow.py


# Contractor Workflow

A LangGraph workflow for connecting customers with vendors based on sentiment analysis.

## Environment Setup

This project requires Python 3.11 and uses a virtual environment for dependency management.

# Agent Implementation

## Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv_py311
source .venv_py311/bin/activate  # On Windows: .venv_py311\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env-example` to `.env` and add your API keys:
```bash
cp .env-example .env
```

## Project Structure

### Latest Workflow
- `workflow_fixed.py` - The current, recommended workflow implementation that combines the best features from previous versions
  - Improved state management
  - Better error handling
  - Simplified sentiment analysis
  - Enhanced conversation flow

### Deprecated Files (For Reference)
- `workflow2.py` - Original workflow implementation
  - Useful for understanding the initial architecture
  - Contains basic sentiment analysis
  - Will be deprecated in favor of workflow_fixed.py

- `workflowbond7.py` - Intermediate workflow version
  - Introduced improved state management
  - Added more robust error handling
  - Will be deprecated in favor of workflow_fixed.py

## Features

- Customer and vendor management
- Task processing
- Sentiment analysis
- Conversation tracking
- State management
- Error handling

## Running the Workflow

### Local Development
```bash
# Activate the virtual environment
source .venv_py311/bin/activate

# Run the latest workflow
python agent/workflow_fixed.py
```

### LangSmith Studio
```bash
# Start LangSmith Studio locally
langgraph dev

# Access Studio at: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## Environment Variables

See `.env-example` for required environment variables.

## Deployment

This project is designed to be deployed to LangSmith.

### Cloud Deployment
- Deployment URL: https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
- Repository: https://github.com/ricgene/lang-pz3

## Testing

### Development Mode (Mock Responses)
```bash
export MOCK_SENTIMENT_ANALYSIS=True
pytest test_workflow2_pytest.py -v -k "not test_llm"
```

### Production Mode (Real LLM)
```bash
export MOCK_SENTIMENT_ANALYSIS=False
pytest test_workflow2_pytest.py -v
```

### Interactive Testing
```bash
python test_workflow2_local.py
```

## Query Testing
```bash
python query-langgraph.py
```

## Notes

- The project uses pip and requirements.txt for dependency management
- All development should be done in the Python 3.11 virtual environment
- The latest workflow implementation is in `workflow_fixed.py`
- Previous workflow versions are kept for reference but will be deprecated

# incorporate query-trace-filter-out-scanned.py
poetry run python query-langgraph.py

# Test in the cloud:
Deploy:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
   https://github.com/ricgene/lang-pz3

https://smith.langchain.com/studio/thread


#later, separately - let's see
poetry run test-agent-local-studio-nostream.py