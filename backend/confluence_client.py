import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Confluence API configuration
BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
USERNAME = os.getenv("CONFLUENCE_USERNAME")
API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

def get_page_content(page_id):
    """
    Fetch the content of a Confluence page by its ID.
    """

    url = f"{BASE_URL}/rest/api/content/{page_id}?expand=body.storage"
    response = requests.get(url, auth=(USERNAME, API_TOKEN))
    data = response.json()
    html = data['body']['storage']['value']
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")

def get_all_page_ids(space_key):
    """
    Fetch all page IDs from a specific Confluence space.
    """
    
    url = f"{BASE_URL}/rest/api/content?spaceKey={space_key}&limit=10"
    response = requests.get(url, auth=(USERNAME, API_TOKEN))
    data = response.json()
    if 'results' not in data:
        raise KeyError("Missing 'results' key in response")
    return [p['id'] for p in data['results']]
