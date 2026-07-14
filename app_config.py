import os
import logging
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Helper to get secrets securely in Streamlit
def get_secret(key, default=""):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
LOG_LEVEL = get_secret("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

# --------------------------------------------------
# API Configuration
# --------------------------------------------------

# OpenRouter
OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# LLM Model (Configurable)
LLM_MODEL = get_secret("OPENROUTER_MODEL", get_secret("LLM_MODEL", "openrouter/free"))

# Optional OpenRouter headers
APP_NAME = get_secret("OPENROUTER_APP_NAME", "AI Influencer Intelligence Platform")
SITE_URL = get_secret("OPENROUTER_SITE_URL", "http://localhost:8501")

# Search Provider
SERPAPI_API_KEY = get_secret("SERPAPI_API_KEY", "")

# --------------------------------------------------
# Cache Configuration
# --------------------------------------------------

CACHE_EXPIRY_HOURS = int(
    os.getenv("CACHE_EXPIRY_HOURS", 24)
)

# --------------------------------------------------
# Ranking Weights
# Total = 1.00
# --------------------------------------------------

WEIGHT_AI_CLASSIFICATION = 0.40
WEIGHT_KEYWORD_MATCH = 0.30
WEIGHT_LANGUAGE_MATCH = 0.20
WEIGHT_FOLLOWERS = 0.10

# --------------------------------------------------
# Supported Languages
# --------------------------------------------------

SUPPORTED_LANGUAGES = [
    "English",
    "Hindi"
]

# --------------------------------------------------
# Assignment Keywords
# --------------------------------------------------

KEYWORDS = [
    "Digital India",
    "Startup India",
    "Skill India",
    "Swachh Bharat",
    "PMAY",
    "Ayushman Bharat",
    "UPI",
    "Make in India",
    "Atmanirbhar Bharat",
    "Vocal for Local",
    "Infrastructure",
    "Education",
    "Healthcare",
    "Government Schemes",
    "National Development",
    "Government Initiative",
    "Policy",
    "India Development"
]

# --------------------------------------------------
# Search Providers
# --------------------------------------------------

SEARCH_PROVIDERS = [
    "SerpAPI",
    "DuckDuckGo",
    "CSV Upload",
    "Sample Dataset"
]

# --------------------------------------------------
# Validation
# --------------------------------------------------

if not OPENROUTER_API_KEY:
    logger.warning(
        "OPENROUTER_API_KEY is not configured. AI classification will be unavailable."
    )

if not SERPAPI_API_KEY:
    logger.warning(
        "SERPAPI_API_KEY is not configured. Live Google search will be skipped."
    )
