import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = "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"

print(f"Using API key (first/last 5 chars): {api_key[:5]}...{api_key[-5:]}")

headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(
    "https://api.smith.langchain.com/api/v1/projects", 
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    projects = response.json()
    print(f"Found {len(projects)} projects:")
    for project in projects:
        print(f"  - Name: {project.get('name')}")
        print(f"    ID: {project.get('id')}")
        print(f"    Created: {project.get('created_at')}")
        print("    ---")
else:
    print(f"Error: {response.text}")