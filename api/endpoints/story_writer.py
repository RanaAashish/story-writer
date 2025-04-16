from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Union, Any
from core.config import Config
from scripts import (
    google_search,
    content_extractor,
    llm_processor,
)
import os
import json
from pathlib import Path
from pydantic import BaseModel, RootModel
from datetime import datetime

router = APIRouter()
config = Config()

def ensure_directories_exist():
    """Create all required data directories if they don't exist"""
    directories = [
        config.DATA_DIR
    ]  # Single directory only
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

class SearchQuery(BaseModel):
    query: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "Taj Mahal history"
            }
        }
    }

class StoryResponse(BaseModel):
    narration: str
    caption: str
    hashtags: str

class WebsiteResponse(RootModel[Dict[str, Union[StoryResponse, Dict[str, str]]]]):
    pass

@router.post("/fetch-websites", response_model=Dict[str, Any])
async def fetch_websites(search_query: SearchQuery):
    try:
        # Get the search query from the request body
        query = search_query.query
        
        # Generate timestamp-based filename for this search session
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"search_results_{timestamp}"
        
        # Ensure directories exist
        ensure_directories_exist()

        # Step 1: Search and get raw URLs
        raw_urls = google_search.search_places(query)
        raw_output_file = os.path.join(config.DATA_DIR, f"{base_filename}_raw.json")
        with open(raw_output_file, 'w') as f:
            json.dump({
                'query': query,
                'timestamp': timestamp,
                'urls': raw_urls
            }, f, indent=4)

        # Step 2: Extract content
        content_output_file = os.path.join(config.DATA_DIR, f"{base_filename}_content.json")
        content_data = content_extractor.extract_website_content(raw_urls, content_output_file)

        # Step 3: Process content with LLM
        structured_output_file = os.path.join(config.DATA_DIR, f"{base_filename}_story.json")
        llm_results = llm_processor.process_website_data(
            query,
            content_data,
            structured_output_file,
            config.OPENAI_API_KEY
        )

        response = llm_results
        with open(structured_output_file, 'w') as f:
            json.dump(response, f, indent=4)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

