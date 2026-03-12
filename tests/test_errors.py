"""
Tests for error handling.
"""

import unittest

from errors import (
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
    validate_content_length,
    validate_platform_name,
    validate_required_fields,
)


class TestCustomExceptions(unittest.TestCase):
    """Test cases for custom exception classes."""

    def test_publishing_error(self):
        """Test PublishingError exception."""
        error = PublishingError("Test error message")
        self.assertEqual(str(error), "Test error message")

    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error = ConfigurationError("Configuration error")
        self.assertEqual(str(error), "Configuration error")

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("Authentication failed")
        self.assertEqual(str(error), "Authentication failed")

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        error = RateLimitError("Rate limit exceeded")
        self.assertEqual(str(error), "Rate limit exceeded")

    def test_network_error(self):
        """Test NetworkError exception."""
        error = NetworkError("Network connection failed")
        self.assertEqual(str(error), "Network connection failed")

    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid content")
        self.assertEqual(str(error), "Invalid content")

    def test_platform_error(self):
        """Test PlatformError exception."""
        error = PlatformError("Platform error")
        self.assertEqual(str(error), "Platform error")

    def test_content_too_long_error(self):
        """Test ContentTooLongError exception."""
        error = ContentTooLongError("Content too long")
        self.assertEqual(str(error), "Content too long")

    def test_missing_required_field_error(self):
        """Test MissingRequiredFieldError exception."""
        error = MissingRequiredFieldError("Missing field")
        self.assertEqual(str(error), "Missing field")

    def test_invalid_format_error(self):
        """Test InvalidFormatError exception."""
        error = InvalidFormatError("Invalid format")
        self.assertEqual(str(error), "Invalid format")

    def test_platform_not_configured_error(self):
        """Test PlatformNotConfiguredError exception."""
        error = PlatformNotConfiguredError("Platform not configured")
        self.assertEqual(str(error), "Platform not configured")

    def test_api_error(self):
        """Test APIError exception."""
        error = APIError("API error", 404, {"error": "Not found"})
        self.assertEqual(str(error), "API error")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.response, {"error": "Not found"})

    def test_unsupported_platform_error(self):
        """Test UnsupportedPlatformError exception."""
        error = UnsupportedPlatformError("Unsupported platform")
        self.assertEqual(str(error), "Unsupported platform")

    def test_template_error(self):
        """Test TemplateError exception."""
        error = TemplateError("Template error")
        self.assertEqual(str(error), "Template error")

    def test_file_error(self):
        """Test FileError exception."""
        error = FileError("File error")
        self.assertEqual(str(error), "File error")


class TestValidationErrorFunctions(unittest.TestCase):
    """Test cases for validation error functions."""

    def test_validate_required_fields_success(self):
        """Test validate_required_fields with all fields present."""
        data = {"title": "Test", "content": "Content", "author": "Author"}
        required_fields = ["title", "content"]

        # Should not raise any exception
        validate_required_fields(data, required_fields)

    def test_validate_required_fields_missing_field(self):
        """Test validate_required_fields with missing field."""
        data = {"title": "Test", "author": "Author"}
        required_fields = ["title", "content"]

        with self.assertRaises(MissingRequiredFieldError) as context:
            validate_required_fields(data, required_fields)

        self.assertIn("Missing required fields", str(context.exception))
        self.assertIn("content", str(context.exception))

    def test_validate_required_fields_empty_field(self):
        """Test validate_required_fields with empty field."""
        data = {"title": "Test", "content": "", "author": "Author"}
        required_fields = ["title", "content"]

        with self.assertRaises(MissingRequiredFieldError) as context:
            validate_required_fields(data, required_fields)

        self.assertIn("Missing required fields", str(context.exception))
        self.assertIn("content", str(context.exception))

    def test_validate_required_fields_none_field(self):
        """Test validate_required_fields with None field."""
        data = {"title": "Test", "content": None, "author": "Author"}
        required_fields = ["title", "content"]

        with self.assertRaises(MissingRequiredFieldError) as context:
            validate_required_fields(data, required_fields)

        self.assertIn("Missing required fields", str(context.exception))
        self.assertIn("content", str(context.exception))

    def test_validate_content_length_success(self):
        """Test validate_content_length with content within limits."""
        content = "This is valid content"
        max_length = 100
        platform = "test"

        # Should not raise any exception
        validate_content_length(content, max_length, platform)

    def test_validate_content_length_too_long(self):
        """Test validate_content_length with content exceeding limits."""
        content = "This content is definitely too long for the specified maximum length"
        max_length = 20
        platform = "test"

        with self.assertRaises(ContentTooLongError) as context:
            validate_content_length(content, max_length, platform)

        self.assertIn("Content too long for test", str(context.exception))
        self.assertIn("Maximum length: 20", str(context.exception))
        self.assertIn(f"actual length: {len(content)}", str(context.exception))

    def test_validate_platform_name_success(self):
        """Test validate_platform_name with supported platform."""
        platform = "x"

        # Should not raise any exception
        validate_platform_name(platform)

    def test_validate_platform_name_unsupported(self):
        """Test validate_platform_name with unsupported platform."""
        platform = "unsupported"

        with self.assertRaises(UnsupportedPlatformError) as context:
            validate_platform_name(platform)

        self.assertIn("Unsupported platform: unsupported", str(context.exception))
        self.assertIn("Supported platforms", str(context.exception))


class TestHandlePublishingErrorDecorator(unittest.TestCase):
    """Test cases for handle_publishing_error decorator."""

    def test_handle_publishing_error_no_exception(self):
        """Test decorator with function that doesn't raise exception."""
        from errors import handle_publishing_error

        @handle_publishing_error
        def test_function():
            return "success"

        result = test_function()
        self.assertEqual(result, "success")

    def test_handle_publishing_error_publishing_error(self):
        """Test decorator with function that raises PublishingError."""
        from errors import PublishingError, handle_publishing_error

        @handle_publishing_error
        def test_function():
            raise PublishingError("Original error")

        with self.assertRaises(PublishingError) as context:
            test_function()

        self.assertEqual(str(context.exception), "Original error")

    def test_handle_publishing_error_generic_exception(self):
        """Test decorator with function that raises generic exception."""
        from errors import handle_publishing_error

        @handle_publishing_error
        def test_function():
            raise ValueError("Generic error")

        with self.assertRaises(PublishingError) as context:
            test_function()

        self.assertIn("Unexpected error in test_function", str(context.exception))
        self.assertIn("Generic error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
