import requests
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="api_requests.log",  # Log file
    level=logging.INFO,  # Log level (INFO, ERROR, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

def make_prompt(prompt, purpose):
    api_key = os.getenv('API_KEY')    
    url = "http://localhost:3000/api/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-r1:1.5b",
        "messages": [
            {"role": "system", "content": f"{purpose}"},
            {"role": "user", "content": f"{prompt}"}
        ],
        "stream": False
    }

    logging.info(f"Sending request to {url} with payload: {data}")

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise exception for HTTP errors

        content = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        logging.info(f"Received response: {content}")

        return content.encode("utf-8", errors="replace")

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None
