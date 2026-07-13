import logging
import requests
import re
import urllib.parse
from typing import List, Dict, Any
import app_config as config

logger = logging.getLogger(__name__)

def is_social_profile(url: str) -> bool:
    url_lower = url.lower()
    rejects = [
        ".gov.in", "nic.in", "wikipedia.org", "medium.com", "blog",
        "news", "article", "press", ".pdf", "docs", "github.com",
        "reddit.com", "quora.com", "stackoverflow.com", "/search", 
        "/tag", "/category"
    ]
    for r in rejects:
        if r in url_lower:
            return False
            
    if re.search(r'https?://(www\.)?(x\.com|twitter\.com)/[\w_]+/?$', url_lower):
        return True
    if re.search(r'https?://(www\.)?instagram\.com/[\w_\.]+/?$', url_lower):
        return True
    if re.search(r'https?://(www\.)?youtube\.com/(@[\w_-]+|channel/[\w_-]+)/?$', url_lower):
        return True
    if re.search(r'https?://(www\.)?linkedin\.com/(in|company)/[\w_-]+/?$', url_lower):
        return True
        
    return False

def get_profile_confidence(url: str) -> int:
    url_lower = url.lower()
    if "twitter.com/" in url_lower or "x.com/" in url_lower:
        return 100
    if "instagram.com/" in url_lower:
        return 95
    if "youtube.com/@" in url_lower:
        return 90
    if "linkedin.com/in/" in url_lower:
        return 85
    if "youtube.com/channel/" in url_lower:
        return 70
    if "linkedin.com/company/" in url_lower:
        return 60
    return 20

def clean_name(title: str) -> str:
    name = re.split(r'\||-|(@|\()', title)[0].strip()
    if not name or len(name.split()) > 5:
        return ""
    if "://" in name or ".com" in name or ".in" in name:
        return ""
    return name

def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "twitter.com" in url_lower: return "Twitter"
    if "x.com" in url_lower: return "X"
    if "instagram.com" in url_lower: return "Instagram"
    if "youtube.com" in url_lower: return "YouTube"
    if "linkedin.com" in url_lower: return "LinkedIn"
    return "Web"

def extract_handle(url: str, platform: str) -> str:
    try:
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.strip('/')
        parts = path.split('/')
        if not parts or not parts[0]:
            return "Unknown"
            
        if platform in ["X", "Twitter", "Instagram"]:
            return f"@{parts[0]}"
        elif platform == "YouTube":
            if parts[0].startswith('@'):
                return parts[0]
            elif parts[0] == "channel" and len(parts) > 1:
                return parts[1]
        elif platform == "LinkedIn":
            if parts[0] in ["in", "company"] and len(parts) > 1:
                return parts[1]
    except Exception:
        pass
    return "Unknown"

def search_google(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches raw search results for a specific query variation and returns valid candidate profiles.
    """
    if not config.SERPAPI_API_KEY:
        return []
        
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": config.SERPAPI_API_KEY,
        "engine": "google",
        "num": num_results * 2
    }
    
    results = []
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        for item in data.get("organic_results", []):
            link = item.get("link", "")
            if not link or not is_social_profile(link):
                continue
                
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            
            name = clean_name(title)
            if not name:
                continue
                
            platform = detect_platform(link)
            handle = extract_handle(link, platform)
            confidence = get_profile_confidence(link)
            
            results.append({
                "Name": name,
                "Handle": handle,
                "Platform": platform, 
                "Profile URL": link,
                "Followers": 0,
                "Language": "Unknown",
                "Bio": snippet,
                "Recent Posts": "",
                "_confidence": confidence
            })
            
        return results
    except Exception:
        return []
