"""
Tests for configuration management.
"""

import os
import tempfile
import unittest
from unittest.mock import patch

from publish_socials_package.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_env_file = None

    def tearDown(self):
        """Clean up test environment."""
        if self.temp_env_file and os.path.exists(self.temp_env_file):
            os.unlink(self.temp_env_file)

    def test_config_initialization(self):
        """Test basic configuration initialization."""
        config = Config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config._config, dict)

    def test_config_with_file(self):
        """Test configuration loading from file."""
        # Create a temporary .env file
        self.temp_env_file = tempfile.mkstemp(suffix=".env")[1]
        with open(self.temp_env_file, "w") as f:
            f.write("TEST_VAR=test_value\n")

        config = Config(self.temp_env_file)
        self.assertEqual(config.get("app", "test_var"), "test_value")

    def test_get_method(self):
        """Test get method functionality."""
        config = Config()

        # Test with default value
        result = config.get("nonexistent", "key", "default")
        self.assertEqual(result, "default")

        # Test with environment variable
        with patch.dict(os.environ, {"TEST_VAR": "env_value"}):
            config = Config()
            result = config.get("app", "test_var")
            self.assertEqual(result, "env_value")

    def test_validate_platform_config(self):
        """Test platform configuration validation."""
        config = Config()

        # Test with missing configuration
        result = config.validate_platform_config("x")
        self.assertFalse(result)

        # Test with mock configuration
        with patch.dict(
            os.environ,
            {
                "X_API_KEY": "test_key",
                "X_API_SECRET": "test_secret",
                "X_ACCESS_TOKEN": "test_token",
                "X_ACCESS_SECRET": "test_secret",
            },
        ):
            config = Config()
            result = config.validate_platform_config("x")
            self.assertTrue(result)

    def test_get_required_fields(self):
        """Test getting required fields for platforms."""
        config = Config()

        x_fields = config._get_required_fields("x")
        self.assertIn("api_key", x_fields)
        self.assertIn("api_secret", x_fields)
        self.assertIn("access_token", x_fields)
        self.assertIn("access_secret", x_fields)

        # Test unknown platform
        unknown_fields = config._get_required_fields("unknown")
        self.assertEqual(unknown_fields, [])

    def test_get_all_platforms(self):
        """Test getting all supported platforms."""
        config = Config()
        platforms = config.get_all_platforms()

        expected_platforms = ["x", "reddit", "medium", "substack", "linkedin"]
        self.assertEqual(set(platforms), set(expected_platforms))

    def test_is_platform_configured(self):
        """Test platform configuration check."""
        config = Config()

        # Test with missing configuration
        result = config.is_platform_configured("x")
        self.assertFalse(result)

        # Test with mock configuration
        with patch.dict(
            os.environ,
            {
                "X_API_KEY": "test_key",
                "X_API_SECRET": "test_secret",
                "X_ACCESS_TOKEN": "test_token",
                "X_ACCESS_SECRET": "test_secret",
            },
        ):
            config = Config()
            result = config.is_platform_configured("x")
            self.assertTrue(result)

    def test_get_app_setting(self):
        """Test getting application settings."""
        config = Config()

        # Test with default value
        result = config.get_app_setting("nonexistent", "default")
        self.assertEqual(result, "default")

        # Test with environment variable
        with patch.dict(os.environ, {"DEBUG": "true"}):
            config = Config()
            result = config.get_app_setting("debug")
            self.assertTrue(result)

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertIn("x", config_dict)
        self.assertIn("reddit", config_dict)
        self.assertIn("medium", config_dict)
        self.assertIn("substack", config_dict)
        self.assertIn("linkedin", config_dict)
        self.assertIn("app", config_dict)

    def test_create_env_template(self):
        """Test creating environment template file."""
        template_file = tempfile.mkstemp(suffix=".env.template")[1]

        try:
            Config.create_env_template(template_file)

            # Check if file was created
            self.assertTrue(os.path.exists(template_file))

            # Check if file contains expected content
            with open(template_file, "r") as f:
                content = f.read()
                self.assertIn("X_API_KEY", content)
                self.assertIn("REDDIT_CLIENT_ID", content)
                self.assertIn("MEDIUM_API_TOKEN", content)
                self.assertIn("SUBSTACK_EMAIL", content)
                self.assertIn("LINKEDIN_ACCESS_TOKEN", content)

        finally:
            if os.path.exists(template_file):
                os.unlink(template_file)


if __name__ == "__main__":
    unittest.main()
