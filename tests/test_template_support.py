"""Tests for Template support functionality"""

import pytest
from string import Template
from unittest.mock import Mock

from autolocalise.translator import Translator


class TestTemplateSupport:
    """Test Template functionality with parameter protection"""

    @pytest.fixture
    def mock_translator(self):
        """Create a mock translator for testing without API calls"""
        translator = Mock(spec=Translator)
        translator.source = "en"
        translator.target = "fr"

        # Mock the translate method to simulate translation
        def mock_translate(texts, target_locale=None, source_locale=None):
            result = {}
            for text in texts:
                # Simple mock translation: replace English words with French
                translated = (
                    text.replace("Hello", "Bonjour")
                    .replace("hello", "bonjour")
                    .replace("Welcome", "Bienvenue")
                    .replace("welcome", "bienvenue")
                    .replace("you have", "vous avez")
                    .replace("messages", "messages")
                    .replace("items", "articles")
                    .replace("view", "vue")
                )
                if translated == text:  # If no replacement, add prefix
                    translated = f"FR_{text}"
                result[text] = translated
            return result

        translator.translate.side_effect = mock_translate

        # Add the actual translate_template method
        from autolocalise.translator import Translator as RealTranslator

        translator.translate_template = RealTranslator.translate_template.__get__(
            translator
        )

        return translator

    def test_simple_template_example(self, mock_translator):
        """Test simple template example: hello $name, welcome to
        ${location_name} view"""
        template = Template("hello $name, welcome to ${location_name} view")
        result = mock_translator.translate_template(
            template, name="Alice", location_name="dashboard"
        )

        assert "Alice" in result  # Parameter preserved
        assert "dashboard" in result  # Parameter preserved
        assert "bonjour Alice, bienvenue to dashboard vue" == result

    def test_template_without_parameters(self, mock_translator):
        """Test template without any parameters"""
        template = Template("This is a simple message.")
        result = mock_translator.translate_template(template)

        assert result == "FR_This is a simple message."

    def test_missing_parameters(self, mock_translator):
        """Test template with some missing parameters"""
        template = Template("Hello $name, you have $count items in $container.")
        result = mock_translator.translate_template(template, name="Bob", count=7)

        assert "Bob" in result  # Provided parameter preserved
        assert "7" in result  # Provided parameter preserved
        assert "$container" in result  # Missing parameter remains as template variable
        assert "Bonjour" in result  # Text translated

    def test_invalid_template_type(self, mock_translator):
        """Test error handling for non-Template objects"""
        with pytest.raises(
            ValueError, match="First argument must be a string.Template object"
        ):
            mock_translator.translate_template("Not a template", name="Test")

    def test_mixed_parameter_syntax(self, mock_translator):
        """Test template with both $var and ${var} syntax"""
        template = Template(
            "Hello $name, welcome to ${location_name} view! You have $count items."
        )
        result = mock_translator.translate_template(
            template, name="Bob", location_name="admin", count=42
        )

        assert "Bob" in result
        assert "admin" in result
        assert "42" in result
        assert "Bonjour Bob, bienvenue to admin vue! You have 42 articles." == result

    def test_language_override(self, mock_translator):
        """Test template translation with language override"""
        template = Template("Hello $name!")

        # Mock different behavior for Spanish
        def mock_translate_es(texts, target_locale=None, source_locale=None):
            if target_locale == "es":
                return {text: text.replace("Hello", "Hola") for text in texts}
            return mock_translator.translate(texts, target_locale, source_locale)

        mock_translator.translate.side_effect = mock_translate_es

        result = mock_translator.translate_template(
            template, target_locale="es", name="Maria"
        )
        assert "Hola" in result
        assert "Maria" in result
