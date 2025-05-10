# Workflow Testing Instructions

This repository contains a workflow implementation for customer-vendor interactions. Here's how to run the tests:

## Setup

1. Make sure you have Python installed
2. Install the required packages:
```bash
pip install langgraph langchain-openai openai pytest
```

3. Set up your environment variables in a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Testing Options

### 1. Interactive Testing

Run the workflow interactively to test specific scenarios:

#### With Real LLM (Production Mode)
```bash
export MOCK_USER_RESPONSES=False
export MOCK_SENTIMENT_ANALYSIS=False
python agent/test_workflow2_local.py
```

#### With Mocking (Development Mode)
```bash
export MOCK_USER_RESPONSES=True
export MOCK_SENTIMENT_ANALYSIS=True
python agent/test_workflow2_local.py
```

### 2. Automated Testing with pytest

The test suite includes various test cases for sentiment analysis, workflow initialization, and error handling.

#### Run All Tests
```bash
pytest agent/test_workflow2_pytest.py -v
```

#### Run Only Mock Tests (No API Key Required)
```bash
pytest agent/test_workflow2_pytest.py -v -k "not test_llm"
```

#### Run Only LLM Tests (Requires API Key)
```bash
pytest agent/test_workflow2_pytest.py -v -k "test_llm"
```

#### Test Coverage
The test suite covers:
- Workflow initialization
- Sentiment analysis (both mock and LLM-based)
  - Positive responses ("yes", "I'll do it tomorrow", etc.)
  - Negative responses ("no", "I'm concerned about cost", etc.)
  - Ambiguous responses ("maybe", "I'll think about it")
- Full conversation flow
- Error handling for invalid inputs

### 3. Test Cases

#### Positive Sentiment Examples
- "yes"
- "I'll do it tomorrow"
- "sounds great"
- "will do"

#### Negative Sentiment Examples
- "no"
- "I can't right now"
- "I'm concerned about the cost"
- "the budget is too high"

#### Unknown Sentiment Examples
- "maybe"
- "I'll think about it"
- "can you provide more information"

## Environment Variables

- `MOCK_USER_RESPONSES`: When True, automatically generates user responses
- `MOCK_SENTIMENT_ANALYSIS`: When True, uses rule-based sentiment analysis instead of LLM
- `OPENAI_API_KEY`: Required when `MOCK_SENTIMENT_ANALYSIS` is False

## Development Workflow

1. Run mock tests during development:
```bash
export MOCK_SENTIMENT_ANALYSIS=True
pytest agent/test_workflow2_pytest.py -v -k "not test_llm"
```

2. Test specific scenarios interactively:
```bash
python agent/test_workflow2_local.py
```

3. Before deployment, run full test suite including LLM tests:
```bash
export MOCK_SENTIMENT_ANALYSIS=False
pytest agent/test_workflow2_pytest.py -v
```

## Cloud Deployment

Deploy to LangSmith:
1. Visit: https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
2. Connect to repository: https://github.com/ricgene/gitl/lang-pz3

## Local Studio Testing

Run workflow locally in LangSmith studio:
```bash
poetry run langgraph dev
```
This starts: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## Query Testing
```bash
poetry run python query-langgraph.py
```

# Test locally from file
cd ~/gitl/lang-pz3

See ~gitl/pz3/client-agent/README.md

poetry run python workflow2.py

# to run workflow2.py locally in studio
poetry run langgraph dev
# starts this: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 
# then paste input data from workflow2.py file into studio input.

# incorporate query-trace-filter-out-scanned.py
poetry run python query-langgraph.py

# Test in the cloud:
Deploy:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
   https://github.com/ricgene/gitl/lang-pz3

   # https://www.perplexity.ai/search/what-url-is-called-to-start-a-GXUl38JgQUSREB1WI_g5Tg

https://smith.langchain.com/studio/thread




#later, separately - let's see
poetry run test-agent-local-studio-nostream.py
