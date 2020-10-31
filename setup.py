"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations

Setup script for generating package.
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "swbs", # Replace with your own username
    version = "1.0",
    author = "perpetualCreations",
    author_email = "tchen0584@gmail.com",
    description = "Socket wrapper for sending and receiving byte strings.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/perpetualCreations/swbs/",
    packages=setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = '>=3.6',
)
