import logging
from typing import Dict, Any
import app_config as config

logger = logging.getLogger(__name__)

from utils.language_detection import detect_language

def evaluate_keywords(text: str) -> Dict[str, Any]:
    """
    Evaluates text against the predefined assignment keywords.
    Assigns a keyword score (0.0 to 1.0) based on matches.
    Also infers Language, Content Niche, and Political Orientation.
    """
    if not text:
        return {
            "score": 0.0, 
            "matched_keywords": [],
            "Language": "Unknown",
            "Content Niche": "Unknown",
            "Political Orientation": "Neutral"
        }
        
    text_lower = text.lower()
    matched = []
    
    for kw in config.KEYWORDS:
        if kw.lower() in text_lower:
            matched.append(kw)
            
    # Calculate score based on how many keywords matched.
    score = min(len(matched) / 3.0, 1.0) if matched else 0.0
    
    # Infer Language
    inferred_lang = detect_language(text)
    
    # Infer Niche
    niche_mapping = {
        "education": "Education",
        "healthcare": "Healthcare",
        "ayushman": "Healthcare",
        "startup": "Technology",
        "digital": "Technology",
        "upi": "Finance",
        "finance": "Finance",
        "infrastructure": "Government Schemes",
        "pmay": "Government Schemes",
        "bharat": "Government Schemes",
        "scheme": "Government Schemes"
    }
    
    inferred_niche = "Unknown"
    for kw in matched:
        for key, val in niche_mapping.items():
            if key in kw.lower():
                inferred_niche = val
                break
        if inferred_niche != "Unknown":
            break
            
    # If no specific niche found but matched government keywords
    if inferred_niche == "Unknown" and len(matched) > 0:
        inferred_niche = "Government Schemes"
        
    # Infer Political Orientation
    if len(matched) > 0:
        inferred_orientation = "Pro Government"
    else:
        inferred_orientation = "Neutral"
        
    # Calculate confidence score based on keyword coverage
    num_matches = len(matched)
    if num_matches >= 4:
        confidence = 90
    elif num_matches == 3:
        confidence = 75
    elif num_matches == 2:
        confidence = 60
    elif num_matches == 1:
        confidence = 40
    else:
        confidence = 10
        
    return {
        "score": round(score, 2),
        "matched_keywords": matched,
        "Language": inferred_lang,
        "Content Niche": inferred_niche,
        "Political Orientation": inferred_orientation,
        "Confidence Score": confidence
    }
