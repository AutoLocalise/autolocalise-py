# Development Guide

This guide explains how to set up the development environment and run examples and tests locally.

## ⚠️ Important: Virtual Environment Required

**Always use a virtual environment** to avoid conflicts with system packages and other projects. This is especially important for development work.

## Setup Development Environment

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/AutoLocalise/autolocalise-py.git
cd autolocalise-py

# setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Verify Installation

```bash
# Check that the package is installed
python -c "import autolocalise; print('✅ AutoLocalise installed successfully')"
```

## Running Examples

### Basic Example

```bash
# Run the main example
python example.py
```

**Expected output:**

```
AutoLocalise Python SDK Example
========================================

1. Single Translation:
'Hello, world!' -> 'Hello, world!'  # (Will fallback since no real API key)

2. Batch Translation:
'Submit' -> 'Submit'
'Cancel' -> 'Cancel'

3. Cache Status:
Cached translations: 0

...
```

### With Real API Key

To test with actual translations, set your API key:

```bash
# Option 1: Environment variable
export AUTOLOCALISE_API_KEY="your-actual-api-key"
python example.py

# Option 2: Modify the example file
# Edit example.py and replace "demo-api-key" with your real key
```

## Running Tests

### Run All Tests

```bash
# Run all tests with verbose output
pytest -v

# Run all tests with coverage
pytest --cov=autolocalise --cov-report=html
```

### Run Specific Test Files

```bash
# Test core translator functionality
pytest tests/test_translator_core.py -v

# Test API interactions
pytest tests/test_translation_api.py -v

# Test cache functionality and thread safety
pytest tests/test_cache_functionality.py -v
```

### Run Specific Test Methods

```bash
# Run a specific test method
pytest tests/test_translator_core.py::TestTranslatorCore::test_init_with_required_params -v

# Run all tests in a specific class
pytest tests/test_cache_functionality.py::TestCacheBasics -v
```

### Test Output Examples

**Successful test run:**

```bash
$ pytest tests/test_translator_core.py -v

========================= test session starts =========================
tests/test_translator_core.py::TestTranslatorCore::test_init_with_required_params PASSED
tests/test_translator_core.py::TestTranslatorCore::test_init_with_all_params PASSED
tests/test_translator_core.py::TestTranslatorCore::test_set_languages PASSED
========================= 3 passed in 0.12s =========================
```

**With coverage:**

```bash
$ pytest --cov=autolocalise

========================= test session starts =========================
tests/test_cache_functionality.py .................... [ 64%]
tests/test_translation_api.py ............ [ 85%]
tests/test_translator_core.py ....... [100%]

---------- coverage: platform darwin, python 3.11.0 -----------
Name                           Stmts   Miss  Cover
--------------------------------------------------
autolocalise/__init__.py           3      0   100%
autolocalise/cache.py             45      2    96%
autolocalise/exceptions.py        12      0   100%
autolocalise/translator.py       89      5    94%
--------------------------------------------------
TOTAL                            149      7    95%
```

## Test Organization

Our tests are organized into three focused files:

### `test_translator_core.py`

- Core translator functionality
- Initialization and configuration
- Basic operations
- Parameter validation

### `test_translation_api.py`

- API interaction testing
- Network error handling
- Cache population from server
- Request/response validation

### `test_cache_functionality.py`

- Cache operations (get, set, clear)
- Thread safety testing
- Shared vs independent cache modes
- Concurrent access scenarios

## Development Workflow

### 1. Make Changes

```bash
# Edit code in autolocalise/ directory
vim autolocalise/translator.py
```

### 2. Run Tests

```bash
# Quick test run
pytest tests/test_translator_core.py -v

# Full test suite
pytest

# With coverage
pytest --cov=autolocalise
```

### 3. Check Code Quality

```bash
# Format code
black autolocalise tests

# Check linting
flake8 autolocalise tests

# Type checking (if using mypy)
mypy autolocalise
```

### 4. Test Examples

```bash
# Test your changes with examples
python example.py
python example_multithreaded.py
```

## Debugging

### Debug Test Failures

```bash
# Run with more verbose output
pytest -vvv --tb=long

# Run with pdb debugger on failure
pytest --pdb

# Run specific failing test
pytest tests/test_translation_api.py::TestTranslationAPI::test_successful_translation -vvv
```

### Debug Examples

```bash
# Add debug prints to examples
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
exec(open('example.py').read())
"
```

## Common Issues

### Import Errors

```bash
# If you get import errors, reinstall in development mode
pip install -e ".[dev]"
```

### Test Database/Cache Issues

```bash
# Clear any cached data
python -c "from autolocalise import Translator; Translator.clear_global_cache()"
```

### Virtual Environment Issues

```bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Performance Testing

### Benchmark Cache Performance

```bash
# Run multithreaded example with timing
time python example_multithreaded.py
```

### Memory Usage

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler example.py
```

## CI/CD Workflow

The repository uses a single GitHub Actions workflow (`.github/workflows/main.yml`) that handles:

- **Tests**: Run on every push to any branch and all PRs
- **Build**: Package building for tags and releases
- **Publish**: Automatic publishing to TestPyPI (tags) and PyPI (releases)

### Workflow Triggers

```yaml
# Tests run on:
- Push to any branch
- Pull requests to main/staging

# Publishing happens on:
- Version tags (v1.0.0) → TestPyPI
- GitHub releases → PyPI
```

### Release Process

1. **Update version** in `autolocalise/_version.py`
2. **Create tag**: `git tag v1.0.0 && git push origin v1.0.0`
3. **TestPyPI publish** happens automatically
4. **Create GitHub release** to publish to PyPI

## Contributing

1. **Run all tests** before submitting changes
2. **Add tests** for new functionality
3. **Update examples** if API changes
4. **Check code formatting** with black and flake8
5. **Update documentation** if needed

```bash
# Pre-commit checklist
pytest                    # All tests pass
black autolocalise tests  # Code formatted
flake8 autolocalise tests # No linting errors
python example.py         # Examples work
```
