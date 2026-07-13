import time
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Simple in-memory cache
_CACHE: Dict[str, Dict[str, Any]] = {}

def get_from_cache(key: str) -> Any:
    """Retrieve an item from cache if it hasn't expired."""
    if key in _CACHE:
        entry = _CACHE[key]
        if time.time() < entry['expiry']:
            logger.debug(f"Cache hit for key: {key}")
            return entry['data']
        else:
            logger.debug(f"Cache expired for key: {key}")
            del _CACHE[key]
    return None

def set_in_cache(key: str, data: Any, ttl_seconds: int = 3600) -> None:
    """Set an item in cache with a time-to-live (TTL) in seconds."""
    _CACHE[key] = {
        'data': data,
        'expiry': time.time() + ttl_seconds
    }
    logger.debug(f"Cache set for key: {key} (TTL: {ttl_seconds}s)")
