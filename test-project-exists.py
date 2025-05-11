import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = "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"
project_name = "prizm-workflow-2"

headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(
    f"https://api.smith.langchain.com/api/v1/projects/{project_name}", 
    headers=headers
)

print(f"Project check status: {response.status_code}")
if response.status_code == 200:
    project = response.json()
    print(f"✅ Project '{project_name}' exists!")
    print(f"Project ID: {project.get('id')}")
    print(f"Created: {project.get('created_at')}")
else:
    print(f"❌ Project '{project_name}' not found or access denied")
    print(f"Error: {response.text}")