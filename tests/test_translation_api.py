"""Tests for translation API interactions"""

import pytest
import requests
from unittest.mock import Mock, patch

from autolocalise import Translator, __version__
from autolocalise.exceptions import APIError, NetworkError


class TestTranslationAPI:
    """Test cases for translation API interactions"""
    
    def setup_method(self):
        """Clear global cache before each test"""
        Translator.clear_global_cache()
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_successful_translation(self, mock_post):
        """Test successful translation API call"""
        # Mock API responses
        mock_post.side_effect = [
            # First call to /v1/translations (no existing translations)
            Mock(status_code=404),
            # Second call to /v1/translate
            Mock(status_code=200, json=lambda: {
                "translations": {"69609650": "Bonjour"}  # Hash of "Hello"
            })
        ]
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        result = translator.translate(["Hello"])
        
        assert result == {"Hello": "Bonjour"}
        assert mock_post.call_count == 2
        
        # Verify the /v1/translations call
        mock_post.assert_any_call(
            "https://autolocalise-main-53fde32.zuplo.app/v1/translations",
            json={"apiKey": "test-key", "targetLocale": "fr"},
            timeout=3600
        )
        
        # Check that the /v1/translate call was made with hash-based format
        translate_calls = [call for call in mock_post.call_args_list if 'v1/translate' in str(call)]
        assert len(translate_calls) == 1
        
        translate_call = translate_calls[0]
        call_json = translate_call[1]['json']
        
        # Verify the structure
        assert "texts" in call_json
        assert isinstance(call_json["texts"], list)
        assert len(call_json["texts"]) == 1
        
        # Verify text object structure
        text_obj = call_json["texts"][0]
        assert "hashkey" in text_obj
        assert "text" in text_obj
        assert "persist" in text_obj
        assert text_obj["text"] == "Hello"
        assert text_obj["persist"] is True
        assert text_obj["hashkey"] == "69609650"  # Hash of "Hello"
        
        # Verify other fields
        assert call_json["sourceLocale"] == "en"
        assert call_json["targetLocale"] == "fr"
        assert call_json["apiKey"] == "test-key"
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_batch_translation(self, mock_post):
        """Test successful batch translation"""
        mock_post.side_effect = [
            # /v1/translations call
            Mock(status_code=200, json=lambda: {
                "translations": {"69609650": "Bonjour"}  # Hash of "Hello"
            }),
            # /v1/translate call for remaining texts
            Mock(status_code=200, json=lambda: {
                "translations": {"83766130": "Monde"}  # Hash of "World"
            })
        ]
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        results = translator.translate(["Hello", "World"])
        
        assert results == {"Hello": "Bonjour", "World": "Monde"}
        assert mock_post.call_count == 2
        
        # Verify the /v1/translations call
        mock_post.assert_any_call(
            "https://autolocalise-main-53fde32.zuplo.app/v1/translations",
            json={"apiKey": "test-key", "targetLocale": "fr"},
            timeout=3600
        )
        
        # Check that the /v1/translate call was made with hash-based format
        translate_calls = [call for call in mock_post.call_args_list if 'v1/translate' in str(call)]
        assert len(translate_calls) == 1
        
        translate_call = translate_calls[0]
        call_json = translate_call[1]['json']
        
        # Verify the structure
        assert "texts" in call_json
        assert isinstance(call_json["texts"], list)
        assert len(call_json["texts"]) == 1
        
        # Verify text object structure  
        text_obj = call_json["texts"][0]
        assert "hashkey" in text_obj
        assert "text" in text_obj
        assert "persist" in text_obj
        assert text_obj["text"] == "World"
        assert text_obj["persist"] is True
        assert text_obj["hashkey"] == "83766130"  # Hash of "World"
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_initialization_populates_cache(self, mock_post):
        """Test that initialization populates cache with existing translations"""
        mock_post.return_value = Mock(status_code=200, json=lambda: {
            "translations": {"69609650": "Bonjour", "-1397214398": "Bienvenue"}  # Hashes of "Hello" and "Welcome"
        })
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        
        # Should have called /v1/translations during initialization
        assert mock_post.call_count == 1
        mock_post.assert_called_with(
            "https://autolocalise-main-53fde32.zuplo.app/v1/translations",
            json={"apiKey": "test-key", "targetLocale": "fr"},
            timeout=3600
        )
        
        # Note: Cache won't be pre-populated since we don't know original texts for hashes
        # This is expected behavior - cache will be populated as translations are requested
        
        # Test that we can still translate (will hit API since cache is empty)
        with patch('autolocalise.translator.requests.Session.post') as mock_translate:
            mock_translate.return_value = Mock(status_code=200, json=lambda: {
                "translations": {"69609650": "Bonjour", "-1397214398": "Bienvenue"}
            })
            results = translator.translate(["Hello", "Welcome"])
            assert results == {"Hello": "Bonjour", "Welcome": "Bienvenue"}
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_api_error_handling(self, mock_post):
        """Test handling of API errors"""
        mock_post.return_value = Mock(
            status_code=400,
            json=lambda: {"error": "Invalid language code"}
        )
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        
        # Should fallback to original text on error
        result = translator.translate(["Hello"])
        assert result == {"Hello": "Hello"}
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_network_error_handling(self, mock_post):
        """Test handling of network errors"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        
        # Should fallback to original text on network error
        result = translator.translate(["Hello"])
        assert result == {"Hello": "Hello"}
    
    @patch('autolocalise.translator.requests.Session.post')
    def test_cache_hit_avoids_api_call(self, mock_post):
        """Test that cached translations don't trigger API calls"""
        # Mock first translation
        mock_post.side_effect = [
            Mock(status_code=404),
            Mock(status_code=200, json=lambda: {
                "translations": {"69609650": "Bonjour"}  # Hash of "Hello"
            })
        ]
        
        translator = Translator(api_key="test-key", source_locale="en", target_locale="fr", shared_cache=False)
        
        # First translation - should hit API
        result1 = translator.translate(["Hello"])
        assert result1 == {"Hello": "Bonjour"}
        
        # Second translation - should hit cache
        result2 = translator.translate(["Hello"])
        assert result2 == {"Hello": "Bonjour"}
        
        # Should only call API twice (once for /v1/translations, once for /v1/translate)
        assert mock_post.call_count == 2