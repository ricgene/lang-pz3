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

## Running Tests

### Interactive Testing

#### With Real LLM (Production Mode)
To run tests with the real OpenAI LLM:

```bash
export MOCK_USER_RESPONSES=False
export MOCK_SENTIMENT_ANALYSIS=False
python agent/test_workflow2_local.py
```

#### With Mocking (Development Mode)
To run tests with mock responses and rule-based sentiment analysis:

```bash
export MOCK_USER_RESPONSES=True
export MOCK_SENTIMENT_ANALYSIS=True
python agent/test_workflow2_local.py
```

### Automated Testing with pytest

Run the full test suite:
```bash
pytest agent/test_workflow2_pytest.py -v
```

Run only mock tests (no LLM calls):
```bash
pytest agent/test_workflow2_pytest.py -v -k "not test_llm"
```

Run only LLM tests:
```bash
pytest agent/test_workflow2_pytest.py -v -k "test_llm"
```

The test suite includes:
- Workflow initialization tests
- Mock sentiment analysis with various responses
- LLM-based sentiment analysis (requires API key)
- Full conversation flow tests
- Error handling tests

## Test Interaction

1. The test will start a conversation simulation
2. You can type responses to the prompts (or they will be auto-generated if mocking is enabled)
3. Type 'quit' to end the conversation

## Expected Behavior

The workflow will:
1. Initialize with test customer and vendor data
2. Present an initial greeting
3. Analyze sentiment of responses (using LLM or rules-based analysis)
4. Generate appropriate follow-up messages
5. Track conversation state and sentiment throughout

## Environment Variables

- `MOCK_USER_RESPONSES`: When True, automatically generates user responses
- `MOCK_SENTIMENT_ANALYSIS`: When True, uses rule-based sentiment analysis instead of LLM
- `OPENAI_API_KEY`: Required when `MOCK_SENTIMENT_ANALYSIS` is False

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
