from typing import List, Union
import time
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from core.config import Config

def search_places(query: str, max_results: int = 10) -> List[str]:
    """Search for places using Google"""
    urls = []
    try:
        for url in search(
            query,
            num=max_results,
            stop=max_results,
            pause=2
        ):
            urls.append(url)
            if len(urls) >= max_results:
                break
            time.sleep(2)  # Added rate limiting
        return urls
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []

def get_content(url: str) -> Union[str, None]:
    """Get content from a URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get text content
        text = ' '.join([p.text.strip() for p in soup.find_all('p') if p.text.strip()])
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {str(e)}")
        return None