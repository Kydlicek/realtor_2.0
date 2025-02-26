import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def make_prompt(prompt,purpose):

    api_key=os.getenv('API_KEY')    
    # API endpoint
    url = "http://localhost:3000/api/chat/completions"

    # Headers
    headers = {
        "Authorization": f"Bearer {api_key}",  # Replace with your actual API key
        "Content-Type": "application/json"
    }

    # Request payload
    data = {
        "model": "llama3.2:1b",
        "messages": [
            {
                "role": "system",
                "content": f"{purpose}"
            },
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        "stream": False
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

