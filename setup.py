"""
Socket Wrapper for Byte Strings (SWBS)
Made by perpetualCreations

Setup script for generating package.
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swbs",
    version="1.2.5",
    author="perpetualCreations",
    author_email="tchen0584@gmail.com",
    description="Socket wrapper for sending and receiving byte strings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perpetualCreations/swbs/",
    install_requires=["pycryptodomex >= 3.9.9"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
