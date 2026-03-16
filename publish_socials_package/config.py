import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from .errors import ConfigurationError


class Config:
    """
    Configuration management for the Publisher application.
    Handles loading and validation of API credentials and settings with secure testing support.
    """

    # Default values for non-critical settings
    DEFAULTS = {
        "app": {
            "rate_limit_delay": 1,
            "max_retries": 3,
            "timeout": 30,
            "debug": False,
        }
    }

    # Required fields for each platform
    REQUIRED_FIELDS = {
        "x": ["api_key", "api_secret", "access_token", "access_secret"],
        "reddit": ["client_id", "client_secret", "user_agent", "username", "password"],
        "medium": ["api_token", "user_id"],
        "substack": ["email", "password", "domain"],
        "linkedin": ["access_token", "profile_urn"],
    }

    def __init__(
        self, env_file: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize configuration with optional environment file and overrides.

        Args:
            env_file (str, optional): Path to .env file
            overrides (dict, optional): Dictionary of configuration overrides for testing
        """
        self.overrides = overrides or {}

        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env file

        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with fallbacks."""
        config = {}

        # Load platform configurations
        for platform in self.REQUIRED_FIELDS.keys():
            platform_config = {}
            for field in self.REQUIRED_FIELDS[platform]:
                env_key = f"{platform.upper()}_{field.upper()}"
                value = self.overrides.get(platform, {}).get(field)
                if value is None:
                    value = os.getenv(env_key)
                platform_config[field] = value
            config[platform] = platform_config

        # Load application settings with defaults
        app_config = {}
        for key, default_value in self.DEFAULTS["app"].items():
            env_key = f"APP_{key.upper()}"
            value = self.overrides.get("app", {}).get(key)
            if value is None:
                env_value = os.getenv(env_key)
                if env_value is not None:
                    # Convert string values to appropriate types
                    if key == "debug":
                        value = env_value.lower() == "true"
                    elif key in ["rate_limit_delay", "max_retries", "timeout"]:
                        try:
                            value = int(env_value)
                        except ValueError:
                            value = default_value
                    else:
                        value = env_value
                else:
                    value = default_value
            app_config[key] = value

        config["app"] = app_config
        return config

    def get(self, platform: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value for a specific platform and key.

        Args:
            platform (str): Platform name (x, reddit, medium, substack, linkedin)
            key (str): Configuration key
            default (Any, optional): Default value if not found

        Returns:
            Any: Configuration value
        """
        # Check overrides first
        if platform in self.overrides and key in self.overrides[platform]:
            value = self.overrides[platform][key]
            # Convert string values to appropriate types for app settings
            if platform == "app" and key == "debug" and isinstance(value, str):
                return value.lower() == "true"
            elif (
                platform == "app"
                and key in ["rate_limit_delay", "max_retries", "timeout"]
                and isinstance(value, str)
            ):
                try:
                    return int(value)
                except ValueError:
                    pass
            return value

        # Check loaded configuration
        value = self._config.get(platform, {}).get(key)
        if value is not None:
            return value

        # Check environment variables directly (for dynamic loading during tests)
        # Only check if we don't have overrides for this platform
        if platform not in self.overrides:
            env_key = f"{platform.upper()}_{key.upper()}"
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Convert string values to appropriate types
                if platform == "app" and key == "debug":
                    return env_value.lower() == "true"
                elif platform == "app" and key in [
                    "rate_limit_delay",
                    "max_retries",
                    "timeout",
                ]:
                    try:
                        return int(env_value)
                    except ValueError:
                        pass
                return env_value

        return default

    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get all configuration for a specific platform.

        Args:
            platform (str): Platform name

        Returns:
            dict: Platform configuration
        """
        return self._config.get(platform, {}).copy()

    def validate_platform_config(self, platform: str) -> bool:
        """
        Validate that all required configuration is present for a platform.

        Args:
            platform (str): Platform name

        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = self.REQUIRED_FIELDS.get(platform, [])

        for field in required_fields:
            if not self.get(platform, field):
                return False

        return True

    def validate_required_credentials(self, platform: str) -> None:
        """
        Validate that all required credentials are present for a platform.
        Raises a descriptive exception if validation fails.

        Args:
            platform (str): Platform name

        Raises:
            ConfigurationError: If required credentials are missing
        """
        if platform not in self.REQUIRED_FIELDS:
            raise ValueError(f"Unknown platform: {platform}")

        missing_fields = []
        required_fields = self.REQUIRED_FIELDS[platform]

        for field in required_fields:
            if not self.get(platform, field):
                missing_fields.append(field)

        if missing_fields:
            field_list = ", ".join(missing_fields)
            raise ConfigurationError(
                f"Missing required configuration for {platform} platform: {field_list}. "
                f"Please set the following environment variables: "
                f"{', '.join([f'{platform.upper()}_{field.upper()}' for field in missing_fields])}. "
                f"See the documentation for instructions on obtaining these credentials."
            )

    def get_all_platforms(self) -> List[str]:
        """
        Get list of all supported platforms.

        Returns:
            list: List of platform names
        """
        return list(self.REQUIRED_FIELDS.keys())

    def is_platform_configured(self, platform: str) -> bool:
        """
        Check if a platform is properly configured.

        Args:
            platform (str): Platform name

        Returns:
            bool: True if platform is configured, False otherwise
        """
        return self.validate_platform_config(platform)

    def get_app_setting(self, key: str, default: Any = None) -> Any:
        """
        Get application-level configuration setting.

        Args:
            key (str): Setting key
            default (Any, optional): Default value

        Returns:
            Any: Setting value
        """
        return self.get("app", key, default)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            dict: Configuration as dictionary
        """
        return self._config.copy()

    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to a file.

        Args:
            file_path (str): Path to save configuration file
        """
        with open(file_path, "w") as f:
            json.dump(self._config, f, indent=2)

    @classmethod
    def create_env_template(cls, file_path: str = ".env.template") -> None:
        """
        Create a template .env file with all required configuration fields.

        Args:
            file_path (str): Path to save template file
        """
        template = """# X (Twitter) API Configuration
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_SECRET=your_x_access_secret
X_BEARER_TOKEN=your_x_bearer_token

# Reddit API Configuration
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Medium API Configuration
MEDIUM_API_TOKEN=your_medium_api_token
MEDIUM_USER_ID=your_medium_user_id

# Substack Configuration
SUBSTACK_EMAIL=your_substack_email
SUBSTACK_PASSWORD=your_substack_password
SUBSTACK_DOMAIN=your_substack_domain

# LinkedIn API Configuration
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PROFILE_URN=your_linkedin_profile_urn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Application Settings
APP_RATE_LIMIT_DELAY=1
APP_MAX_RETRIES=3
APP_TIMEOUT=30
APP_DEBUG=false
"""

        with open(file_path, "w") as f:
            f.write(template)

        print(f"Environment template created at: {file_path}")
        print("Please copy this file to .env and fill in your actual API credentials.")


def load_config(
    env_file: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
) -> Config:
    """
    Convenience function to load configuration.

    Args:
        env_file (str, optional): Path to configuration file
        overrides (dict, optional): Configuration overrides for testing

    Returns:
        Config: Configuration object
    """
    return Config(env_file, overrides)
