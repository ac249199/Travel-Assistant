import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

# Google Maps configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

STAYAPI_API_KEY = os.getenv("STAYAPI_API_KEY")

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
RAILCORE_API_KEY = os.getenv("RAILCORE_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing")

if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY is missing")

if not STAYAPI_API_KEY:
    raise ValueError("STAYAPI_API_KEY is missing from .env")

