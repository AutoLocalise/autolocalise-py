"""Tests for core Translator functionality"""

import pytest
from unittest.mock import Mock, patch

from autolocalise import Translator
from autolocalise.exceptions import ConfigurationError


class TestTranslatorCore:
    """Test cases for core Translator functionality"""

    def setup_method(self):
        """Clear global cache before each test"""
        Translator.clear_global_cache()

    def test_init_with_required_params(self):
        """Test translator initialization with required parameters"""
        translator = Translator(
            api_key="test-key", source_locale="en", target_locale="fr"
        )
        assert translator.api_key == "test-key"
        assert translator.source == "en"
        assert translator.target == "fr"

    def test_init_with_all_params(self):
        """Test translator initialization with all parameters"""
        translator = Translator(
            api_key="test-key",
            source_locale="es",
            target_locale="de",
        )
        assert translator.api_key == "test-key"
        assert translator.source == "es"
        assert translator.target == "de"
        # assert translator.base_url == "https://autolocalise-main-53fde32.zuplo.app"
        assert translator.timeout == 30

    def test_init_without_api_key(self):
        """Test that initialization fails without API key"""
        with pytest.raises(ConfigurationError):
            Translator(api_key="", source_locale="en", target_locale="fr")

    def test_init_without_source_locale(self):
        """Test that initialization fails without source locale"""
        with pytest.raises(ConfigurationError):
            Translator(api_key="test-key", source_locale="", target_locale="fr")

    def test_init_without_target_locale(self):
        """Test that initialization fails without target locale"""
        with pytest.raises(ConfigurationError):
            Translator(api_key="test-key", source_locale="en", target_locale="")

    def test_set_languages(self):
        """Test changing source and target languages"""
        translator = Translator(
            api_key="test-key", source_locale="en", target_locale="fr"
        )

        translator.set_languages("es", "de")
        assert translator.source == "es"
        assert translator.target == "de"

    def test_cache_is_always_enabled(self):
        """Test that cache is always enabled"""
        translator = Translator(
            api_key="test-key",
            source_locale="en",
            target_locale="fr",
        )

        assert translator._cache is not None
        assert translator.cache_size() >= 0

    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text"""
        translator = Translator(
            api_key="test-key", source_locale="en", target_locale="fr"
        )

        assert translator.translate([""]) == {"": ""}
        assert translator.translate(["   "]) == {"   ": "   "}
        assert translator.translate(["", "   "]) == {"": "", "   ": "   "}

    def test_invalid_text_types(self):
        """Test handling of invalid text types (non-strings)"""
        translator = Translator(
            api_key="test-key", source_locale="en", target_locale="fr"
        )

        # Non-string types should be skipped
        assert translator.translate([123, None, [], {}]) == {}

        # Mixed valid and invalid text
        result = translator.translate(["Hello", 123, "World", None])
        assert result == {
            "Hello": "Hello",
            "World": "World",
        }  # Fallback to original on API error

    def test_callable_interface(self):
        """Test that translator can be called directly"""
        with patch("autolocalise.translator.requests.Session.post") as mock_post:
            mock_post.side_effect = [
                Mock(status_code=404),
                Mock(
                    status_code=200,
                    json=lambda: {
                        "translations": {"69609650": "Bonjour"}  # Hash of "Hello"
                    },
                ),
            ]

            translator = Translator(
                api_key="test-key",
                source_locale="en",
                target_locale="fr",
            )
            result = translator(["Hello"])

            assert result == {"Hello": "Bonjour"}
