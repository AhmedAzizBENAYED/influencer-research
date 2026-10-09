"""Application settings loaded from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration. Secrets come from the environment / `.env` file."""

    # API keys
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    NOVADA_API_KEY = os.getenv("NOVADA_API_KEY")
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

    # Models
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    MODEL_TEMPERATURE = 0.3
    EMAIL_MODEL_NAME = os.getenv("EMAIL_MODEL_NAME", "gemini-2.0-flash")

    # Research
    MAX_SEARCH_RESULTS = 10
    MIN_INFLUENCERS_REQUIRED = 15
    RECURSION_LIMIT = 75

    # Output
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

    # Email outreach (optional)
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    # Safety net: generated emails are delivered here instead of to the influencer
    OUTREACH_TEST_RECIPIENT = os.getenv("OUTREACH_TEST_RECIPIENT") or EMAIL_USER

    @classmethod
    def validate(cls):
        """Raise if a required API key is missing."""
        required_vars = [
            ("TAVILY_API_KEY", cls.TAVILY_API_KEY),
            ("GOOGLE_API_KEY", cls.GOOGLE_API_KEY),
            ("NOVADA_API_KEY", cls.NOVADA_API_KEY),
            ("RAPIDAPI_KEY", cls.RAPIDAPI_KEY),
        ]
        missing_vars = [name for name, value in required_vars if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


settings = Settings()
