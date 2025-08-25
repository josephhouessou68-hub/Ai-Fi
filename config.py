import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # OpenAI API Key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # LangSmith API Key
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "langchain-trading")
    
    # API Keys
    POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    # Model Configuration
    OPENAI_MODEL = "gpt-4"
    TEMPERATURE = 0.1
    
    # API Endpoints
    POLYGON_BASE_URL = "https://api.polygon.io"
    NEWS_API_BASE_URL = "https://newsapi.org/v2"
    
    # Timeout settings
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def validate_config(cls):
        """Validate that required API keys are present"""
        required_keys = ["OPENAI_API_KEY"]
        missing_keys = [key for key in required_keys if not getattr(cls, key)]
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True
