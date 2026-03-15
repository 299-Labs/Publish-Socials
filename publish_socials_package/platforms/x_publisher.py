"""
X (Twitter) Publisher module.
"""

import logging
from typing import Any, Dict, Optional

import requests

from ..errors import APIError, AuthenticationError, PublishingError
from ..utils import ContentFormatter


class XPublisher:
    """
    Publisher for X (Twitter) platform.
    """

    def __init__(self, config):
        """
        Initialize X publisher.

        Args:
            config: Configuration object
        """
        self.config = config
        self.formatter = ContentFormatter()
        self.base_url = "https://api.twitter.com/2"
        self.logger = logging.getLogger(__name__)

        # Validate configuration
        if not self.config.validate_platform_config("x"):
            raise AuthenticationError("X platform not properly configured")

    def is_connected(self) -> bool:
        """
        Check if connected to X API.

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            self.test_connection()
            return True
        except Exception:
            return False

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to X API.

        Returns:
            dict: Connection test result
        """
        try:
            # Make a simple API call to verify credentials
            headers = self._get_headers()
            url = f"{self.base_url}/users/me"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return {
                    "success": True,
                    "user": response.json().get("data", {}).get("username", "Unknown"),
                }
            else:
                raise APIError(
                    f"Connection test failed with status {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Connection test failed: {str(e)}")

    def publish(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to X.

        Args:
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for X
            content = self.formatter.format_for_platform(
                article["content"], "x", article.get("title")
            )

            # Add hashtags if provided
            if "tags" in article and article["tags"]:
                hashtags = self._generate_hashtags(article["tags"])
                content = f"{content}\n\n{hashtags}"

            # Publish tweet
            result = self._post_tweet(content)

            return {
                "success": True,
                "tweet_id": result.get("data", {}).get("id"),
                "url": f"https://x.com/user/status/{result.get('data', {}).get('id')}",
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to X: {str(e)}")
            raise PublishingError(f"Failed to publish to X: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for X API."""
        return {
            "Authorization": f"Bearer {self.config.get('x', 'bearer_token')}",
            "Content-Type": "application/json",
        }

    def _post_tweet(self, content: str) -> Dict[str, Any]:
        """
        Post a tweet to X.

        Args:
            content (str): Tweet content

        Returns:
            dict: API response
        """
        url = f"{self.base_url}/tweets"
        headers = self._get_headers()
        data = {"text": content}

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to post tweet: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())

    def _generate_hashtags(self, tags: list) -> str:
        """
        Generate hashtags from tags.

        Args:
            tags (list): List of tags

        Returns:
            str: Hashtag string
        """
        # Limit to 3 hashtags for X
        max_hashtags = 3
        hashtags = []

        for tag in tags[:max_hashtags]:
            # Clean tag and convert to hashtag
            clean_tag = "".join(c for c in tag if c.isalnum())
            if clean_tag:
                hashtags.append(f"#{clean_tag}")

        return " ".join(hashtags)

    def schedule_tweet(
        self, article: Dict[str, Any], schedule_time: str
    ) -> Dict[str, Any]:
        """
        Schedule a tweet for later publication.

        Args:
            article (dict): Article data
            schedule_time (str): ISO format datetime string

        Returns:
            dict: Scheduling result
        """
        # Note: X API v2 doesn't have native scheduling
        # This would require implementing a scheduling system
        # or using a third-party service

        raise NotImplementedError(
            "Tweet scheduling is not implemented in X API v2. "
            "Consider using a third-party scheduling service."
        )

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.

        Returns:
            dict: User information
        """
        try:
            headers = self._get_headers()
            url = f"{self.base_url}/users/me"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                raise APIError(
                    f"Failed to get user info: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get user info: {str(e)}")

    def get_tweet_stats(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific tweet.

        Args:
            tweet_id (str): Tweet ID

        Returns:
            dict: Tweet statistics
        """
        try:
            headers = self._get_headers()
            url = f"{self.base_url}/tweets/{tweet_id}"
            params = {"tweet.fields": "public_metrics,created_at,author_id"}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                raise APIError(
                    f"Failed to get tweet stats: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get tweet stats: {str(e)}")
