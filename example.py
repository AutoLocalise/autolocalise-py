#!/usr/bin/env python3
"""
Example usage of AutoLocalise Python SDK
"""

import time
from autolocalise import Translator


def main():
    print("AutoLocalise Python SDK Example - Cache Demonstration")
    print("=" * 60)

    # Track API calls to demonstrate cache behavior
    api_call_count = 0
    original_post = None

    def track_api_calls(*args, **kwargs):
        nonlocal api_call_count
        api_call_count += 1
        print(f"  📡 API Call #{api_call_count}")
        return original_post(*args, **kwargs)

    # Initialize translator
    # In production, use environment variables for API key
    translator = Translator(
        api_key="your-api-key-here",  # Replace with your actual API key
        source_locale="en",
        target_locale="fr",
    )

    # Patch the session.post method to track API calls
    original_post = translator._session.post
    translator._session.post = track_api_calls

    # First translation - should hit API
    print("\n1. First Translation (API Call Expected):")
    text = "Hello, world!"
    start_time = time.time()
    try:
        translations = translator([text])
        translated = translations[text]
        elapsed = (time.time() - start_time) * 1000
        print(f"  ✅ '{text}' -> '{translated}' ({elapsed:.1f}ms)")
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ Translation failed: {e}")

    # Same translation again - should hit cache
    print("\n2. Same Translation Again (Cache Hit Expected):")
    start_time = time.time()
    try:
        translations = translator([text])
        translated = translations[text]
        elapsed = (time.time() - start_time) * 1000
        print(f"  ⚡ '{text}' -> '{translated}' ({elapsed:.1f}ms) - FROM CACHE")
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ Translation failed: {e}")

    # New translations - should hit API
    print("\n3. New Translations (API Call Expected):")
    texts = ["Submit", "Cancel"]
    start_time = time.time()
    try:
        translations = translator.translate(texts)
        elapsed = (time.time() - start_time) * 1000
        print(f"  ✅ Batch translation completed ({elapsed:.1f}ms):")
        for original, translated in translations.items():
            print(f"    '{original}' -> '{translated}'")
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ Batch translation failed: {e}")

    # Mix of cached and new translations
    print("\n4. Mixed Translation (Some Cached, Some New):")
    mixed_texts = ["Hello, world!", "Submit", "Welcome", "Goodbye"]
    start_time = time.time()
    try:
        translations = translator.translate(mixed_texts)
        elapsed = (time.time() - start_time) * 1000
        print(f"  🔄 Mixed translation completed ({elapsed:.1f}ms):")
        for original, translated in translations.items():
            cache_status = (
                "FROM CACHE" if original in ["Hello, world!", "Submit"] else "FROM API"
            )
            print(f"    '{original}' -> '{translated}' ({cache_status})")
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ Mixed translation failed: {e}")

    # Language switching - cache is language-pair specific
    print("\n5. Language Switching (Different Cache):")
    translator.set_languages("en", "es")
    start_time = time.time()
    try:
        spanish_translations = translator(["Hello, world!"])
        spanish = spanish_translations["Hello, world!"]
        elapsed = (time.time() - start_time) * 1000
        print(
            f"  ✅ English to Spanish: 'Hello, world!' -> '{spanish}' ({elapsed:.1f}ms)"
        )
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ Spanish translation failed: {e}")

    # Back to French - should hit cache again
    print("\n6. Back to French (Cache Hit Expected):")
    translator.set_languages("en", "fr")
    start_time = time.time()
    try:
        french_translations = translator(["Hello, world!"])
        french = french_translations["Hello, world!"]
        elapsed = (time.time() - start_time) * 1000
        print(
            f"  ⚡ English to French: 'Hello, world!' -> '{french}' ({elapsed:.1f}ms) - FROM CACHE"
        )
        print(f"  📊 Cache size: {translator.cache_size()}")
    except Exception as e:
        print(f"  ❌ French translation failed: {e}")

    # Summary
    print(f"\n📈 Summary:")
    print(f"  Total API calls made: {api_call_count}")
    print(f"  Final cache size: {translator.cache_size()}")
    print(
        f"  Cache demonstrates significant performance improvement for repeated translations!"
    )


if __name__ == "__main__":
    main()
