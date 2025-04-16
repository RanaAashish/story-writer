import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
import tiktoken
from core.config import Config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import re

def count_tokens(text: str) -> int:
    """Count tokens in the given text using GPT-4 tokenizer"""
    try:
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

# Step 2: Generate story using an LLM
def generate_story_prompt(location: str,data: str, language="hi"):
    prompt = f"""
    Based on the following information about {location}, create a short, engaging story script for an Instagram Reel (30-60 seconds). The story should be vivid, emotional, and culturally resonant, capturing the essence of the location for a travel audience. Focus on sensory details (sights, sounds, feelings) and a narrative arc that inspires viewers to visit or connect with the place. Output in {language} (Hindi).

    Data: {data}

    Format:
    {{
        "narration": "The story text, concise and rhythmic, suitable for voice-over in a 30-60 second reel",
        "caption": "A short, catchy caption for the reel",
        "hashtags": "Relevant hashtags (e.g., #TravelIndia, #{location})"
    }}

    Instructions:
    1. Keep the narration vivid, emotional, and under 100 words for brevity.
    2. Highlight cultural, historical, or natural elements of {location}.
    3. Ensure the caption is engaging and encourages interaction (e.g., 'Have you visited?').
    4. Include 4-6 hashtags relevant to travel and the location.
    5. If data is limited, use general knowledge about {location} to enrich the story.
    """
    
    
    return prompt

def chat_completion(query: str, content: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured information from website content using OpenAI API
    
    Args:
        query: The query or location name
        content: Raw website content
        api_key: OpenAI API key
    
    Returns:
        Dictionary containing structured information or None if extraction fails
    """
    try:
        client = OpenAI(api_key=api_key)
        
        prompt = generate_story_prompt(query, content)
        token_count = count_tokens(prompt)
        
        if token_count > 128000:
            print(f"Warning: Content too long ({token_count} tokens). Truncating...")
            content = content[:int(len(content) * (128000 / token_count))]
            prompt = generate_story_prompt(query, content)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert story writer. Generate a story about the place and return the response as a JSON object with 'narration(250 words)', 'caption', and 'hashtags' fields."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\nPlease return the response in JSON format."
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}  # Explicitly set JSON response format
        )
        
        try:
            extracted_info = json.loads(response.choices[0].message.content)
            return extracted_info
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return None

def process_website_data(query:str, input_data:Dict, output_file: str, api_key: str) -> Dict[str, Any]:
    """
    Process website content and extract structured information
    
    Args:
        input_data: Either path to input JSON file or dictionary containing website content
        output_file: Path to save extracted information
        api_key: OpenAI API key
    
    Returns:
        Dictionary containing processed results
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Handle input data
        if isinstance(input_data, str):
            with open(input_data, 'r', encoding='utf-8') as f:
                website_data = json.load(f)
        else:
            website_data = input_data
        
        print(f"Processing {len(website_data)} websites...")
        
        # Extract information for each website
        parsed_results = {}
        for url, content in website_data.items():
            print(f"\nProcessing: {url}")
            
            # Skip if content has error
            if isinstance(content, dict) and 'error' in content:
                print(f"Skipping due to previous error: {content['error']}")
                parsed_results[url] = {"error": content['error']}
                continue
            
            # Combine all text content for processing
            combined_content = ""
            if isinstance(content, dict):
                combined_content = f"Title: {content.get('title', '')}\n"
                combined_content += f"Description: {content.get('meta_description', '')}\n"
                combined_content += "Headers:\n" + "\n".join(content.get('h1_headers', []) + content.get('h2_headers', [])) + "\n"
                combined_content += "Content:\n" + "\n".join(content.get('paragraphs', []))
            
            # Extract structured information
            response = chat_completion(query,combined_content, api_key)
            if response:
                parsed_results[query] = response
            else:
                parsed_results[query] = {"error": "Failed to generate story"}
        
        # Save results in two formats
        # 1. JSON file (for API)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, indent=2, ensure_ascii=False)
            
        # 2. Text file (for readable Hindi)
        txt_output_file = output_file.replace('.json', '.txt')
        with open(txt_output_file, 'w', encoding='utf-8') as f:
            for location, content in parsed_results.items():
                if isinstance(content, dict) and 'error' not in content:
                    f.write(f"Location: {location}\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"Narration:\n{content.get('narration', '')}\n\n")
                    f.write(f"Caption:\n{content.get('caption', '')}\n\n")
                    f.write(f"Hashtags:\n{content.get('hashtags', '')}\n")
                    f.write("=" * 50 + "\n\n")
        
        print(f"\nProcessing complete. Results saved to:")
        print(f"- JSON: {output_file}")
        print(f"- Text: {txt_output_file}")
        
        return parsed_results
    
    except Exception as e:
        print(f"Error processing website data: {str(e)}")
        return {}