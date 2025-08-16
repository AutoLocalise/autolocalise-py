# AutoLocalise Python SDK

A framework-agnostic Python SDK for the AutoLocalise translation service. Works seamlessly with Django, Flask, FastAPI, or any Python backend.

## Features

- **Framework-agnostic** — Works with any Python web framework
- **Intelligent caching** — In-memory cache with thread-safe operations
- **Batch translation** — Efficient bulk translation support
- **Smart API usage** — Only translates new strings, reuses existing translations
- **Error handling** — Graceful fallbacks when translation fails
- **Simple API** — Clean, intuitive interface

## Installation

```bash
pip install autolocalise
```

## Quick Start

```python
from autolocalise import Translator

# Initialize translator
t = Translator(api_key="your-api-key", source_locale="en", target_locale="fr")

# Translate single text
text = t("Hello, world!")
print(text)  # "Bonjour, le monde!"

# Translate multiple texts efficiently
texts = ["Hello", "Goodbye", "Thank you"]
translations = t.translate(texts)
print(translations)
# {"Hello": "Bonjour", "Goodbye": "Au revoir", "Thank you": "Merci"}
```

## Configuration

### Basic Configuration

```python
from autolocalise import Translator

translator = Translator(
    api_key="your-api-key",
    source_locale="en",           # Source language (default: "en")
    target_locale="fr",           # Target language (default: "fr")
    cache_ttl=30,            # Request timeout in seconds
)
```

### Environment Variables

You can also configure using environment variables:

```python
import os
from autolocalise import Translator

translator = Translator(
    api_key=os.getenv("AUTOLOCALISE_API_KEY"),
    source_locale=os.getenv("AUTOLOCALISE_SOURCE_LANG", "en"),
    target_locale=os.getenv("AUTOLOCALISE_TARGET_LANG", "fr")
)
```

## Usage Examples

### Single Translation

```python
# Using the callable interface (single string)
result = translator("Hello")
print(result)  # "Bonjour"

# Using the translate method (list input)
result = translator.translate(["Hello"])
hello_translated = result["Hello"]

# Override languages for specific translation
result = translator.translate(["Hello"], source_locale="en", target_locale="es")
hello_spanish = result["Hello"]
```

### Translation with Parameters/Placeholders

When you need to insert dynamic values into translated text, use placeholder patterns:

```python
from autolocalise import Translator

translator = Translator(api_key="your-api-key", source_locale="en", target_locale="fr")

# Simple parameter substitution
name = "Alice"
greeting = translator("Welcome, {{1}}!").replace("{{1}}", name)
print(greeting)  # "Bienvenue, Alice!"

# Multiple parameters
name = "Bob"
city = "Paris"
message = translator("Hello {{1}}, welcome to {{2}}!") \
    .replace("{{1}}", name) \
    .replace("{{2}}", city)
print(message)  # "Bonjour Bob, bienvenue à Paris!"

# Nested translations (translate parameters too)
name = "Charlie"
day_greeting = translator("Have a great day!")
welcome_msg = translator("Welcome, {{1}}! Nice to meet you. {{2}}.") \
    .replace("{{1}}", name) \
    .replace("{{2}}", day_greeting)
print(welcome_msg)  # "Bienvenue, Charlie! Ravi de vous rencontrer. Passez une excellente journée!."

# Using format strings for cleaner code
def translate_with_params(text, **params):
    """Helper function for parameter substitution"""
    translated = translator(text)
    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        translated = translated.replace(placeholder, str(value))
    return translated

# Usage with helper function
result = translate_with_params(
    "Hello {{name}}, you have {{count}} new messages!",
    name="David",
    count=5
)
print(result)  # "Bonjour David, vous avez 5 nouveaux messages!"

# Advanced: Translate parameters that are also translatable
def smart_translate(text, **params):
    """Translate text and also translate any translatable parameters"""
    translated_text = translator(text)

    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        # If value looks like translatable text, translate it too
        if isinstance(value, str) and any(c.isalpha() for c in value):
            try:
                translated_value = translator(value)
            except:
                translated_value = value
        else:
            translated_value = str(value)

        translated_text = translated_text.replace(placeholder, translated_value)

    return translated_text

# Smart translation example
result = smart_translate(
    "Status: {{status}}. Next action: {{action}}.",
    status="Complete",
    action="Review results"
)
print(result)  # "Statut: Terminé. Action suivante: Examiner les résultats."
```

#### Best Practices for Parameters

1. **Use consistent placeholder format**: `{{1}}`, `{{2}}` or `{{name}}`, `{{count}}`
2. **Keep placeholders simple**: Avoid complex nested structures
3. **Translate the base text first**: Always translate the template before substitution
4. **Consider parameter order**: Some languages may need different word order
5. **Handle missing parameters gracefully**: Check for undefined placeholders

```python
# Example of robust parameter handling
def safe_translate_with_params(text, **params):
    """Safely translate text with parameter substitution"""
    try:
        translated = translator(text)

        # Replace all provided parameters
        for key, value in params.items():
            placeholder = "{{" + key + "}}"
            if placeholder in translated:
                translated = translated.replace(placeholder, str(value))

        # Warn about unreplaced placeholders (optional)
        import re
        remaining_placeholders = re.findall(r'\{\{[^}]+\}\}', translated)
        if remaining_placeholders:
            print(f"Warning: Unreplaced placeholders: {remaining_placeholders}")

        return translated
    except Exception as e:
        print(f"Translation failed: {e}")
        return text  # Fallback to original

# Usage
result = safe_translate_with_params(
    "Welcome {{name}}! You have {{count}} items in your {{container}}.",
    name="Eve",
    count=3
    # Note: 'container' parameter missing - will be warned about
)
```

### Batch Translation

```python
texts = [
    "Welcome to our app",
    "Please enter your email",
    "Submit",
    "Cancel"
]

translations = translator.translate(texts, target_locale="es")

for original, translated in translations.items():
    print(f"{original} -> {translated}")
```

### Framework Integration

#### Django

```python
# settings.py
AUTOLOCALISE_API_KEY = "your-api-key"
AUTOLOCALISE_SOURCE = "en"
AUTOLOCALISE_TARGET = "fr"

# utils.py
from django.conf import settings
from autolocalise import Translator

translator = Translator(
    api_key=settings.AUTOLOCALISE_API_KEY,
    source_locale=settings.AUTOLOCALISE_SOURCE,
    target_locale=settings.AUTOLOCALISE_TARGET
)

def translate_with_params(text, **params):
    """Helper for parameter substitution in Django"""
    translated = translator(text)
    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        translated = translated.replace(placeholder, str(value))
    return translated

# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import translator, translate_with_params

def home_view(request):
    message = translator("Welcome to our site!")
    return render(request, 'home.html', {'message': message})

@login_required
def dashboard_view(request):
    user = request.user
    welcome_msg = translate_with_params(
        "Hello {{name}}, you have {{count}} notifications!",
        name=user.first_name,
        count=user.notifications.unread().count()
    )
    return render(request, 'dashboard.html', {'welcome_msg': welcome_msg})

# In templates (home.html)
# {{ message }}  <!-- Displays: "Bienvenue sur notre site!" -->
```

#### Flask

```python
from flask import Flask, session, request
from autolocalise import Translator

app = Flask(__name__)
translator = Translator(
    api_key=app.config['AUTOLOCALISE_API_KEY'],
    source_locale="en",
    target_locale="fr"
)

def t_with_params(text, **params):
    """Flask helper for parameterized translations"""
    translated = translator(text)
    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        translated = translated.replace(placeholder, str(value))
    return translated

@app.route('/')
def home():
    message = translator("Hello, Flask!")
    return f"<h1>{message}</h1>"

@app.route('/user/<username>')
def user_profile(username):
    greeting = t_with_params(
        "Welcome back, {{name}}! Your last visit was {{time}}.",
        name=username,
        time="2 hours ago"  # This could come from database
    )
    return f"<p>{greeting}</p>"

@app.route('/cart')
def cart():
    item_count = len(session.get('cart_items', []))
    if item_count == 0:
        message = translator("Your cart is empty.")
    else:
        message = t_with_params(
            "You have {{count}} items in your cart.",
            count=item_count
        )
    return f"<p>{message}</p>"
```

#### FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from autolocalise import Translator
from typing import Optional

app = FastAPI()
translator = Translator(api_key="your-api-key")

class User(BaseModel):
    name: str
    email: str
    notification_count: int = 0

def translate_params(text: str, **params) -> str:
    """FastAPI helper for parameterized translations"""
    translated = translator(text)
    for key, value in params.items():
        placeholder = "{{" + key + "}}"
        translated = translated.replace(placeholder, str(value))
    return translated

@app.get("/")
async def root():
    message = translator("Hello, FastAPI!")
    return {"message": message}

@app.get("/welcome/{user_name}")
async def welcome_user(user_name: str):
    message = translate_params(
        "Welcome {{name}}! Enjoy using our API.",
        name=user_name
    )
    return {"welcome_message": message}

@app.post("/user/notifications")
async def user_notifications(user: User):
    if user.notification_count == 0:
        message = translator("No new notifications.")
    elif user.notification_count == 1:
        message = translator("You have 1 new notification.")
    else:
        message = translate_params(
            "You have {{count}} new notifications.",
            count=user.notification_count
        )

    return {
        "user": user.name,
        "message": message,
        "status": "success"
    }

@app.get("/error-example")
async def error_example():
    try:
        # Simulate some operation that might fail
        raise ValueError("Something went wrong")
    except ValueError:
        error_msg = translate_params(
            "An error occurred. Please try again or contact {{support}}.",
            support="support@example.com"
        )
        raise HTTPException(status_code=500, detail=error_msg)
```

### Cache Management

```python
# Check cache size
print(f"Cached translations: {translator.cache_size()}")

# Clear cache for this instance's language pair only
translator.clear_cache()

# Clear the entire global shared cache (affects all instances)
Translator.clear_global_cache()

# Disable cache for specific instance
translator_no_cache = Translator(
    api_key="your-api-key",
    cache_enabled=False
)
```

### Language Management

```python
# Change languages dynamically
translator.set_languages(source_locale="es", target_locale="de")

# Use different languages for specific translations
spanish_result = translator.translate(["Hello"], source_locale="en", target_locale="es")
spanish_text = spanish_result["Hello"]

german_result = translator.translate(["Hello"], source_locale="en", target_locale="de")
german_text = german_result["Hello"]
```

### Error Handling

```python
from autolocalise import Translator, APIError, NetworkError

translator = Translator(api_key="your-api-key")

try:
    result = translator("Hello")
except APIError as e:
    print(f"API error: {e.message} (Status: {e.status_code})")
except NetworkError as e:
    print(f"Network error: {e}")
```

## How It Works

1. **Check Cache**: First checks in-memory cache for existing translation
2. **Fetch Existing**: Calls API to get server-persisted translations
3. **Translate New**: Only sends untranslated strings for translation
4. **Cache Results**: Stores all translations in memory for future use
5. **Fallback**: Returns original text if translation fails

This approach minimizes API calls and ensures fast response times for repeated translations.

## API Reference

### Translator Class

#### `__init__(api_key, source_locale="en", target_locale="fr", cache_ttl=3600, cache_enabled=True, shared_cache=True)`

Initialize a new translator instance.

**Parameters:**

- `api_key` (str): Your AutoLocalise API key
- `source_locale` (str): Source language code (default: "en")
- `target_locale` (str): Target language code (default: "fr")
- `cache_ttl` (int): Request timeout in seconds (default: 3600)
- `cache_enabled` (bool): Enable caching (default: True)
- `shared_cache` (bool): Use global shared cache (default: True)

#### `translate(texts, target_locale=None, source_locale=None)`

Translate multiple strings (array input only).

**Parameters:**

- `texts` (str or List[str]): Text(s) to translate
- `target_locale` (str, optional): Override target language
- `source_locale` (str, optional): Override source language

**Returns:**

- Returns dict mapping original to translated text

#### `clear_cache()`

Clear cached translations for this instance's language pair.

#### `clear_global_cache()` (class method)

Clear the entire global shared cache (affects all instances).

#### `cache_size()`

Get the number of cached translations.

**Returns:** int - Number of cached translation pairs

#### `set_languages(source_locale, target_locale)`

Update source and target languages for this instance.

**Parameters:**

- `source_locale` (str): New source language code
- `target_locale` (str): New target language code

## Development

For detailed development instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

### Quick Start

```bash
# Clone and setup
git clone https://github.com/AutoLocalise/autolocalise-py.git
cd autolocalise-py
python setup-dev.py  # Automated setup

# Or manual setup
python -m venv venv && source venv/bin/activate && pip install -e ".[dev]"

# Run examples
python example.py
python example_multithreaded.py

# Run tests
pytest
```

### Releases

All releases are managed through GitHub workflows. See [RELEASING.md](RELEASING.md) for instructions.

## License

MIT License - see LICENSE file for details.

## Support

For support, please contact at https://www.autolocalise.com/support
