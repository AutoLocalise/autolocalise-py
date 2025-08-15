"""Tests for core Translator functionality"""

import pytest
import requests
from unittest.mock import Mock, patch

from autolocalise import Translator
from autolocalise.exceptions import APIError, NetworkError, ConfigurationError


class TestTranslatorCore:
    """Test cases for core Translator functionality"""
    
    def setup_method(self):
        """Clear global cache before each test"""
        Translator.clear_global_cache()
    
    def test_init_with_required_params(self):
        """Test translator initialization with required parameters"""
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr")
        assert translator.api_key == "test-key"
        assert translator.source == "en"
        assert translator.target == "fr"
        assert translator.cache_enabled is True
    
    def test_init_with_all_params(self):
        """Test translator initialization with all parameters"""
        translator = Translator(
            api_key="test-key",
            source_locale="es",
            target_locale="de",
            cache_ttl=60,
            cache_enabled=False,
            shared_cache=False
        )
        assert translator.api_key == "test-key"
        assert translator.source == "es"
        assert translator.target == "de"
        # assert translator.base_url == "https://autolocalise-main-53fde32.zuplo.app"
        assert translator.timeout == 60
        assert translator.cache_enabled is False
        assert translator.shared_cache is False
    
    def test_init_without_api_key(self):
        """Test that initialization fails without API key"""
        with pytest.raises(ConfigurationError):
            Translator(api_key="", source_locale="en", target_locale="fr")
    
    def test_set_languages(self):
        """Test changing source and target languages"""
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr")
        
        translator.set_languages("es", "de")
        assert translator.source == "es"
        assert translator.target == "de"
    
    def test_disabled_cache(self):
        """Test translator with disabled cache"""
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", cache_enabled=False)
        
        assert translator._cache is None
        assert translator.cache_size() == 0
    
    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text"""
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr")
        
        assert translator.translate([""]) == {"": ""}
        assert translator.translate(["   "]) == {"   ": "   "}
        assert translator.translate(["", "   "]) == {"": "", "   ": "   "}
    
    def test_callable_interface(self):
        """Test that translator can be called directly"""
        with patch('autolocalise.translator.requests.Session.post') as mock_post:
            mock_post.side_effect = [
                Mock(status_code=404),
                Mock(status_code=200, json=lambda: {
                    "translations": {"69609650": "Bonjour"}  # Hash of "Hello"
                })
            ]
            
            translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
            result = translator(["Hello"])
            
            assert result == {"Hello": "Bonjour"}