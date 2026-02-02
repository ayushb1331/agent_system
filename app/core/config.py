import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "dummy_key")
    GEMINI_MODEL: str = "gemini-2.0-flash"
    # NEW: Toggle this to True for testing without API calls
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() == "true"

settings = Settings()