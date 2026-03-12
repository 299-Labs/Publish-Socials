"""
Setup script for Publisher package.
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()


# Read requirements file
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


# Get version from pyproject.toml
def get_version():
    import toml

    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
    return pyproject["project"]["version"]


setup(
    name="Publish-Socials",
    version=get_version(),
    author="299labs",
    author_email="contact@299labs.xyz",
    description="Multi-platform social media publishing tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/299-Labs/Publish-Socials",
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
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "reddit": ["praw>=7.7.0"],
    },
    entry_points={
        "console_scripts": [
            "publish-socials=publish_socials.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "publish_socials": ["*.md", "*.txt"],
    },
    zip_safe=False,
)
