#!/usr/bin/env python3
"""Setup file for the *hole API Python client."""
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(here, "README.rst"), encoding="utf-8") as desc:
    long_description = desc.read()

setup(
    name="hole",
    version="0.8.0",
    description="Python API for interacting with *hole.",
    long_description=long_description,
    url="https://github.com/home-assistant-ecosystem/python-hole",
    download_url="https://github.com/home-assistant-ecosystem/python-hole/releases",
    author="Fabian Affolter",
    author_email="fabian@affolter-engineering.ch",
    license="MIT",
    install_requires=[
        "aiohttp<4",
        "async_timeout>4,<5",
    ],
    packages=["hole"],
    python_requires=">=3.9",
    zip_safe=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
)
