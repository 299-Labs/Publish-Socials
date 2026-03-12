import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv


class Config:
    """
    Configuration management for the Publisher application.
    Handles loading and validation of API credentials and settings.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path (str, optional): Path to .env file
        """
        if config_path:
            load_dotenv(config_path)
        else:
            load_dotenv()  # Load from default .env file
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {
            # X (Twitter) Configuration
            'x': {
                'api_key': os.getenv('X_API_KEY'),
                'api_secret': os.getenv('X_API_SECRET'),
                'access_token': os.getenv('X_ACCESS_TOKEN'),
                'access_secret': os.getenv('X_ACCESS_SECRET'),
                'bearer_token': os.getenv('X_BEARER_TOKEN')
            },
            
            # Reddit Configuration
            'reddit': {
                'client_id': os.getenv('REDDIT_CLIENT_ID'),
                'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
                'user_agent': os.getenv('REDDIT_USER_AGENT'),
                'username': os.getenv('REDDIT_USERNAME'),
                'password': os.getenv('REDDIT_PASSWORD')
            },
            
            # Medium Configuration
            'medium': {
                'api_token': os.getenv('MEDIUM_API_TOKEN'),
                'user_id': os.getenv('MEDIUM_USER_ID')
            },
            
            # Substack Configuration
            'substack': {
                'email': os.getenv('SUBSTACK_EMAIL'),
                'password': os.getenv('SUBSTACK_PASSWORD'),
                'domain': os.getenv('SUBSTACK_DOMAIN')
            },
            
            # LinkedIn Configuration
            'linkedin': {
                'access_token': os.getenv('LINKEDIN_ACCESS_TOKEN'),
                'profile_urn': os.getenv('LINKEDIN_PROFILE_URN'),
                'client_id': os.getenv('LINKEDIN_CLIENT_ID'),
                'client_secret': os.getenv('LINKEDIN_CLIENT_SECRET')
            },
            
            # Application Settings
            'app': {
                'rate_limit_delay': int(os.getenv('RATE_LIMIT_DELAY', 1)),
                'max_retries': int(os.getenv('MAX_RETRIES', 3)),
                'timeout': int(os.getenv('TIMEOUT', 30)),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true'
            }
        }
        
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
        return self._config.get(platform, {}).get(key, default)
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """
        Get all configuration for a specific platform.
        
        Args:
            platform (str): Platform name
            
        Returns:
            dict: Platform configuration
        """
        return self._config.get(platform, {})
    
    def validate_platform_config(self, platform: str) -> bool:
        """
        Validate that all required configuration is present for a platform.
        
        Args:
            platform (str): Platform name
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_fields = self._get_required_fields(platform)
        
        for field in required_fields:
            if not self.get(platform, field):
                return False
        
        return True
    
    def _get_required_fields(self, platform: str) -> List[str]:
        """
        Get list of required configuration fields for a platform.
        
        Args:
            platform (str): Platform name
            
        Returns:
            list: List of required field names
        """
        required_fields = {
            'x': ['api_key', 'api_secret', 'access_token', 'access_secret'],
            'reddit': ['client_id', 'client_secret', 'user_agent', 'username', 'password'],
            'medium': ['api_token', 'user_id'],
            'substack': ['email', 'password', 'domain'],
            'linkedin': ['access_token', 'profile_urn']
        }
        
        return required_fields.get(platform, [])
    
    def get_all_platforms(self) -> List[str]:
        """
        Get list of all supported platforms.
        
        Returns:
            list: List of platform names
        """
        return ['x', 'reddit', 'medium', 'substack', 'linkedin']
    
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
        return self.get('app', key, default)
    
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
        with open(file_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    @classmethod
    def create_env_template(cls, file_path: str = '.env.template') -> None:
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
RATE_LIMIT_DELAY=1
MAX_RETRIES=3
TIMEOUT=30
DEBUG=false
"""
        
        with open(file_path, 'w') as f:
            f.write(template)
        
        print(f"Environment template created at: {file_path}")
        print("Please copy this file to .env and fill in your actual API credentials.")


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Convenience function to load configuration.
    
    Args:
        config_path (str, optional): Path to configuration file
        
    Returns:
        Config: Configuration object
    """
    return Config(config_path)