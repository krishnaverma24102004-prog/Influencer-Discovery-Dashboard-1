import json
import logging
from typing import Dict, Any
from openai import OpenAI
import openai
import app_config as config

logger = logging.getLogger(__name__)

# Initialize OpenAI client with OpenRouter
if getattr(config, "OPENROUTER_API_KEY", ""):
    client = OpenAI(
        api_key=config.OPENROUTER_API_KEY,
        base_url=getattr(config, "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
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
            logger.error("LLM returned empty or null content.")
            return fallback_result
        
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            first_nl = content.find("\n")
            last_backticks = content.rfind("```")
            if first_nl != -1 and last_backticks != -1 and last_backticks > first_nl:
                content = content[first_nl:last_backticks].strip()
        
        # Robust JSON extraction
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        else:
            logger.error(f"Failed to find JSON structure in content.")
            return fallback_result
            
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {e}. Content snippet: {content[:100]}")
            return fallback_result
        
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

    except openai.APITimeoutError as e:
        logger.error(f"Network timeout while classifying '{name}': {e}")
        return fallback_result
    except openai.RateLimitError as e:
        logger.error(f"Rate limit or quota exceeded while classifying '{name}': {e}")
        return fallback_result
    except openai.APIConnectionError as e:
        logger.error(f"Network connection error while classifying '{name}': {e}")
        return fallback_result
    except openai.AuthenticationError as e:
        logger.error(f"Authentication error for '{name}': {e}")
        return fallback_result
    except openai.NotFoundError as e:
        logger.error(f"Model not found for '{name}': {e}")
        return fallback_result
    except openai.APIError as e:
        logger.error(f"OpenRouter API error for '{name}': {e.__class__.__name__} - {e}")
        return fallback_result
    except Exception as e:
        logger.exception(f"Unexpected error classifying '{name}': {e}")
        return fallback_result
