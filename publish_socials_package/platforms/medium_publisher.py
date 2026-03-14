"""
Medium Publisher module.
"""

import logging
from typing import Any, Dict, Optional

import requests
from ..errors import APIError, AuthenticationError, PublishingError
from ..utils import ContentFormatter


class MediumPublisher:
    """
    Publisher for Medium platform.
    """

    def __init__(self, config):
        """
        Initialize Medium publisher.

        Args:
            config: Configuration object
        """
        self.config = config
        self.formatter = ContentFormatter()
        self.base_url = "https://api.medium.com/v1"
        self.logger = logging.getLogger(__name__)

        # Validate configuration
        if not self.config.validate_platform_config("medium"):
            raise AuthenticationError("Medium platform not properly configured")

    def is_connected(self) -> bool:
        """
        Check if connected to Medium API.

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
        Test connection to Medium API.

        Returns:
            dict: Connection test result
        """
        try:
            # Get current user info
            user_info = self.get_user_info()

            return {
                "success": True,
                "user": user_info.get("name", "Unknown"),
                "username": user_info.get("username", ""),
                "url": user_info.get("url", ""),
            }

        except Exception as e:
            raise APIError(f"Connection test failed: {str(e)}")

    def publish(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to Medium.

        Args:
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for Medium
            content = self.formatter.format_for_platform(
                article["content"], "medium", article.get("title")
            )

            # Create article
            result = self._create_article(
                title=article["title"],
                content=content,
                tags=article.get("tags") or [],
                publish_status=article.get("publish_status") or "draft",
                canonical_url=article.get("canonical_url"),
                license=article.get("license") or "all-rights-reserved",
            )

            return {
                "success": True,
                "article_id": result.get("data", {}).get("id"),
                "url": result.get("data", {}).get("url"),
                "title": result.get("data", {}).get("title"),
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to Medium: {str(e)}")
            raise PublishingError(f"Failed to publish to Medium: {str(e)}")

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Medium API."""
        return {
            "Authorization": f"Bearer {self.config.get('medium', 'api_token')}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.

        Returns:
            dict: User information
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/me"

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

    def get_user_publications(self) -> list:
        """
        Get list of publications the user can publish to.

        Returns:
            list: List of publications
        """
        try:
            headers = self.get_headers()
            user_id = self.config.get("medium", "user_id")
            url = f"{self.base_url}/users/{user_id}/publications"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                raise APIError(
                    f"Failed to get publications: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get publications: {str(e)}")

    def _create_article(
        self,
        title: str,
        content: str,
        tags: list = None,
        publish_status: str = "draft",
        canonical_url: Optional[str] = None,
        license: str = "all-rights-reserved",
    ) -> Dict[str, Any]:
        """
        Create an article on Medium.

        Args:
            title (str): Article title
            content (str): Article content in HTML
            tags (list): List of tags
            publish_status (str): Publish status (draft, public, unlisted)
            canonical_url (str): Canonical URL
            license (str): License type

        Returns:
            dict: API response
        """
        headers = self.get_headers()
        user_id = self.config.get("medium", "user_id")
        url = f"{self.base_url}/users/{user_id}/posts"

        # Prepare article data
        data = {
            "title": title,
            "contentFormat": "html",
            "content": content,
            "tags": tags or [],
            "publishStatus": publish_status,
            "license": license,
        }

        if canonical_url:
            data["canonicalUrl"] = canonical_url

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to create article: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())

    def update_article(
        self, article_id: str, title: str = None, content: str = None, tags: list = None
    ) -> Dict[str, Any]:
        """
        Update an existing article.

        Args:
            article_id (str): Article ID
            title (str): New title
            content (str): New content
            tags (list): New tags

        Returns:
            dict: API response
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/posts/{article_id}"

            data = {}
            if title:
                data["title"] = title
            if content:
                data["content"] = content
            if tags:
                data["tags"] = tags

            if not data:
                raise PublishingError("No updates provided")

            response = requests.put(url, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to update article: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to update article: {str(e)}")

    def get_article_stats(self, article_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific article.

        Args:
            article_id (str): Article ID

        Returns:
            dict: Article statistics
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/posts/{article_id}/stats"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                raise APIError(
                    f"Failed to get article stats: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get article stats: {str(e)}")

    def delete_article(self, article_id: str) -> bool:
        """
        Delete an article.

        Args:
            article_id (str): Article ID

        Returns:
            bool: True if deleted successfully
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/posts/{article_id}"

            response = requests.delete(url, headers=headers, timeout=10)

            if response.status_code == 204:
                return True
            else:
                raise APIError(
                    f"Failed to delete article: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to delete article: {str(e)}")

    def publish_to_publication(
        self, publication_id: str, article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish article to a specific publication.

        Args:
            publication_id (str): Publication ID
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for Medium
            content = self.formatter.format_for_platform(
                article["content"], "medium", article.get("title")
            )

            # Create article in publication
            result = self._create_article_in_publication(
                publication_id=publication_id,
                title=article["title"],
                content=content,
                tags=article.get("tags", []),
                publish_status=article.get("publish_status", "draft"),
            )

            return {
                "success": True,
                "article_id": result.get("data", {}).get("id"),
                "url": result.get("data", {}).get("url"),
                "title": result.get("data", {}).get("title"),
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to publication: {str(e)}")
            raise PublishingError(f"Failed to publish to publication: {str(e)}")

    def _create_article_in_publication(
        self,
        publication_id: str,
        title: str,
        content: str,
        tags: list = None,
        publish_status: str = "draft",
    ) -> Dict[str, Any]:
        """
        Create an article in a specific publication.

        Args:
            publication_id (str): Publication ID
            title (str): Article title
            content (str): Article content
            tags (list): List of tags
            publish_status (str): Publish status

        Returns:
            dict: API response
        """
        headers = self.get_headers()
        url = f"{self.base_url}/publications/{publication_id}/posts"

        data = {
            "title": title,
            "contentFormat": "html",
            "content": content,
            "tags": tags or [],
            "publishStatus": publish_status,
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to create publication article: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())
