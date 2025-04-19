

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
