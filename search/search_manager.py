import logging
import pandas as pd
from typing import Tuple, List, Dict, Any

from search.google_provider import search_google
from search.duckduckgo_provider import search_duckduckgo
from search.csv_provider import load_from_csv
from search.cache_provider import get_cached_search, set_cached_search

logger = logging.getLogger(__name__)

def execute_discovery(provider_func, base_query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    queries = [
        f"{base_query} influencer India",
        f"{base_query} creator India",
        f"{base_query} site:x.com OR site:twitter.com",
        f"{base_query} site:instagram.com",
        f"{base_query} site:youtube.com OR site:linkedin.com"
    ]
    
    logger.info(f"Expanded into {len(queries)} discovery queries.")
    
    all_results = []
    for q in queries:
        try:
            res = provider_func(q, num_results=10)
            all_results.extend(res)
        except Exception as e:
            logger.error(f"Error executing sub-query '{q}': {e}")
            
    logger.info(f"Retrieved {len(all_results)} raw search results.")
    
    if not all_results:
        return []
        
    # Deduplicate keeping highest confidence
    unique_profiles = {}
    for p in all_results:
        # Use platform + handle for social profiles, fallback to URL for Web
        if p['Handle'] != "Unknown":
            uid = f"{p['Platform']}_{p['Handle']}".lower()
        else:
            uid = p['Profile URL'].lower()
            
        if uid not in unique_profiles or p['_confidence'] > unique_profiles[uid]['_confidence']:
            unique_profiles[uid] = p
            
    deduped = list(unique_profiles.values())
    logger.info(f"Removed {len(all_results) - len(deduped)} duplicates/invalid webpages.")
    
    # Sort
    deduped.sort(key=lambda x: x["_confidence"], reverse=True)
    final = deduped[:num_results]
    
    for r in final:
        r.pop("_confidence", None)
        
    logger.info(f"Returning {len(final)} influencer profiles.")
    return final

def execute_search(query: str, uploaded_file_path: str = None) -> Tuple[pd.DataFrame, str]:
    """
    Executes search according to the priority:
    1. Uploaded CSV (if provided by user explicitly)
    2. Google (SerpAPI)
    3. DuckDuckGo
    4. Sample Dataset (Fallback)
    
    Returns a Tuple of (DataFrame containing results, String indicating Data Source).
    """
    
    # Priority 1: User explicitly uploaded a file (Independent Workflow)
    if uploaded_file_path:
        logger.info(f"Using uploaded file: {uploaded_file_path}")
        try:
            results = load_from_csv(uploaded_file_path)
            if results:
                return pd.DataFrame(results), "CSV Upload"
        except ValueError as ve:
            # Re-raise to show friendly error in UI
            raise ve
            
    # Priority 2 & 3: Live Search (if a query is provided)
    if query:
        # Check cache first to save API calls
        cached = get_cached_search(query)
        if cached:
            return pd.DataFrame(cached), "Cached Live Search"

        # Priority 2: Google (SerpAPI)
        logger.info("Attempting Google Search via SerpAPI...")
        results = execute_discovery(search_google, query)
        if results:
            set_cached_search(query, results)
            return pd.DataFrame(results), "SerpAPI"
            
        # Priority 3: DuckDuckGo Fallback
        logger.info("SerpAPI failed or empty. Attempting DuckDuckGo...")
        results = execute_discovery(search_duckduckgo, query)
        if results:
            set_cached_search(query, results)
            return pd.DataFrame(results), "DuckDuckGo"
            
        logger.warning("Live search failed or no valid profiles found. Falling back to local data...")

    # Priority 4: Built-in Sample Dataset (Absolute Fallback)
    logger.info("Using built-in sample dataset as fallback.")
    sample_path = "data/sample_influencers.csv"
    try:
        results = load_from_csv(sample_path)
    except ValueError:
        results = []
    return pd.DataFrame(results), "Sample Dataset"
