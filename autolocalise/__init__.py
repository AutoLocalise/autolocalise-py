"""AutoLocalise Python SDK"""

from .translator import Translator
from .exceptions import AutoLocaliseError, APIError, NetworkError
from ._version import __version__
from string import Template

__all__ = [
    "Translator",
    "Template",
    "AutoLocaliseError",
    "APIError",
    "NetworkError",
    "__version__",
]
