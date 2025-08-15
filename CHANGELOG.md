# Changelog

## [0.1.0] - 2025-01-13

### Added

- Initial release of AutoLocalise Python SDK
- Framework-agnostic design (works with Django, Flask, FastAPI, etc.)
- Intelligent translation flow with server-side translation fetching
- Thread-safe in-memory caching with shared cache support
- Batch translation capabilities
- Graceful error handling with fallback to original text
- Simple callable interface: `t("Hello")`
- Comprehensive test suite with 27 test cases

### Features

- **Smart API Usage**: Only translates new strings, reuses existing translations
- **Shared Cache**: Multiple translator instances share global cache by default
- **Thread Safety**: Built with `threading.RLock()` for concurrent access
- **Configurable**: API key, languages, cache_ttl, cache settings
- **Error Resilient**: Network failures gracefully fallback to original text

### API

- `Translator(api_key, source_locale="en", target_locale="fr", cache_ttl=30, cache_enabled=True, shared_cache=True)`
- `translate(texts)` - Array-only translation (simplified API)
- `translate_batch(texts)` - Backward compatibility alias
- `clear_cache()` - Clear instance cache
- `clear_global_cache()` - Clear shared cache (class method)
- `cache_size()` - Get cache size
- `set_languages(source, target)` - Update languages

### Technical Details

- Python 3.7+ support
- Dependencies: `requests>=2.25.0`
- Thread-safe singleton pattern for global cache
- Comprehensive error handling with custom exception classes
- Ready for PyPI publishing
