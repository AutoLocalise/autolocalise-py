from setuptools import setup, find_packages
import os
import re

# Read version from _version.py
here = os.path.abspath(os.path.dirname(__file__))
with open(
    os.path.join(here, "autolocalise", "_version.py"), "r", encoding="utf-8"
) as f:
    version_content = f.read()
    version_match = re.search(r'__version__ = "([^"]*)"', version_content)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in _version.py")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autolocalise",
    version=version,
    author="AutoLocalise",
    author_email="support@autolocalise.com",
    description="Python SDK for AutoLocalise translation service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AutoLocalise/autolocalise-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
            "pytest-cov>=3.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
)
