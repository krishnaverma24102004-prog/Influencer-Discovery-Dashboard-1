import json
import os
import logging
from typing import List, Dict, Any
import hashlib

logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _get_cache_path(query: str) -> str:
    """Generate a unique file path for a given search query."""
    query_hash = hashlib.md5(query.lower().strip().encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f"{query_hash}.json")

def get_cached_search(query: str) -> List[Dict[str, Any]]:
    """Retrieve cached search results for a query if they exist."""
    path = _get_cache_path(query)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                logger.info(f"Loaded search results from cache for query: {query}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading cache for '{query}': {e}")
    return []

def set_cached_search(query: str, results: List[Dict[str, Any]]) -> None:
    """Save search results to cache."""
    path = _get_cache_path(query)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved search results to cache for query: {query}")
    except Exception as e:
        logger.error(f"Error writing cache for '{query}': {e}")
