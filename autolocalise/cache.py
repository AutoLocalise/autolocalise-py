"""In-memory cache for translations"""

import threading
from typing import Dict, Optional


# Global shared cache instance
_global_cache = None
_global_cache_lock = threading.Lock()


def get_global_cache():
    """Get or create the global shared cache instance"""
    global _global_cache
    if _global_cache is None:
        with _global_cache_lock:
            if _global_cache is None:
                _global_cache = TranslationCache()
    return _global_cache


class TranslationCache:
    """Thread-safe in-memory cache for translations"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, str]] = {}
        self._lock = threading.RLock()

    def _get_cache_key(self, source_lang: str, target_lang: str) -> str:
        """Generate cache key for language pair"""
        return f"{source_lang}:{target_lang}"

    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Get translation from cache"""
        cache_key = self._get_cache_key(source_lang, target_lang)

        with self._lock:
            lang_cache = self._cache.get(cache_key, {})
            return lang_cache.get(text)

    def set(self, text: str, translation: str, source_lang: str, target_lang: str):
        """Store translation in cache"""
        cache_key = self._get_cache_key(source_lang, target_lang)

        with self._lock:
            if cache_key not in self._cache:
                self._cache[cache_key] = {}
            self._cache[cache_key][text] = translation

    def set_batch(
        self, translations: Dict[str, str], source_lang: str, target_lang: str
    ):
        """Store multiple translations in cache"""
        cache_key = self._get_cache_key(source_lang, target_lang)

        with self._lock:
            if cache_key not in self._cache:
                self._cache[cache_key] = {}
            self._cache[cache_key].update(translations)

    def clear(
        self, source_lang: Optional[str] = None, target_lang: Optional[str] = None
    ):
        """Clear cache for specific language pair or all"""
        with self._lock:
            if source_lang and target_lang:
                cache_key = self._get_cache_key(source_lang, target_lang)
                self._cache.pop(cache_key, None)
            else:
                self._cache.clear()

    def size(self) -> int:
        """Get total number of cached translations"""
        with self._lock:
            return sum(len(lang_cache) for lang_cache in self._cache.values())
