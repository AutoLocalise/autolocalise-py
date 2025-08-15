"""Version information for AutoLocalise Python SDK"""

# Import version from setup.py to maintain single source of truth
import os
import re


def _get_version():
    """Get version from setup.py"""
    here = os.path.dirname(os.path.abspath(__file__))
    setup_py = os.path.join(os.path.dirname(here), "setup.py")

    with open(setup_py, "r", encoding="utf-8") as f:
        content = f.read()

    version_match = re.search(r'version="([^"]*)"', content)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in setup.py")


__version__ = _get_version()
