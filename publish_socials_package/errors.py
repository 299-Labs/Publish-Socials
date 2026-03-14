"""
Custom exceptions for the Publisher application.
"""

from typing import Dict, List, Optional


class PublishingError(Exception):
    """
    Base exception for publishing-related errors.
    """

    pass


class ConfigurationError(PublishingError):
    """
    Exception raised when there are configuration issues.
    """

    pass


class AuthenticationError(PublishingError):
    """
    Exception raised when authentication fails.
    """

    pass


class RateLimitError(PublishingError):
    """
    Exception raised when rate limits are exceeded.
    """

    pass


class NetworkError(PublishingError):
    """
    Exception raised for network-related issues.
    """

    pass


class ValidationError(PublishingError):
    """
    Exception raised when content validation fails.
    """

    pass


class PlatformError(PublishingError):
    """
    Exception raised for platform-specific errors.
    """

    pass


class ContentTooLongError(ValidationError):
    """
    Exception raised when content exceeds platform limits.
    """

    pass


class MissingRequiredFieldError(ValidationError):
    """
    Exception raised when required fields are missing.
    """

    pass


class InvalidFormatError(ValidationError):
    """
    Exception raised when content format is invalid.
    """

    pass


class PlatformNotConfiguredError(ConfigurationError):
    """
    Exception raised when a platform is not properly configured.
    """

    pass


class APIError(PublishingError):
    """
    Exception raised for API-related errors.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class UnsupportedPlatformError(PublishingError):
    """
    Exception raised when an unsupported platform is specified.
    """

    pass


class TemplateError(PublishingError):
    """
    Exception raised for template-related errors.
    """

    pass


class FileError(PublishingError):
    """
    Exception raised for file-related errors.
    """

    pass


# Error handling utilities
def handle_publishing_error(func):
    """
    Decorator to handle publishing errors gracefully.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PublishingError:
            raise  # Re-raise publishing errors
        except Exception as e:
            # Convert generic exceptions to PublishingError
            raise PublishingError(f"Unexpected error in {func.__name__}: {str(e)}")

    return wrapper


def validate_required_fields(data: Dict, required_fields: List[str]) -> None:
    """
    Validate that all required fields are present in the data.

    Args:
        data (dict): Data to validate
        required_fields (list): List of required field names

    Raises:
        MissingRequiredFieldError: If any required field is missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)

    if missing_fields:
        raise MissingRequiredFieldError(
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def validate_content_length(content: str, max_length: int, platform: str) -> None:
    """
    Validate that content length is within platform limits.

    Args:
        content (str): Content to validate
        max_length (int): Maximum allowed length
        platform (str): Platform name for error message

    Raises:
        ContentTooLongError: If content exceeds maximum length
    """
    if len(content) > max_length:
        raise ContentTooLongError(
            f"Content too long for {platform}. "
            f"Maximum length: {max_length}, actual length: {len(content)}"
        )


def validate_platform_name(platform: str) -> None:
    """
    Validate that the platform name is supported.

    Args:
        platform (str): Platform name to validate

    Raises:
        UnsupportedPlatformError: If platform is not supported
    """
    supported_platforms = ["x", "reddit", "medium", "substack", "linkedin"]
    if platform.lower() not in supported_platforms:
        raise UnsupportedPlatformError(
            f"Unsupported platform: {platform}. "
            f"Supported platforms: {', '.join(supported_platforms)}"
        )
