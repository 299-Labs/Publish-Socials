"""
Tests for configuration management with secure testing protocols.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from publish_socials_package.config import Config, load_config
from publish_socials_package.errors import ConfigurationError


class TestConfig(unittest.TestCase):
    """Test cases for Config class with secure testing protocols."""

    def setUp(self):
        """Set up test environment."""
        self.temp_env_file = None
        # Clear any environment variables that might interfere with tests
        for key in list(os.environ.keys()):
            if key.startswith(
                ("X_", "REDDIT_", "MEDIUM_", "SUBSTACK_", "LINKEDIN_", "APP_")
            ):
                del os.environ[key]

    def tearDown(self):
        """Clean up test environment."""
        if self.temp_env_file and os.path.exists(self.temp_env_file):
            try:
                os.unlink(self.temp_env_file)
            except PermissionError:
                # File might be in use, skip deletion for temporary files
                pass

    def test_config_initialization_with_overrides(self):
        """Test configuration initialization with overrides for testing."""
        overrides = {
            "x": {
                "api_key": "test_key",
                "api_secret": "test_secret",
            },
            "app": {
                "debug": True,
                "max_retries": 5,
            },
        }

        config = Config(overrides=overrides)

        # Test that overrides are used
        self.assertEqual(config.get("x", "api_key"), "test_key")
        self.assertEqual(config.get("x", "api_secret"), "test_secret")
        self.assertTrue(config.get("app", "debug"))
        self.assertEqual(config.get("app", "max_retries"), 5)

    def test_config_initialization_with_env_file(self):
        """Test configuration loading from file."""
        # Create a temporary .env file
        self.temp_env_file = tempfile.mkstemp(suffix=".env")[1]
        with open(self.temp_env_file, "w") as f:
            f.write("X_API_KEY=test_key_value\n")
            f.write("X_API_SECRET=test_secret_value\n")
            f.write("APP_DEBUG=true\n")

        config = Config(env_file=self.temp_env_file)

        # Test that file values are loaded
        self.assertEqual(config.get("x", "api_key"), "test_key_value")
        self.assertEqual(config.get("x", "api_secret"), "test_secret_value")
        self.assertTrue(config.get("app", "debug"))

    def test_config_with_environment_variable_fallback(self):
        """Test configuration with environment variable fallback during tests."""
        # Test that environment variables are picked up dynamically
        with patch.dict(os.environ, {"X_API_KEY": "env_test_key", "APP_DEBUG": "true"}):
            # Create config without loading env file to test dynamic loading
            config = Config()

            # Should pick up environment variables
            self.assertEqual(config.get("x", "api_key"), "env_test_key")
            self.assertTrue(config.get("app", "debug"))

    def test_config_with_overrides_precedence(self):
        """Test that overrides take precedence over environment variables."""
        with patch.dict(os.environ, {"X_API_KEY": "env_key", "APP_DEBUG": "true"}):
            overrides = {"x": {"api_key": "override_key"}, "app": {"debug": False}}
            config = Config(overrides=overrides)

            # Overrides should take precedence
            self.assertEqual(config.get("x", "api_key"), "override_key")
            self.assertFalse(config.get("app", "debug"))
            # Should fall back to loaded config (which would be None since no env file was loaded)
            self.assertIsNone(config.get("x", "api_secret"))

    def test_get_method_with_default_values(self):
        """Test get method with default values and fallbacks."""
        config = Config()

        # Test default values for app settings
        self.assertEqual(config.get("app", "rate_limit_delay"), 1)
        self.assertEqual(config.get("app", "max_retries"), 3)
        self.assertEqual(config.get("app", "timeout"), 30)
        self.assertFalse(config.get("app", "debug"))

        # Test default for non-existent platform
        self.assertIsNone(config.get("nonexistent", "key"))
        self.assertEqual(config.get("nonexistent", "key", "default"), "default")

    def test_get_method_type_conversion(self):
        """Test that get method properly converts types."""
        overrides = {
            "app": {
                "rate_limit_delay": "5",
                "max_retries": "10",
                "timeout": "60",
                "debug": "true",
            }
        }

        config = Config(overrides=overrides)

        # Test type conversion
        self.assertEqual(config.get("app", "rate_limit_delay"), 5)
        self.assertEqual(config.get("app", "max_retries"), 10)
        self.assertEqual(config.get("app", "timeout"), 60)
        self.assertTrue(config.get("app", "debug"))

    def test_validate_platform_config(self):
        """Test platform configuration validation."""
        # Test with complete configuration
        overrides = {
            "x": {
                "api_key": "key",
                "api_secret": "secret",
                "access_token": "token",
                "access_secret": "secret",
            }
        }
        config = Config(overrides=overrides)
        self.assertTrue(config.validate_platform_config("x"))

        # Test with missing configuration
        overrides = {"x": {"api_key": "key"}}
        config = Config(overrides=overrides)
        self.assertFalse(config.validate_platform_config("x"))

    def test_validate_required_credentials_success(self):
        """Test successful credential validation."""
        overrides = {
            "x": {
                "api_key": "key",
                "api_secret": "secret",
                "access_token": "token",
                "access_secret": "secret",
            }
        }
        config = Config(overrides=overrides)

        # Should not raise an exception
        config.validate_required_credentials("x")

    def test_validate_required_credentials_failure(self):
        """Test credential validation failure with descriptive error."""
        overrides = {"x": {"api_key": "key"}}
        config = Config(overrides=overrides)

        with self.assertRaises(ConfigurationError) as context:
            config.validate_required_credentials("x")

        error_message = str(context.exception)
        self.assertIn("Missing required configuration for x platform", error_message)
        self.assertIn("api_secret", error_message)
        self.assertIn("access_token", error_message)
        self.assertIn("access_secret", error_message)
        self.assertIn("X_API_SECRET", error_message)

    def test_validate_required_credentials_unknown_platform(self):
        """Test validation with unknown platform."""
        config = Config()

        with self.assertRaises(ValueError) as context:
            config.validate_required_credentials("unknown")

        self.assertIn("Unknown platform", str(context.exception))

    def test_get_all_platforms(self):
        """Test getting all supported platforms."""
        config = Config()
        platforms = config.get_all_platforms()

        expected_platforms = ["x", "reddit", "medium", "substack", "linkedin"]
        self.assertEqual(set(platforms), set(expected_platforms))

    def test_is_platform_configured(self):
        """Test platform configuration check."""
        # Test with missing configuration
        config = Config()
        self.assertFalse(config.is_platform_configured("x"))

        # Test with mock configuration
        overrides = {
            "x": {
                "api_key": "key",
                "api_secret": "secret",
                "access_token": "token",
                "access_secret": "secret",
            }
        }
        config = Config(overrides=overrides)
        self.assertTrue(config.is_platform_configured("x"))

    def test_get_app_setting(self):
        """Test getting application settings."""
        config = Config()

        # Test default values
        self.assertEqual(config.get_app_setting("rate_limit_delay"), 1)
        self.assertEqual(config.get_app_setting("max_retries"), 3)
        self.assertEqual(config.get_app_setting("timeout"), 30)
        self.assertFalse(config.get_app_setting("debug"))

        # Test with override
        overrides = {"app": {"debug": True, "max_retries": 10}}
        config = Config(overrides=overrides)
        self.assertTrue(config.get_app_setting("debug"))
        self.assertEqual(config.get_app_setting("max_retries"), 10)

    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        overrides = {"x": {"api_key": "key"}, "app": {"debug": True}}
        config = Config(overrides=overrides)
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertIn("x", config_dict)
        self.assertIn("app", config_dict)
        self.assertEqual(config_dict["x"]["api_key"], "key")
        self.assertTrue(config_dict["app"]["debug"])

    def test_save_to_file(self):
        """Test saving configuration to file."""
        temp_file = tempfile.mkstemp(suffix=".json")[1]

        try:
            overrides = {"x": {"api_key": "key"}, "app": {"debug": True}}
            config = Config(overrides=overrides)
            config.save_to_file(temp_file)

            # Verify file was created and contains expected data
            self.assertTrue(os.path.exists(temp_file))
            with open(temp_file, "r") as f:
                saved_config = json.load(f)

            self.assertEqual(saved_config["x"]["api_key"], "key")
            self.assertTrue(saved_config["app"]["debug"])
        finally:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except PermissionError:
                # File might be in use, skip deletion for temporary files
                pass

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
                self.assertIn("APP_RATE_LIMIT_DELAY", content)

        finally:
            try:
                if os.path.exists(template_file):
                    os.unlink(template_file)
            except PermissionError:
                # File might be in use, skip deletion for temporary files
                pass

    def test_load_config_convenience_function(self):
        """Test the load_config convenience function."""
        overrides = {"x": {"api_key": "test_key"}}
        config = load_config(overrides=overrides)

        self.assertIsInstance(config, Config)
        self.assertEqual(config.get("x", "api_key"), "test_key")

    def test_environment_variable_type_conversion(self):
        """Test environment variable type conversion during dynamic loading."""
        with patch.dict(
            os.environ,
            {
                "APP_RATE_LIMIT_DELAY": "5",
                "APP_MAX_RETRIES": "10",
                "APP_TIMEOUT": "60",
                "APP_DEBUG": "true",
            },
        ):
            config = Config()

            # Should convert string environment variables to appropriate types
            self.assertEqual(config.get("app", "rate_limit_delay"), 5)
            self.assertEqual(config.get("app", "max_retries"), 10)
            self.assertEqual(config.get("app", "timeout"), 60)
            self.assertTrue(config.get("app", "debug"))

    def test_missing_environment_variable_fallback(self):
        """Test fallback when environment variable is missing."""
        # Clear any existing environment variables
        with patch.dict(os.environ, {}, clear=True):
            config = Config()

            # Should use defaults when environment variables are missing
            self.assertEqual(config.get("app", "rate_limit_delay"), 1)
            self.assertEqual(config.get("app", "max_retries"), 3)
            self.assertEqual(config.get("app", "timeout"), 30)
            self.assertFalse(config.get("app", "debug"))

    def test_platform_specific_validation(self):
        """Test validation for different platforms."""
        # Test Reddit validation
        reddit_overrides = {
            "reddit": {
                "client_id": "id",
                "client_secret": "secret",
                "user_agent": "agent",
                "username": "user",
                "password": "pass",
            }
        }
        config = Config(overrides=reddit_overrides)
        self.assertTrue(config.validate_platform_config("reddit"))

        # Test Medium validation
        medium_overrides = {"medium": {"api_token": "token", "user_id": "user"}}
        config = Config(overrides=medium_overrides)
        self.assertTrue(config.validate_platform_config("medium"))

        # Test Substack validation
        substack_overrides = {
            "substack": {
                "email": "test@example.com",
                "password": "pass",
                "domain": "test.substack.com",
            }
        }
        config = Config(overrides=substack_overrides)
        self.assertTrue(config.validate_platform_config("substack"))

        # Test LinkedIn validation
        linkedin_overrides = {
            "linkedin": {"access_token": "token", "profile_urn": "urn:li:person:test"}
        }
        config = Config(overrides=linkedin_overrides)
        self.assertTrue(config.validate_platform_config("linkedin"))


if __name__ == "__main__":
    unittest.main()
