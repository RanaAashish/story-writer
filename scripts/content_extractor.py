from typing import Dict, List, Union
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse
import logging
from fake_useragent import UserAgent

def extract_website_content(urls_input: Union[str, List[str]], output_file: str) -> Dict[str, Dict]:
    """
    Extract content from websites
    
    Args:
        urls_input: Either a path to file containing URLs (one per line) or a list of URLs
        output_file: Path where extracted content will be saved as JSON
    
    Returns:
        Dict[str, Dict]: Dictionary with URLs as keys and extracted content as values
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize user agent rotator
    ua = UserAgent()
    
    # Handle input: either file path or list of URLs
    if isinstance(urls_input, str):
        # Read URLs from file
        with open(urls_input, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    else:
        # Use provided list of URLs
        urls = urls_input
    
    extracted_content = {}
    
    for url in urls:
        try:
            # Rotate user agent and add headers
            headers = {
                'User-Agent': ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            # Make request
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract relevant content
            content = {
                'title': soup.title.string if soup.title else None,
                'meta_description': soup.find('meta', {'name': 'description'}).get('content') if soup.find('meta', {'name': 'description'}) else None,
                'h1_headers': [h1.text.strip() for h1 in soup.find_all('h1')],
                'h2_headers': [h2.text.strip() for h2 in soup.find_all('h2')],
                'paragraphs': [p.text.strip() for p in soup.find_all('p') if p.text.strip()],
                'domain': urlparse(url).netloc
            }
            
            extracted_content[url] = content
            logger.info(f"Successfully extracted content from {url}")
            
            # Be polite with delays
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            extracted_content[url] = {'error': str(e)}
    
    # Save results to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_content, f, indent=4, ensure_ascii=False)
    
    return extracted_content
