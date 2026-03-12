"""
Publish-Socials - Multi-platform social media publishing tool.

This package provides functionality to publish content across multiple platforms
including X (Twitter), Reddit, Medium, Substack, and LinkedIn.
"""

from .publish_socials import Publisher
from .config import Config
from .errors import (
    PublishingError,
    ConfigurationError,
    AuthenticationError,
    RateLimitError,
    NetworkError,
    ValidationError,
    PlatformError,
    ContentTooLongError,
    MissingRequiredFieldError,
    InvalidFormatError,
    PlatformNotConfiguredError,
    APIError,
    UnsupportedPlatformError,
    TemplateError,
    FileError
)
from .utils import ContentFormatter, validate_article, sanitize_filename, generate_slug

__version__ = "1.0.0"
__author__ = "299labs"
__description__ = "Multi-platform social media publishing tool"

# Expose main classes and functions
__all__ = [
    'Publisher',
    'Config',
    'ContentFormatter',
    'validate_article',
    'sanitize_filename',
    'generate_slug',
    # Error classes
    'PublishingError',
    'ConfigurationError',
    'AuthenticationError',
    'RateLimitError',
    'NetworkError',
    'ValidationError',
    'PlatformError',
    'ContentTooLongError',
    'MissingRequiredFieldError',
    'InvalidFormatError',
    'PlatformNotConfiguredError',
    'APIError',
    'UnsupportedPlatformError',
    'TemplateError',
    'FileError'
]