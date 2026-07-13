import logging
from typing import Optional
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)

# Map langdetect output to our assignment languages
LANGUAGE_MAPPING = {
    "en": "English",
    "hi": "Hindi"
}

def detect_language(text: str) -> str:
    """
    Detects the primary language of the given text using langdetect.
    Focuses only on English and Hindi as per assignment requirements.
    
    Args:
        text (str): The input text to analyze.
        
    Returns:
        str: "English", "Hindi", or "Unknown" if it cannot be detected or 
             is a language not supported by this assignment.
    """
    if not text or not str(text).strip():
        logger.debug("Empty text provided for language detection.")
        return "Unknown"
        
    try:
        # Detect the language code
        lang_code = detect(str(text))
        
        # Map code to readable language name
        detected_lang = LANGUAGE_MAPPING.get(lang_code, "Unknown")
        return detected_lang
        
    except LangDetectException as e:
        logger.warning(f"Language detection failed: {e}")
        return "Unknown"
    except Exception as e:
        logger.error(f"Unexpected error during language detection: {e}")
        return "Unknown"


def is_language_match(detected_language: str, target_language: str) -> bool:
    """
    Validates if the detected language matches the user's selected language filter.
    
    Args:
        detected_language (str): The language of the content (e.g. from detect_language).
        target_language (str): The user's requested language filter (e.g. "English", "Hindi", "All").
        
    Returns:
        bool: True if it matches or if "All" is selected, False otherwise.
    """
    if not target_language or target_language.lower() == "all":
        return True
        
    if not detected_language or detected_language == "Unknown":
        # If we can't detect it, it's safer to consider it a mismatch for strict filtering
        return False
        
    return detected_language.lower() == target_language.lower()
