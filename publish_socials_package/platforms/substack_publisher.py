"""
Substack Publisher module.
"""

import logging
from typing import Any, Dict, Optional

import requests
from ..errors import APIError, AuthenticationError, PublishingError
from ..utils import ContentFormatter


class SubstackPublisher:
    """
    Publisher for Substack platform.
    """

    def __init__(self, config):
        """
        Initialize Substack publisher.

        Args:
            config: Configuration object
        """
        self.config = config
        self.formatter = ContentFormatter()
        self.base_url = "https://api.substack.com"
        self.logger = logging.getLogger(__name__)

        # Validate configuration
        if not self.config.validate_platform_config("substack"):
            raise AuthenticationError("Substack platform not properly configured")

        # Initialize session
        self.session = self._initialize_session()

    def _initialize_session(self) -> requests.Session:
        """Initialize authenticated session for Substack API."""
        session = requests.Session()

        # Set up authentication
        email = self.config.get("substack", "email")
        password = self.config.get("substack", "password")

        if email and password:
            # Basic authentication for Substack
            session.auth = (email, password)

        # Set headers
        session.headers.update(
            {
                "User-Agent": "Publisher/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        return session

    def is_connected(self) -> bool:
        """
        Check if connected to Substack API.

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
        Test connection to Substack API.

        Returns:
            dict: Connection test result
        """
        try:
            # Get current user info
            user_info = self.get_user_info()

            return {
                "success": True,
                "user": user_info.get("name", "Unknown"),
                "email": user_info.get("email", ""),
                "domain": self.config.get("substack", "domain", ""),
            }

        except Exception as e:
            raise APIError(f"Connection test failed: {str(e)}")

    def publish(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to Substack.

        Args:
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for Substack
            content = self.formatter.format_for_platform(
                article["content"], "substack", article.get("title")
            )

            # Create newsletter/post
            result = self._create_post(
                title=article["title"],
                body=content,
                publish_status=article.get("publish_status") or "draft",
                tags=article.get("tags") or [],
                send_to_subscribers=article.get("send_to_subscribers") or False,
            )

            return {
                "success": True,
                "post_id": result.get("id"),
                "url": result.get("url"),
                "title": result.get("title"),
                "status": result.get("status"),
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to Substack: {str(e)}")
            raise PublishingError(f"Failed to publish to Substack: {str(e)}")

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.

        Returns:
            dict: User information
        """
        try:
            url = f"{self.base_url}/user/me"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to get user info: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get user info: {str(e)}")

    def get_publication_info(self) -> Dict[str, Any]:
        """
        Get publication information.

        Returns:
            dict: Publication information
        """
        try:
            domain = self.config.get("substack", "domain")
            if not domain:
                raise PublishingError("No Substack domain configured")

            url = f"{self.base_url}/publication/{domain}"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to get publication info: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get publication info: {str(e)}")

    def _create_post(
        self,
        title: str,
        body: str,
        publish_status: str = "draft",
        tags: list = None,
        send_to_subscribers: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a post/newsletter on Substack.

        Args:
            title (str): Post title
            body (str): Post body in HTML
            publish_status (str): Publish status (draft, publish)
            tags (list): List of tags
            send_to_subscribers (bool): Whether to send to subscribers

        Returns:
            dict: API response
        """
        domain = self.config.get("substack", "domain")
        if not domain:
            raise PublishingError("No Substack domain configured")

        url = f"{self.base_url}/publication/{domain}/posts"

        # Prepare post data
        data = {
            "title": title,
            "body": body,
            "status": publish_status,
            "sendToSubscribers": send_to_subscribers,
        }

        if tags:
            data["tags"] = tags

        response = self.session.post(url, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to create post: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())

    def update_post(
        self, post_id: str, title: str = None, body: str = None, tags: list = None
    ) -> Dict[str, Any]:
        """
        Update an existing post.

        Args:
            post_id (str): Post ID
            title (str): New title
            body (str): New body
            tags (list): New tags

        Returns:
            dict: API response
        """
        try:
            domain = self.config.get("substack", "domain")
            url = f"{self.base_url}/publication/{domain}/posts/{post_id}"

            data = {}
            if title:
                data["title"] = title
            if body:
                data["body"] = body
            if tags:
                data["tags"] = tags

            if not data:
                raise PublishingError("No updates provided")

            response = self.session.put(url, json=data, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to update post: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to update post: {str(e)}")

    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific post.

        Args:
            post_id (str): Post ID

        Returns:
            dict: Post statistics
        """
        try:
            domain = self.config.get("substack", "domain")
            url = f"{self.base_url}/publication/{domain}/posts/{post_id}/stats"

            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to get post stats: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get post stats: {str(e)}")

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a post.

        Args:
            post_id (str): Post ID

        Returns:
            bool: True if deleted successfully
        """
        try:
            domain = self.config.get("substack", "domain")
            url = f"{self.base_url}/publication/{domain}/posts/{post_id}"

            response = self.session.delete(url, timeout=10)

            if response.status_code == 204:
                return True
            else:
                raise APIError(
                    f"Failed to delete post: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to delete post: {str(e)}")

    def get_subscriber_count(self) -> int:
        """
        Get subscriber count.

        Returns:
            int: Number of subscribers
        """
        try:
            publication_info = self.get_publication_info()
            return publication_info.get("subscribers", 0)

        except Exception as e:
            raise APIError(f"Failed to get subscriber count: {str(e)}")

    def get_recent_posts(self, limit: int = 10) -> list:
        """
        Get recent posts from the publication.

        Args:
            limit (int): Number of posts to retrieve

        Returns:
            list: List of recent posts
        """
        try:
            domain = self.config.get("substack", "domain")
            url = f"{self.base_url}/publication/{domain}/posts"
            params = {"limit": limit}

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return response.json().get("posts", [])
            else:
                raise APIError(
                    f"Failed to get recent posts: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get recent posts: {str(e)}")

    def schedule_post(
        self, article: Dict[str, Any], schedule_time: str
    ) -> Dict[str, Any]:
        """
        Schedule a post for later publication.

        Args:
            article (dict): Article data
            schedule_time (str): ISO format datetime string

        Returns:
            dict: Scheduling result
        """
        try:
            # Format content for Substack
            content = self.formatter.format_for_platform(
                article["content"], "substack", article.get("title")
            )

            # Create scheduled post
            result = self._create_scheduled_post(
                title=article["title"],
                body=content,
                schedule_time=schedule_time,
                tags=article.get("tags", []),
                send_to_subscribers=article.get("send_to_subscribers", False),
            )

            return {
                "success": True,
                "post_id": result.get("id"),
                "url": result.get("url"),
                "scheduled_for": result.get("scheduled_for"),
            }

        except Exception as e:
            self.logger.error(f"Failed to schedule post: {str(e)}")
            raise PublishingError(f"Failed to schedule post: {str(e)}")

    def _create_scheduled_post(
        self,
        title: str,
        body: str,
        schedule_time: str,
        tags: list = None,
        send_to_subscribers: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a scheduled post on Substack.

        Args:
            title (str): Post title
            body (str): Post body
            schedule_time (str): Scheduled publish time
            tags (list): List of tags
            send_to_subscribers (bool): Whether to send to subscribers

        Returns:
            dict: API response
        """
        domain = self.config.get("substack", "domain")
        if not domain:
            raise PublishingError("No Substack domain configured")

        url = f"{self.base_url}/publication/{domain}/posts/scheduled"

        data = {
            "title": title,
            "body": body,
            "scheduled_for": schedule_time,
            "sendToSubscribers": send_to_subscribers,
        }

        if tags:
            data["tags"] = tags

        response = self.session.post(url, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to create scheduled post: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())
