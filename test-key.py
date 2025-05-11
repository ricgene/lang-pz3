import os
import requests

this is junk

api_key = "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"
#headers = {"x-api-key": api_key}

headers = {
    "Authorization": f"Bearer {api_key}"
}

url = "https://api.smith.langchain.com/api/whoami"
#url = f"https://api.smith.langchain.com/api/v1/me"

response = requests.get(url, headers=headers)
print(response.status_code, response.text)
