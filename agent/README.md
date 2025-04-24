more claude project directions:
- I am using bash.  I am using pip an requirements.txt, not poetry,
- I am using a venv ( 3.11 )
- my agent graph is in 007-workflow.py


# Contractor Workflow

A LangGraph workflow for connecting customers with vendors based on sentiment analysis.

## Features

- Customer and vendor management
- Task processing
- Sentiment analysis
- Conversation tracking

## Deployment

This project is designed to be deployed to LangSmith.

.....


# see .env-example

# Test locally from file
cd ~/gitl/lang-pz3
# python3.11 -m venv .venv_py311
source .venv_py311/bin/activate
# pip install -r requirements.txt
python agent/007-workflow.py

## poetry env use python3.11 && poetry run python agent/007-workflow.py


# to run workflow2.py locally in studio
poetry run langgraph dev
# starts this: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
# then paste input data from workflow2.py file into studio input.

# incorporate query-trace-filter-out-scanned.py
poetry run python query-langgraph.py

# Test in the cloud:
Deploy:
   https://smith.langchain.com/o/fa54f251-75d3-4005-8788-376a48b2c6c0/host/deployments
   https://github.com/ricgene/lang-pz3

https://smith.langchain.com/studio/thread


#later, separately - let's see
poetry run test-agent-local-studio-nostream.py