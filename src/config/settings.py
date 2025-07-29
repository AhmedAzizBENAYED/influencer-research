"""Configuration settings for the influencer research application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    # API Keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
    NOVADA_API_KEY = os.getenv("NOVADA_API_KEY")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    
    # Model configuration
    MODEL_NAME = "gemini-2.5-flash"
    MODEL_TEMPERATURE = 0.3  # Balance between creativity and consistency
    
    # Search configuration
    MAX_SEARCH_RESULTS = 10
    MIN_INFLUENCERS_REQUIRED = 15
    
    # Output configuration
    OUTPUT_DIR = "outputs"
    RECURSION_LIMIT = 75  # Increased for more thorough research
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        required_vars = [
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
            ("GOOGLE_API_KEY", cls.GOOGLE_API_KEY),
            ("NOVADA_API_KEY", cls.NOVADA_API_KEY),
            ("RAPIDAPI_KEY", cls.RAPIDAPI_KEY),
        ]
        
        missing_vars = [name for name, value in required_vars if not value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Create settings instance
settings = Settings()