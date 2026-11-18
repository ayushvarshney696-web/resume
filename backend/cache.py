"""Thread-safe LRU in-memory cache for analysis results."""

import hashlib
import threading
from collections import OrderedDict
from typing import Optional, Any
from models import AnalysisResult
from config import CACHE_MAX_SIZE

class AnalysisCache:
    """
    Thread-safe Least-Recently-Used (LRU) cache for resume analysis results.
    Prevents redundant LLM and regex processing for identical queries.
    """
    def __init__(self, maxsize: int = CACHE_MAX_SIZE):
        self._maxsize = maxsize
        self._cache: OrderedDict[str, AnalysisResult] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def compute_key(
        text: str,
        role: str,
        description: str,
        persona: str,
        api_key: Optional[str] = None
    ) -> str:
        """Compute SHA-256 fingerprint from query parameters."""
        hasher = hashlib.sha256()
        hasher.update(text.strip().encode("utf-8"))
        hasher.update(role.strip().lower().encode("utf-8"))
        hasher.update(description.strip().lower().encode("utf-8"))
        hasher.update(persona.strip().lower().encode("utf-8"))
        if api_key:
            hasher.update(api_key.strip().encode("utf-8"))
        return hasher.hexdigest()

    def get(self, key: str) -> Optional[AnalysisResult]:
        """Retrieve cached result and update LRU position."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._hits += 1
                return self._cache[key]
            self._misses += 1
            return None

    def put(self, key: str, value: AnalysisResult) -> None:
        """Store result in cache, evicting oldest item if maxsize exceeded."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def stats(self) -> dict:
        """Return cache performance statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_ratio = (self._hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "maxsize": self._maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": round(hit_ratio, 3)
            }

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

analysis_cache = AnalysisCache()
