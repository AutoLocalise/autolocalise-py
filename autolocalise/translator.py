"""Main translator class for AutoLocalise SDK"""

import json
import logging
import re
from string import Template
from typing import Dict, List, Optional
import requests

from .cache import TranslationCache
from .exceptions import APIError, NetworkError, ConfigurationError
from ._version import __version__


logger = logging.getLogger(__name__)


class Translator:
    """AutoLocalise translator client"""

    def __init__(
        self,
        api_key: str,
        source_locale: str,
        target_locale: str,
        cache_ttl: int = 3600,
        cache_enabled: bool = True,
        shared_cache: bool = True,
    ):
        """
        Initialize AutoLocalise translator

        Args:
            api_key: Your AutoLocalise API key
            source_locale: Source language code
            target_locale: Target language code
            cache_ttl: Request timeout in seconds (default: 3600, 1hour)
            cache_enabled: Enable in-memory caching (default: True)
            shared_cache: Use global shared cache across instances (default: True)
        """
        if not api_key:
            raise ConfigurationError("API key is required")

        if not source_locale:
            raise ConfigurationError("Source Locale is required")

        if not target_locale:
            raise ConfigurationError("Target Locale is required")

        self.api_key = api_key
        self.source = source_locale
        self.target = target_locale
        self.base_url = "https://autolocalise-main-53fde32.zuplo.app"
        self.timeout = cache_ttl
        self.cache_enabled = cache_enabled
        self.shared_cache = shared_cache

        if cache_enabled:
            if shared_cache:
                from .cache import get_global_cache

                self._cache = get_global_cache()
            else:
                self._cache = TranslationCache()
        else:
            self._cache = None
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": f"autolocalise-python-sdk/{__version__}",
            }
        )

        # Pre-populate cache with existing translations from server
        if self._cache:
            self._populate_cache_from_server()

    def _populate_cache_from_server(self):
        """Populate cache with existing translations from server during initialization"""
        try:
            response = self._session.post(
                f"{self.base_url}/v1/translations",
                json={"apiKey": self.api_key, "targetLocale": self.target},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                data = response.json()
                hash_translations = data.get("translations", {})
                if hash_translations:
                    # Store hash-based translations for later lookup
                    self._server_translations = hash_translations
                    logger.debug(
                        f"Server has {len(hash_translations)} existing translations available"
                    )
                else:
                    self._server_translations = {}
            elif response.status_code == 404:
                self._server_translations = {}
            else:
                self._server_translations = {}
                self._handle_api_error(response)
        except Exception as e:
            self._server_translations = {}
            logger.warning(f"Failed to check server translations: {e}")

    def __call__(
        self,
        texts: List[str],
        target_locale: Optional[str] = None,
        source_locale: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Translate texts (callable interface)

        Args:
            texts: List of texts to translate
            target_locale: Target language (optional, uses instance default)
            source_locale: Source language (optional, uses instance default)

        Returns:
            Dictionary mapping original text to translated text
        """
        return self.translate(
            texts, target_locale=target_locale, source_locale=source_locale
        )

    def translate(
        self,
        texts: List[str],
        target_locale: Optional[str] = None,
        source_locale: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Translate multiple texts

        Args:
            texts: List of texts to translate
            target_locale: Target language (optional, uses instance default)
            source_locale: Source language (optional, uses instance default)

        Returns:
            Dictionary mapping original text to translated text
        """
        if not texts:
            return {}

        source_lang = source_locale or self.source
        target_lang = target_locale or self.target

        # Filter out empty strings and check cache
        texts_to_translate = []
        results = {}

        for text in texts:
            if not text or not text.strip():
                results[text] = text
                continue

            # Check local cache first
            if self._cache:
                cached = self._cache.get(text, source_lang, target_lang)
                if cached is not None:
                    results[text] = cached
                    continue

            # Check server translations if available
            if hasattr(self, "_server_translations") and self._server_translations:
                text_hash = self._generate_hash(text)
                if text_hash in self._server_translations:
                    translation = self._server_translations[text_hash]
                    results[text] = translation
                    # Cache the translation for future use
                    if self._cache:
                        self._cache.set(text, translation, source_lang, target_lang)
                    continue

            texts_to_translate.append(text)

        # If all texts were cached, return results
        if not texts_to_translate:
            return results

        # Translate all texts (cache misses)
        try:
            if texts_to_translate:
                new_translations = self._translate_texts(
                    texts_to_translate, source_lang, target_lang
                )

                # Update results and cache with new translations
                for text, translation in new_translations.items():
                    results[text] = translation
                    if self._cache:
                        self._cache.set(text, translation, source_lang, target_lang)

        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            # Fallback: return original texts for untranslated items
            for text in texts_to_translate:
                if text not in results:
                    results[text] = text

        return results

    def _generate_hash(self, text: str) -> str:
        """Generate hash for text (matches React SDK implementation)"""
        hash_value = 0
        for char in text:
            char_code = ord(char)
            hash_value = (hash_value << 5) - hash_value + char_code
            hash_value = hash_value & 0xFFFFFFFF  # Keep as 32-bit integer
            # Convert to signed 32-bit integer
            if hash_value > 0x7FFFFFFF:
                hash_value -= 0x100000000
        return str(hash_value)

    def _translate_texts(
        self, texts: List[str], source_lang: str, target_lang: str
    ) -> Dict[str, str]:
        """Send texts for translation"""
        try:
            # Create text objects with hash keys
            text_objects = []
            text_to_hash = {}
            hash_to_text = {}

            for text in texts:
                hash_key = self._generate_hash(text)
                text_objects.append(
                    {"hashkey": hash_key, "text": text, "persist": True}
                )
                text_to_hash[text] = hash_key
                hash_to_text[hash_key] = text

            response = self._session.post(
                f"{self.base_url}/v1/translate",
                json={
                    "texts": text_objects,
                    "sourceLocale": source_lang,
                    "targetLocale": target_lang,
                    "apiKey": self.api_key,
                    "version": f"python-sdk-v{__version__}",
                },
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                # The API returns translations directly, not nested under "translations" key
                hash_translations = data.get(
                    "translations", data
                )  # Fallback to data itself if no "translations" key

                # Convert hash-based response back to text-based
                text_translations = {}
                for hash_key, translation in hash_translations.items():
                    if hash_key in hash_to_text:
                        original_text = hash_to_text[hash_key]
                        text_translations[original_text] = translation
                return text_translations
            else:
                self._handle_api_error(response)

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Failed to translate texts: {e}")

        return {}

    def _handle_api_error(self, response: requests.Response):
        """Handle API error responses"""
        try:
            error_data = response.json()
            message = error_data.get("error", f"API error: {response.status_code}")
        except (ValueError, json.JSONDecodeError):
            message = f"API error: {response.status_code} - {response.text}"

        raise APIError(
            message, status_code=response.status_code, response_data=error_data
        )

    def clear_cache(self):
        """Clear translation cache (instance or global depending on shared_cache setting)"""
        if self._cache:
            if self.shared_cache:
                # Only clear cache for this instance's language pairs
                # This is safer than clearing the entire global cache
                self._cache.clear(self.source, self.target)
            else:
                self._cache.clear()

    @classmethod
    def clear_global_cache(cls):
        """Clear the entire global shared cache"""
        from .cache import get_global_cache

        cache = get_global_cache()
        cache.clear()

    def cache_size(self) -> int:
        """Get number of cached translations"""
        return self._cache.size() if self._cache else 0

    def set_languages(self, source_locale: str, target_locale: str):
        """Update source and target languages"""
        self.source = source_locale
        self.target = target_locale

    def translate_template(
        self,
        template: Template,
        target_locale: Optional[str] = None,
        source_locale: Optional[str] = None,
        **params,
    ) -> str:
        """
        Translate a Python Template with parameter protection.

        Parameters are replaced with unique placeholders during translation
        to ensure they are not translated, then restored in the final result.

        Args:
            template: Python string.Template object
            target_locale: Target language (optional, uses instance default)
            source_locale: Source language (optional, uses instance default)
            **params: Template parameters (protected from translation)

        Returns:
            Translated text with parameters substituted

        Example:
            template = Template("Hello $name, you have $count messages!")
            result = translator.translate_template(template, name="John", count=5)
            # Returns: "Bonjour John, vous avez 5 messages!"
        """
        if not isinstance(template, Template):
            raise ValueError("First argument must be a string.Template object")

        # Get the template string
        template_str = template.template

        # If no parameters provided, just translate the template string directly
        if not params:
            result = self.translate([template_str], target_locale, source_locale)
            return result[template_str]

        # Step 1: Extract template variables and create placeholder mapping
        # Find all $identifier and ${identifier} patterns in the template
        var_pattern = re.compile(
            r"\$(?P<named>[_a-z][_a-z0-9]*)|" r"\$\{(?P<braced>[_a-z][_a-z0-9]*)\}",
            re.IGNORECASE,
        )

        # Create unique placeholders for each parameter
        placeholder_map = {}
        reverse_placeholder_map = {}
        param_counter = 1

        for match in var_pattern.finditer(template_str):
            var_name = match.group("named") or match.group("braced")
            if var_name in params and var_name not in placeholder_map:
                # Create a short, unique placeholder to minimize translation costs
                # Format: X1X, X2X, etc. (unlikely to appear in real text)
                placeholder = f"X{param_counter}X"
                placeholder_map[var_name] = placeholder
                reverse_placeholder_map[placeholder] = str(params[var_name])
                param_counter += 1

        # Step 2: Replace parameters with placeholders in template
        protected_template_str = template_str
        for var_name, placeholder in placeholder_map.items():
            # Replace both $var and ${var} formats
            protected_template_str = re.sub(
                rf"\${var_name}\b|\${{{var_name}\}}",
                placeholder,
                protected_template_str,
            )

        # Step 3: Translate the protected template
        translation_result = self.translate(
            [protected_template_str], target_locale, source_locale
        )
        translated_text = translation_result[protected_template_str]

        # Step 4: Restore original parameter values
        for placeholder, param_value in reverse_placeholder_map.items():
            translated_text = translated_text.replace(placeholder, param_value)

        return translated_text
