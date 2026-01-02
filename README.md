# AutoLocalise Python SDK

A framework-agnostic Python SDK for the [AutoLocalise](https://www.autolocalise.com) translation service. Works seamlessly with Django, Flask, FastAPI, or any Python backend.

## Features

- **Framework-agnostic** — Works with any Python web framework
- **Intelligent caching** — In-memory cache with thread-safe operations
- **Template support** — Built-in Python Template support with parameter protection
- **Batch translation** — Efficient bulk translation support
- **Smart API usage** — Only translates new strings, reuses existing translations
- **Error handling** — Graceful fallbacks when translation fails

## Installation

```bash
pip install autolocalise
```

## Quick Start

```python
from autolocalise import Translator

# Initialize translator
translator = Translator(api_key="your-api-key", source_locale="en", target_locale="fr")

# Simple translation
result = translator.translate(["Hello", "Goodbye"])
print(result)
# {"Hello": "Bonjour", "Goodbye": "Au revoir"}

# Template with parameters
from string import Template
template = Template("Hello $name, you have $count new messages!")
translated = translator.translate_template(template, name="Alice", count=5)
print(translated)
# "Bonjour Alice, vous avez 5 nouveaux messages!"
```

## Core Usage

### Basic Translation

```python
from autolocalise import Translator

translator = Translator(
    api_key="your-api-key",
    source_locale="en",
    target_locale="fr"
)

# Single or multiple texts
texts = ["Welcome", "Login", "Submit"]
translations = translator(texts)
```

### Template Translation with Parameters

The SDK supports Python's `string.Template` with automatic parameter protection:

```python
from string import Template
from autolocalise import Translator

translator = Translator(api_key="your-api-key", source_locale="en", target_locale="fr")

# Create template
template = Template("Welcome $name! You have $count items in your $container.")

# Translate with parameters - parameters are protected from translation
result = translator.translate_template(template, name="John", count=3, container="cart")
print(result)
# "Bienvenue John! Vous avez 3 articles dans votre cart."
```

### Environment Configuration

```python
import os
from autolocalise import Translator

translator = Translator(
    api_key=os.getenv("AUTOLOCALISE_API_KEY"),
    source_locale=os.getenv("AUTOLOCALISE_SOURCE_LANG", "en"),
    target_locale=os.getenv("AUTOLOCALISE_TARGET_LANG", "fr")
)
```

### Framework Examples

#### Django
```python
# utils.py
from django.conf import settings
from autolocalise import Translator
from string import Template

translator = Translator(
    api_key=settings.AUTOLOCALISE_API_KEY,
    source_locale="en",
    target_locale="fr"
)

def translate_message(template_str, **params):
    template = Template(template_str)
    return translator.translate_template(template, **params)

# views.py
def dashboard_view(request):
    message = translate_message(
        "Hello $name, you have $count notifications!",
        name=request.user.first_name,
        count=request.user.notifications.unread().count()
    )
    return render(request, 'dashboard.html', {'message': message})
```

#### Flask
```python
from flask import Flask
from autolocalise import Translator
from string import Template

app = Flask(__name__)
translator = Translator(api_key=app.config['AUTOLOCALISE_API_KEY'], source_locale="en", target_locale="fr")

@app.route('/user/<username>')
def user_profile(username):
    template = Template("Welcome back, $name!")
    message = translator.translate_template(template, name=username)
    return f"<h1>{message}</h1>"
```

#### FastAPI
```python
from fastapi import FastAPI
from autolocalise import Translator
from string import Template

app = FastAPI()
translator = Translator(api_key="your-api-key", source_locale="en", target_locale="fr")

@app.get("/welcome/{user_name}")
async def welcome_user(user_name: str):
    template = Template("Welcome $name! Enjoy using our API.")
    message = translator.translate_template(template, name=user_name)
    return {"message": message}
```

## API Reference

### Translator Class

#### `__init__(api_key, source_locale, target_locale)`

Initialize a new translator instance.

**Parameters:**
- `api_key` (str): Your AutoLocalise API key
- `source_locale` (str): Source language code (e.g., "en")
- `target_locale` (str): Target language code (e.g., "fr")

**Raises:**
- `ConfigurationError`: If required parameters are missing

#### `translate(texts, target_locale=None, source_locale=None)`

Translate multiple strings.

**Parameters:**
- `texts` (List[str]): List of strings to translate
- `target_locale` (str, optional): Target language code (overrides instance default)
- `source_locale` (str, optional): Source language code (overrides instance default)

**Returns:** Dict[str, str] - Dictionary mapping original text to translated text

**Behavior:**
- Non-string values are silently skipped
- Empty strings are returned as-is

**Raises:**
- `ValueError`: If any text exceeds 10,000 characters

**Example:**
```python
# Valid strings
result = translator.translate(["Hello", "World"])
# Returns: {"Hello": "Bonjour", "World": "Monde"}

# Mixed valid and invalid inputs
result = translator.translate(["Hello", 123, ""])
# Returns: {"Hello": "Bonjour", "": ""}
# Note: 123 is skipped (not a string)

# Text too long
translator.translate(["a" * 10001])  # Raises: ValueError
```

#### `translate_template(template, **params)`

Translate a Python Template with parameter protection.

**Parameters:**
- `template` (Template): Python string.Template object
- `**params`: Template parameters (protected from translation)

**Returns:** str - Translated text with parameters substituted

#### Cache Management

```python
# Check cache size
translator.cache_size()

# Clear cache
translator.clear_cache()

# Clear global cache
Translator.clear_global_cache()
```

## How Parameter Protection Works

When using `translate_template()`:

1. **Parameter Extraction**: Parameters are temporarily replaced with short placeholders like `X1X`, `X2X`
2. **Translation**: Only the template text with placeholders is sent for translation 
3. **Parameter Restoration**: Original parameter values are substituted back
4. **Result**: Translated text with original parameter values intact

**Cost Optimization**: Short placeholders minimize translation API costs while ensuring parameters like usernames, numbers, and dynamic content are never accidentally translated.

**Example**: `"Hello $name!"` → `"Hello X1X!"` (sent to API) → `"Bonjour John!"` (final result)

## Development

```bash
git clone https://github.com/AutoLocalise/autolocalise-py.git
cd autolocalise-py
pip install -e ".[dev]"
pytest
```

## License

MIT License - see LICENSE file for details.

## Support

For support, please contact at https://www.autolocalise.com/support