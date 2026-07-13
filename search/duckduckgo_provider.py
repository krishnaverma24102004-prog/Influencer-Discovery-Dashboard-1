import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

from search.google_provider import (
    clean_name, detect_platform, extract_handle, 
    is_social_profile, get_profile_confidence
)

def search_duckduckgo(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches raw search results for a specific query variation and returns valid candidate profiles.
    """
    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    data = {"q": query}
    
    results = []
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for result in soup.find_all('div', class_='result'):
            title_tag = result.find('a', class_='result__url')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                link = title_tag.get('href', '')
                if not link or not is_social_profile(link):
                    continue
                    
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True)
                
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
