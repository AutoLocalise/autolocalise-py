"""Tests for cache functionality and thread safety"""

from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

from autolocalise import Translator
from autolocalise.cache import TranslationCache, get_global_cache


class TestCacheBasics:
    """Test cases for basic cache operations"""

    def test_basic_operations(self):
        """Test basic cache operations"""
        cache = TranslationCache()

        # Initially empty
        assert cache.size() == 0
        assert cache.get("Hello", "en", "fr") is None

        # Set and get
        cache.set("Hello", "Bonjour", "en", "fr")
        assert cache.get("Hello", "en", "fr") == "Bonjour"
        assert cache.size() == 1

        # Different language pair
        cache.set("Hello", "Hola", "en", "es")
        assert cache.get("Hello", "en", "es") == "Hola"
        assert cache.get("Hello", "en", "fr") == "Bonjour"
        assert cache.size() == 2

    def test_batch_operations(self):
        """Test batch cache operations"""
        cache = TranslationCache()

        translations = {
            "Hello": "Bonjour",
            "Goodbye": "Au revoir",
            "Thank you": "Merci",
        }

        cache.set_batch(translations, "en", "fr")
        assert cache.size() == 3

        for english, french in translations.items():
            assert cache.get(english, "en", "fr") == french

    def test_batch_operations_with_eviction(self):
        """Test batch operations trigger eviction when cache is full"""
        cache = TranslationCache(max_size=5)

        # Fill cache to max size
        for i in range(5):
            cache.set(f"text_{i}", f"translation_{i}", "en", "fr")

        assert cache.size() == 5

        # Add batch that would exceed max size
        batch = {"new_1": "trans_1", "new_2": "trans_2"}
        cache.set_batch(batch, "en", "fr")

        # Should still be at max size (5 entries)
        assert cache.size() == 5

        # New entries should be present
        assert cache.get("new_1", "en", "fr") == "trans_1"
        assert cache.get("new_2", "en", "fr") == "trans_2"

        # Oldest entries should have been evicted
        assert cache.get("text_0", "en", "fr") is None
        assert cache.get("text_1", "en", "fr") is None

    def test_batch_operations_overwrite(self):
        """Test batch operations can overwrite existing entries"""
        cache = TranslationCache()

        # Set initial translations
        cache.set("Hello", "Bonjour", "en", "fr")
        cache.set("Goodbye", "Au revoir", "en", "fr")
        assert cache.size() == 2

        # Batch update with some new and some existing
        batch = {
            "Hello": "Salut",  # Overwrite
            "Thank you": "Merci",  # New
        }
        cache.set_batch(batch, "en", "fr")

        # Should have 3 entries (Goodbye + Hello + Thank you)
        assert cache.size() == 3

        # Hello should be updated
        assert cache.get("Hello", "en", "fr") == "Salut"
        # Goodbye should remain
        assert cache.get("Goodbye", "en", "fr") == "Au revoir"
        # Thank you should be new
        assert cache.get("Thank you", "en", "fr") == "Merci"

    def test_batch_operations_empty(self):
        """Test batch operations with empty dictionary"""
        cache = TranslationCache()

        cache.set("Hello", "Bonjour", "en", "fr")
        assert cache.size() == 1

        # Add empty batch
        cache.set_batch({}, "en", "fr")

        # Size should remain the same
        assert cache.size() == 1
        assert cache.get("Hello", "en", "fr") == "Bonjour"

    def test_clear_operations(self):
        """Test cache clearing operations"""
        cache = TranslationCache()

        # Add translations for multiple language pairs
        cache.set("Hello", "Bonjour", "en", "fr")
        cache.set("Hello", "Hola", "en", "es")
        cache.set("Goodbye", "Adiós", "en", "es")
        assert cache.size() == 3

        # Clear specific language pair
        cache.clear("en", "fr")
        assert cache.get("Hello", "en", "fr") is None
        assert cache.get("Hello", "en", "es") == "Hola"
        assert cache.size() == 2

        # Clear all
        cache.clear()
        assert cache.size() == 0

    def test_cache_key_generation(self):
        """Test cache key generation for different language pairs"""
        cache = TranslationCache()

        # Same text, different language pairs should be separate
        cache.set("Hello", "Bonjour", "en", "fr")
        cache.set("Hello", "Hola", "en", "es")
        cache.set("Hello", "Guten Tag", "en", "de")

        assert cache.get("Hello", "en", "fr") == "Bonjour"
        assert cache.get("Hello", "en", "es") == "Hola"
        assert cache.get("Hello", "en", "de") == "Guten Tag"
        assert cache.size() == 3

    def test_overwrite_existing(self):
        """Test overwriting existing translations"""
        cache = TranslationCache()

        cache.set("Hello", "Bonjour", "en", "fr")
        assert cache.get("Hello", "en", "fr") == "Bonjour"
        assert cache.size() == 1

        # Overwrite with new translation
        cache.set("Hello", "Salut", "en", "fr")
        assert cache.get("Hello", "en", "fr") == "Salut"
        assert cache.size() == 1  # Size shouldn't change


class TestCacheThreadSafety:
    """Test cases for cache thread safety"""

    def test_concurrent_cache_access(self):
        """Test concurrent access to cache from multiple threads"""
        cache = TranslationCache()
        results = []

        def worker(thread_id):
            # Each thread adds translations
            for i in range(100):
                text = f"text_{thread_id}_{i}"
                translation = f"translation_{thread_id}_{i}"
                cache.set(text, translation, "en", "fr")

            # Verify translations are accessible
            for i in range(100):
                text = f"text_{thread_id}_{i}"
                expected = f"translation_{thread_id}_{i}"
                actual = cache.get(text, "en", "fr")
                results.append(actual == expected)

        # Run multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            for future in futures:
                future.result()

        # All operations should have succeeded
        assert all(results)
        assert cache.size() == 500  # 5 threads * 100 translations each

    def test_global_cache_singleton(self):
        """Test that global cache is a proper singleton"""
        cache1 = get_global_cache()
        cache2 = get_global_cache()

        assert cache1 is cache2

        # Should be the same instance used by translators
        translator = Translator(
            api_key="test", source_locale="en", target_locale="fr"
        )
        assert translator._cache is cache1


class TestSharedCache:
    """Test cases for shared cache functionality"""

    def setup_method(self):
        """Clear global cache before each test"""
        Translator.clear_global_cache()

    def test_shared_cache_between_instances(self):
        """Test that multiple translator instances share the same cache"""
        # Create two translator instances
        t1 = Translator(
            api_key="test-key-1",
            source_locale="en",
            target_locale="fr",
        )
        t2 = Translator(
            api_key="test-key-2",
            source_locale="en",
            target_locale="fr",
        )

        # They should use the same cache instance
        assert t1._cache is t2._cache

        # Add translation via first instance
        t1._cache.set("Hello", "Bonjour", "en", "fr")

        # Second instance should see the same translation
        assert t2._cache.get("Hello", "en", "fr") == "Bonjour"

        # Cache size should be consistent
        assert t1.cache_size() == t2.cache_size() == 1

    def test_mixed_cache_modes(self):
        """Test that all instances share the same cache"""
        t1 = Translator(
            api_key="shared-1",
            source_locale="en",
            target_locale="fr",
        )
        t2 = Translator(
            api_key="shared-2",
            source_locale="en",
            target_locale="fr",
        )
        t3 = Translator(
            api_key="shared-3",
            source_locale="en",
            target_locale="fr",
        )

        # Add translation via first instance
        t1._cache.set("Hello", "Bonjour", "en", "fr")

        # All instances should see it
        assert t2._cache.get("Hello", "en", "fr") == "Bonjour"
        assert t3._cache.get("Hello", "en", "fr") == "Bonjour"

        # Cache sizes should be the same
        assert t1.cache_size() == t2.cache_size() == t3.cache_size() == 1

    def test_concurrent_shared_cache_access(self):
        """Test concurrent access to shared cache from multiple threads"""
        results = []

        def worker(thread_id):
            translator = Translator(
                api_key=f"key-{thread_id}",
                source_locale="en",
                target_locale="fr",
            )

            # Each thread adds some translations
            for i in range(10):
                text = f"text_{thread_id}_{i}"
                translation = f"translation_{thread_id}_{i}"
                translator._cache.set(text, translation, "en", "fr")

            # Verify translations are accessible
            for i in range(10):
                text = f"text_{thread_id}_{i}"
                expected = f"translation_{thread_id}_{i}"
                actual = translator._cache.get(text, "en", "fr")
                results.append(actual == expected)

            # Also check that we can see translations from other threads
            cache_size = translator.cache_size()
            results.append(cache_size >= 10)  # At least our own translations

        # Run multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            for future in futures:
                future.result()

        # All operations should have succeeded
        assert all(results)

        # Final cache should contain all translations
        final_translator = Translator(
            api_key="final", source_locale="en", target_locale="fr"
        )
        assert final_translator.cache_size() == 50  # 5 threads * 10 translations

    @patch("autolocalise.translator.requests.Session.post")
    def test_shared_cache_with_real_translations(self, mock_post):
        """Test shared cache with actual translation workflow"""
        # Mock API responses
        mock_post.side_effect = [
            # First translator initialization
            Mock(status_code=404),  # No existing translations
            # Second translator initialization
            Mock(status_code=404),  # No existing translations
            # First translator translate call
            Mock(
                status_code=200, json=lambda: {"translations": {"69609650": "Bonjour"}}
            ),  # Hash of "Hello"
            # Second translator calls - should hit cache, no API calls needed
        ]

        t1 = Translator(
            api_key="test-key-1",
            source_locale="en",
            target_locale="fr",
        )
        t2 = Translator(
            api_key="test-key-2",
            source_locale="en",
            target_locale="fr",
        )

        # First translation should hit API
        result1 = t1.translate(["Hello"])
        assert result1 == {"Hello": "Bonjour"}
        assert mock_post.call_count == 3  # 2 initialization calls + 1 translate call

        # Second translation should hit shared cache
        result2 = t2.translate(["Hello"])
        assert result2 == {"Hello": "Bonjour"}
        # Should still be 3 calls (no additional API calls)
        assert mock_post.call_count == 3

        # Both should show same cache size
        assert t1.cache_size() == t2.cache_size() == 1


class TestCacheOperations:
    """Test cases for cache management operations"""

    def setup_method(self):
        """Clear global cache before each test"""
        Translator.clear_global_cache()

    def test_cache_operations(self):
        """Test cache operations"""
        translator = Translator(
            api_key="test-key",
            source_locale="en",
            target_locale="fr",
        )

        # Initially empty
        assert translator.cache_size() == 0

        # Manually add to cache
        translator._cache.set("Hello", "Bonjour", "en", "fr")
        assert translator.cache_size() == 1

        # Clear cache
        translator.clear_cache()
        assert translator.cache_size() == 0

    def test_clear_cache_behavior(self):
        """Test different cache clearing behaviors"""
        t1 = Translator(
            api_key="key-1", source_locale="en", target_locale="fr"
        )
        t2 = Translator(
            api_key="key-2", source_locale="en", target_locale="es"
        )

        # Add translations for different language pairs
        t1._cache.set("Hello", "Bonjour", "en", "fr")
        t2._cache.set("Hello", "Hola", "en", "es")

        assert t1.cache_size() == 2  # Both language pairs

        # Clear cache for specific instance (only its language pair)
        t1.clear_cache()

        # Should only clear en->fr, not en->es
        assert t1._cache.get("Hello", "en", "fr") is None
        assert t1._cache.get("Hello", "en", "es") == "Hola"
        assert t1.cache_size() == 1

        # Clear entire global cache
        Translator.clear_global_cache()
        assert t1.cache_size() == 0
        assert t2.cache_size() == 0
