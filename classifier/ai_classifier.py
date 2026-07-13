import json
import logging
from typing import Dict, Any
import openai
import app_config as config

logger = logging.getLogger(__name__)

# Initialize OpenAI client with OpenRouter
if getattr(config, "OPENROUTER_API_KEY", ""):
    client = openai.OpenAI(
        base_url=getattr(config, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=config.OPENROUTER_API_KEY,
    )
else:
    client = None

import re
from classifier.keyword_classifier import evaluate_keywords

import streamlit as st

def get_fallback_result(name: str, bio: str, recent_posts: str) -> Dict[str, Any]:
    combined_text = f"{name} {bio} {recent_posts}"
    kw_data = evaluate_keywords(combined_text)
    return {
        "Language": kw_data.get("Language", "Unknown"),
        "Content Niche": kw_data.get("Content Niche", "Unknown"),
        "Political Orientation": kw_data.get("Political Orientation", "Neutral"),
        "Government Support": "Neutral",
        "Confidence Score": kw_data.get("Confidence Score", 0),
        "Reasoning": "🟡 Keyword Classification (AI unavailable)",
        "Classification Source": "Keyword Fallback"
    }

@st.cache_data(show_spinner=False, max_entries=200, ttl=3600)
def classify_influencer(name: str, bio: str, recent_posts: str) -> Dict[str, Any]:
    """
    Uses LLM via OpenRouter to classify the influencer based on assignment criteria.
    Returns JSON structure with Language, Content Niche, Political Orientation, 
    Government Support, Confidence Score, Reasoning, Classification Source.
    """
    fallback_result = get_fallback_result(name, bio, recent_posts)

    if not client:
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result

    prompt = f"""
Analyze the following influencer based on their bio and recent posts.
Name: {name}
Bio: {bio}
Recent Posts: {recent_posts}

Return ONLY valid JSON in the exact format below:
{{
  "Language": "",
  "Content Niche": "",
  "Political Orientation": "",
  "Government Support": "",
  "Confidence Score": 0,
  "Reasoning": ""
}}
"""
    try:
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=250,
            timeout=15.0,
            extra_headers={
                "HTTP-Referer": getattr(config, "SITE_URL", ""),
                "X-Title": getattr(config, "APP_NAME", ""),
            }
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("LLM returned empty or null content.")
        
        content = content.strip()
        
        # Robust JSON extraction
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
            
        result = json.loads(content)
        
        # Validate returned JSON and apply defaults for missing expected fields
        validated_result = {
            "Language": result.get("Language") or fallback_result["Language"],
            "Content Niche": result.get("Content Niche") or fallback_result["Content Niche"],
            "Political Orientation": result.get("Political Orientation") or fallback_result["Political Orientation"],
            "Government Support": result.get("Government Support") or fallback_result["Government Support"],
            "Reasoning": "🟢 AI Classification",
            "Classification Source": "AI"
        }
        
        # Ensure confidence score is strictly numeric
        try:
            score = result.get("Confidence Score", 0)
            validated_result["Confidence Score"] = int(score) if score is not None else 0
        except (ValueError, TypeError):
            validated_result["Confidence Score"] = fallback_result["Confidence Score"]
            
        logger.info("AI classification successful.")
        return validated_result

    except openai.APITimeoutError:
        logger.error(f"Network timeout while classifying '{name}'.")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except openai.RateLimitError:
        logger.error(f"Rate limit or quota exceeded while classifying '{name}'.")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except openai.APIConnectionError:
        logger.error(f"Network connection error while classifying '{name}'.")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except openai.APIError as e:
        logger.error(f"OpenRouter API error for '{name}': {e.__class__.__name__}")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except json.JSONDecodeError:
        logger.error("Invalid JSON received from LLM.")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except ValueError as e:
        logger.error(f"Validation error for '{name}': {str(e)}")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
    except Exception as e:
        logger.error(f"Unexpected error classifying '{name}': {e.__class__.__name__}")
        logger.warning("AI unavailable. Switching to keyword classifier.")
        return fallback_result
