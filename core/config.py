import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    def __init__(self):
        # Validate required environment variables
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Base paths
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        
        # Ensure data directory exists
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
        # Flask Configuration
        self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
        self.DEBUG = os.environ.get('FLASK_DEBUG', False)

        # Directories
        self.PACKAGE_ROOT = Path(__file__).parent.parent

        # Search Configuration
        self.SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", 10))
        self.MAX_SEARCH_RESULTS = int(os.getenv("MAX_RESULTS", 100))
        self.SEARCH_DELAY = int(os.getenv("SEARCH_DELAY", 2))
        self.SEARCH_COUNTRY = "IN"
        self.SEARCH_LANGUAGE = "en"
