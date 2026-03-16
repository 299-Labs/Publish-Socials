"""
Publish-Socials - Multi-platform social media publishing tool.

This package provides functionality to publish content across multiple platforms
including X (Twitter), Reddit, Medium, Substack, and LinkedIn.
"""

from .config import Config
from .errors import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ContentTooLongError,
    FileError,
    InvalidFormatError,
    MissingRequiredFieldError,
    NetworkError,
    PlatformError,
    PlatformNotConfiguredError,
    PublishingError,
    RateLimitError,
    TemplateError,
    UnsupportedPlatformError,
    ValidationError,
)
from .platforms.linkedin_publisher import LinkedInPublisher
from .platforms.medium_publisher import MediumPublisher
from .platforms.reddit_publisher import RedditPublisher
from .platforms.substack_publisher import SubstackPublisher
from .platforms.x_publisher import XPublisher
from .publish_socials import Publisher
from .utils import ContentFormatter, generate_slug, sanitize_filename, validate_article

__version__ = "1.0.0"
__author__ = "299labs"
__description__ = "Multi-platform social media publishing tool"

# Expose main classes and functions
__all__ = [
    "Publisher",
    "Config",
    "ContentFormatter",
    "validate_article",
    "sanitize_filename",
    "generate_slug",
    # Platform publishers
    "XPublisher",
    "RedditPublisher", 
    "MediumPublisher",
    "SubstackPublisher",
    "LinkedInPublisher",
    # Error classes
    "PublishingError",
    "ConfigurationError",
    "AuthenticationError",
    "RateLimitError",
    "NetworkError",
    "ValidationError",
    "PlatformError",
    "ContentTooLongError",
    "MissingRequiredFieldError",
    "InvalidFormatError",
    "PlatformNotConfiguredError",
    "APIError",
    "UnsupportedPlatformError",
    "TemplateError",
    "FileError",
]
