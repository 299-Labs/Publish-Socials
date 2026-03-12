import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

# Import platform-specific modules
from platforms.x_publisher import XPublisher
from platforms.reddit_publisher import RedditPublisher
from platforms.medium_publisher import MediumPublisher
from platforms.substack_publisher import SubstackPublisher
from platforms.linkedin_publisher import LinkedInPublisher

# Import configuration and utilities
from config import Config
from utils import ContentFormatter, validate_article
from errors import PublishingError, ConfigurationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Publisher:
    """
    Main Publisher class that coordinates publishing across multiple platforms.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Publisher with configuration.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        self.config = Config(config_path)
        self.formatter = ContentFormatter()
        
        # Initialize platform publishers
        self.x_publisher = XPublisher(self.config)
        self.reddit_publisher = RedditPublisher(self.config)
        self.medium_publisher = MediumPublisher(self.config)
        self.substack_publisher = SubstackPublisher(self.config)
        self.linkedin_publisher = LinkedInPublisher(self.config)
        
        logger.info("Publisher initialized successfully")
    
    def publish_to_all(self, article: Dict[str, Any], 
                      platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Publish article to all specified platforms.
        
        Args:
            article (dict): Article data with title, content, tags, etc.
            platforms (list, optional): List of platforms to publish to.
                                      If None, publishes to all platforms.
        
        Returns:
            dict: Results of publishing attempts for each platform
        """
        if platforms is None:
            platforms = ['x', 'reddit', 'medium', 'substack', 'linkedin']
        
        results = {}
        
        # Validate article
        try:
            validate_article(article)
        except ValueError as e:
            raise PublishingError(f"Article validation failed: {str(e)}")
        
        # Publish to each platform
        for platform in platforms:
            try:
                if platform == 'x':
                    result = self.publish_to_x(article)
                elif platform == 'reddit':
                    result = self.publish_to_reddit(article)
                elif platform == 'medium':
                    result = self.publish_to_medium(article)
                elif platform == 'substack':
                    result = self.publish_to_substack(article)
                elif platform == 'linkedin':
                    result = self.publish_to_linkedin(article)
                else:
                    logger.warning(f"Unknown platform: {platform}")
                    continue
                
                results[platform] = {
                    'success': True,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to publish to {platform}: {str(e)}")
                results[platform] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    def publish_to_x(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to X (Twitter).
        
        Args:
            article (dict): Article data
            
        Returns:
            dict: Publishing result
        """
        return self.x_publisher.publish(article)
    
    def publish_to_reddit(self, article: Dict[str, Any], 
                         subreddit: Optional[str] = None) -> Dict[str, Any]:
        """
        Publish article to Reddit.
        
        Args:
            article (dict): Article data
            subreddit (str, optional): Subreddit to post to
            
        Returns:
            dict: Publishing result
        """
        return self.reddit_publisher.publish(article, subreddit)
    
    def publish_to_medium(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to Medium.
        
        Args:
            article (dict): Article data
            
        Returns:
            dict: Publishing result
        """
        return self.medium_publisher.publish(article)
    
    def publish_to_substack(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to Substack.
        
        Args:
            article (dict): Article data
            
        Returns:
            dict: Publishing result
        """
        return self.substack_publisher.publish(article)
    
    def publish_to_linkedin(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to LinkedIn.
        
        Args:
            article (dict): Article data
            
        Returns:
            dict: Publishing result
        """
        return self.linkedin_publisher.publish(article)
    
    def publish_with_template(self, article: Dict[str, Any], 
                             template: str, 
                             platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Publish article using a template to format content.
        
        Args:
            article (dict): Article data
            template (str): Template string with placeholders
            platforms (list, optional): List of platforms to publish to
            
        Returns:
            dict: Results of publishing attempts
        """
        # Format content using template
        formatted_content = self.formatter.apply_template(article, template)
        article['content'] = formatted_content
        
        # Publish to platforms
        return self.publish_to_all(article, platforms)
    
    def get_platform_status(self) -> Dict[str, Any]:
        """
        Get status of all platform connections.
        
        Returns:
            dict: Status of each platform
        """
        status = {}
        
        platforms = [
            ('x', self.x_publisher),
            ('reddit', self.reddit_publisher),
            ('medium', self.medium_publisher),
            ('substack', self.substack_publisher),
            ('linkedin', self.linkedin_publisher)
        ]
        
        for name, publisher in platforms:
            try:
                status[name] = {
                    'connected': publisher.is_connected(),
                    'error': None
                }
            except Exception as e:
                status[name] = {
                    'connected': False,
                    'error': str(e)
                }
        
        return status
    
    def test_all_connections(self) -> Dict[str, Any]:
        """
        Test connections to all platforms.
        
        Returns:
            dict: Connection test results
        """
        results = {}
        
        platforms = [
            ('x', self.x_publisher),
            ('reddit', self.reddit_publisher),
            ('medium', self.medium_publisher),
            ('substack', self.substack_publisher),
            ('linkedin', self.linkedin_publisher)
        ]
        
        for name, publisher in platforms:
            try:
                result = publisher.test_connection()
                results[name] = {
                    'success': True,
                    'result': result
                }
            except Exception as e:
                results[name] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results


def main():
    """
    Example usage of the Publisher class.
    """
    # Initialize publisher
    publisher = Publisher()
    
    # Test connections
    print("Testing platform connections...")
    status = publisher.test_all_connections()
    for platform, result in status.items():
        if result['success']:
            print(f"✓ {platform}: Connected")
        else:
            print(f"✗ {platform}: {result['error']}")
    
    # Example content
    content = {
        "title": "My First Post",
        "content": "This is the content of my post in markdown format.",
        "tags": ["technology", "programming", "python"],
        "publish_date": "2024-01-01",
        "author": "Your Name"
    }
    
    # Publish to all platforms
    print("\nPublishing to all platforms...")
    results = publisher.publish_to_all(content)
    
    for platform, result in results.items():
        if result['success']:
            print(f"✓ {platform}: Published successfully")
        else:
            print(f"✗ {platform}: {result['error']}")


if __name__ == "__main__":
    main()