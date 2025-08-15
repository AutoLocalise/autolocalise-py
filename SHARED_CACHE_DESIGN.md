# Shared Cache Design for AutoLocalise Python SDK

## Overview

The AutoLocalise Python SDK implements a sophisticated shared cache system that allows multiple translator instances to share translations across threads and processes, significantly improving performance in multi-threaded applications like web servers.

## Design Decisions

### ✅ **Shared Cache by Default (Recommended)**

```python
# Default behavior - all instances share the same cache
translator1 = Translator(api_key="key1")  # shared_cache=True by default
translator2 = Translator(api_key="key2")  # Uses same cache as translator1

# First translation hits API
result1 = translator1("Hello")  # API call + cache store

# Second translation hits shared cache - much faster!
result2 = translator2("Hello")  # Cache hit, no API call
```

**Benefits:**

- **Performance**: Eliminates redundant API calls across instances
- **Memory Efficient**: One cache for entire application
- **Thread Safe**: Built-in synchronization with `threading.RLock()`
- **Perfect for Web Apps**: Multiple requests can share translations

### **Independent Cache (Special Cases)**

```python
# Each instance has its own cache
translator1 = Translator(api_key="key1", shared_cache=False)
translator2 = Translator(api_key="key2", shared_cache=False)

# Each will make separate API calls even for same text
result1 = translator1("Hello")  # API call + instance cache
result2 = translator2("Hello")  # Another API call + separate cache
```

**Use Cases:**

- Testing environments where isolation is needed
- Applications requiring strict cache separation
- Debugging scenarios

## Implementation Details

### **Global Cache Singleton**

```python
# In cache.py
_global_cache = None
_global_cache_lock = threading.Lock()

def get_global_cache():
    """Thread-safe singleton pattern"""
    global _global_cache
    if _global_cache is None:
        with _global_cache_lock:
            if _global_cache is None:
                _global_cache = TranslationCache()
    return _global_cache
```

### **Cache Assignment Logic**

```python
# In translator.py __init__
if cache_enabled:
    if shared_cache:
        from .cache import get_global_cache
        self._cache = get_global_cache()  # Shared instance
    else:
        self._cache = TranslationCache()  # New instance
else:
    self._cache = None
```

### **Thread Safety**

The `TranslationCache` class uses `threading.RLock()` for all operations:

```python
class TranslationCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, str]] = {}
        self._lock = threading.RLock()  # Reentrant lock

    def get(self, text: str, source_lang: str, target_lang: str):
        with self._lock:
            # Thread-safe read operation

    def set(self, text: str, translation: str, source_lang: str, target_lang: str):
        with self._lock:
            # Thread-safe write operation
```

## Cache Management

### **Instance-Level Cache Clearing**

```python
translator = Translator(api_key="key", source="en", target="fr")
translator.clear_cache()  # Only clears en->fr translations from shared cache
```

### **Global Cache Clearing**

```python
Translator.clear_global_cache()  # Clears entire shared cache for all instances
```

### **Cache Size Monitoring**

```python
size = translator.cache_size()  # Returns total translations in cache
```

## Performance Benefits

### **Web Application Example**

```python
# Request 1
def handle_request_1():
    t = Translator(api_key="key")
    return t("Welcome")  # API call + cache store

# Request 2 (concurrent or later)
def handle_request_2():
    t = Translator(api_key="key")
    return t("Welcome")  # Cache hit - instant response!
```

### **Batch Processing Benefits**

```python
# Multiple workers processing different data
def worker_1():
    t = Translator(api_key="key")
    return t.translate_batch(["Hello", "World"])  # API calls + cache

def worker_2():
    t = Translator(api_key="key")
    return t.translate_batch(["Hello", "Goodbye"])  # "Hello" from cache!
```

## Memory Usage

- **Shared Cache**: O(unique_translations) memory usage
- **Independent Cache**: O(instances × unique_translations_per_instance)

For a web app with 100 concurrent requests translating the same 50 strings:

- **Shared**: ~50 cached translations
- **Independent**: ~5,000 cached translations (100× memory usage!)

## Testing Strategy

The SDK includes comprehensive tests for both cache modes:

```python
# Test shared cache behavior
def test_shared_cache_between_instances():
    t1 = Translator(api_key="key1", shared_cache=True)
    t2 = Translator(api_key="key2", shared_cache=True)

    assert t1._cache is t2._cache  # Same cache instance

# Test independent cache behavior
def test_independent_cache_instances():
    t1 = Translator(api_key="key1", shared_cache=False)
    t2 = Translator(api_key="key2", shared_cache=False)

    assert t1._cache is not t2._cache  # Different cache instances
```

## Recommendations

### ✅ **Use Shared Cache When:**

- Building web applications (Django, Flask, FastAPI)
- Multiple threads/processes need translations
- Performance and memory efficiency are important
- You want to minimize API calls

### ⚠️ **Use Independent Cache When:**

- Testing requires isolation between instances
- You need strict cache separation for security
- Debugging cache-related issues
- Building single-threaded applications with specific requirements

## Migration Guide

### **Opting Out of Shared Cache**

```python
# If you need the old isolated behavior
translator = Translator(api_key="key", shared_cache=False)
```

The shared cache design makes the AutoLocalise SDK highly efficient for production web applications while maintaining flexibility for special use cases.
