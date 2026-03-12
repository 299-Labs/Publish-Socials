"""
LinkedIn Publisher module.
"""

import logging
from typing import Any, Dict, Optional

import requests
from errors import APIError, AuthenticationError, PublishingError
from utils import ContentFormatter


class LinkedInPublisher:
    """
    Publisher for LinkedIn platform.
    """

    def __init__(self, config):
        """
        Initialize LinkedIn publisher.

        Args:
            config: Configuration object
        """
        self.config = config
        self.formatter = ContentFormatter()
        self.base_url = "https://api.linkedin.com/v2"
        self.logger = logging.getLogger(__name__)

        # Validate configuration
        if not self.config.validate_platform_config("linkedin"):
            raise AuthenticationError("LinkedIn platform not properly configured")

    def is_connected(self) -> bool:
        """
        Check if connected to LinkedIn API.

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
        Test connection to LinkedIn API.

        Returns:
            dict: Connection test result
        """
        try:
            # Get current user info
            user_info = self.get_user_info()

            return {
                "success": True,
                "user": user_info.get("localizedFirstName", "Unknown"),
                "last_name": user_info.get("localizedLastName", ""),
                "profile_url": user_info.get("profileUrl", ""),
            }

        except Exception as e:
            raise APIError(f"Connection test failed: {str(e)}")

    def publish(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish article to LinkedIn.

        Args:
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for LinkedIn
            content = self.formatter.format_for_platform(
                article["content"], "linkedin", article.get("title")
            )

            # Create post
            author_urn = self.config.get("linkedin", "profile_urn")
            result = self._create_post(
                text=content,
                title=article.get("title") or None,
                visibility=article.get("visibility", "PUBLIC"),
                author_urn=author_urn,
            )

            return {
                "success": True,
                "post_id": result.get("id"),
                "url": f"https://www.linkedin.com/feed/update/{result.get('id')}",
                "visibility": result.get("visibility"),
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to LinkedIn: {str(e)}")
            raise PublishingError(f"Failed to publish to LinkedIn: {str(e)}")

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for LinkedIn API."""
        return {
            "Authorization": f"Bearer {self.config.get('linkedin', 'access_token')}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def get_user_info(self) -> Dict[str, Any]:
        """
        Get current user information.

        Returns:
            dict: User information
        """
        try:
            headers = self.get_headers()
            profile_urn = self.config.get("linkedin", "profile_urn")
            url = f"{self.base_url}/me"

            response = requests.get(url, headers=headers, timeout=10)

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

    def get_organization_info(self, organization_id: str) -> Dict[str, Any]:
        """
        Get organization information.

        Args:
            organization_id (str): Organization ID

        Returns:
            dict: Organization information
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/organizations/{organization_id}"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                raise APIError(
                    f"Failed to get organization info: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get organization info: {str(e)}")

    def _create_post(
        self,
        text: str,
        title: Optional[str] = None,
        visibility: str = "PUBLIC",
        author_urn: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a post on LinkedIn.

        Args:
            text (str): Post text
            title (str): Post title
            visibility (str): Post visibility (PUBLIC, CONNECTIONS)
            author_urn (str): Author URN

        Returns:
            dict: API response
        """
        headers = self.get_headers()
        url = f"{self.base_url}/ugcPosts"

        # Prepare post data
        if author_urn:
            author = author_urn
        else:
            # Get current user URN
            user_info = self.get_user_info()
            author_id = user_info.get("id")
            if author_id:
                author = f"urn:li:person:{author_id}"
            else:
                raise APIError("Unable to determine author URN")

        data = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
        }

        # Add title if provided
        if title:
            data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"][
                "text"
            ] = f"{title}\n\n{text}"

        response = requests.post(url, headers=headers, json=data, timeout=30)

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

    def publish_to_organization(
        self, organization_id: str, article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish article to an organization page.

        Args:
            organization_id (str): Organization ID
            article (dict): Article data

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for LinkedIn
            content = self.formatter.format_for_platform(
                article["content"], "linkedin", article.get("title")
            )

            # Create organization post
            result = self._create_organization_post(
                organization_id=organization_id,
                text=content,
                title=article.get("title") or None,
                visibility=article.get("visibility", "PUBLIC"),
            )

            return {
                "success": True,
                "post_id": result.get("id"),
                "url": f"https://www.linkedin.com/company/{organization_id}/update/{result.get('id')}",
                "visibility": result.get("visibility"),
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to organization: {str(e)}")
            raise PublishingError(f"Failed to publish to organization: {str(e)}")

    def _create_organization_post(
        self,
        organization_id: str,
        text: str,
        title: Optional[str] = None,
        visibility: str = "PUBLIC",
    ) -> Dict[str, Any]:
        """
        Create a post on an organization page.

        Args:
            organization_id (str): Organization ID
            text (str): Post text
            title (str): Post title
            visibility (str): Post visibility

        Returns:
            dict: API response
        """
        headers = self.get_headers()
        url = f"{self.base_url}/ugcPosts"

        data = {
            "author": f"urn:li:organization:{organization_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": visibility},
        }

        # Add title if provided
        if title:
            data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"][
                "text"
            ] = f"{title}\n\n{text}"

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            error_msg = f"Failed to create organization post: {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {error_details}"
            except Exception as e:
                # Log the error but don't fail silently
                error_msg += f" - Error: {str(e)}"

            raise APIError(error_msg, response.status_code, response.json())

    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific post.

        Args:
            post_id (str): Post ID

        Returns:
            dict: Post statistics
        """
        try:
            headers = self.get_headers()
            url = f"{self.base_url}/socialActions/{post_id}"

            response = requests.get(url, headers=headers, timeout=10)

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
            headers = self.get_headers()
            url = f"{self.base_url}/ugcPosts/{post_id}"

            response = requests.delete(url, headers=headers, timeout=10)

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

    def get_followers_count(self, organization_id: str = None) -> int:
        """
        Get followers count for user or organization.

        Args:
            organization_id (str, optional): Organization ID. If None, gets user followers.

        Returns:
            int: Number of followers
        """
        try:
            headers = self.get_headers()

            if organization_id:
                url = f"{self.base_url}/organizations/{organization_id}?projection=(followerCount)"
            else:
                url = f"{self.base_url}/me?projection=(numFollowers)"

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("followerCount", 0)
                    if organization_id
                    else data.get("numFollowers", 0)
                )
            else:
                raise APIError(
                    f"Failed to get followers count: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get followers count: {str(e)}")

    def get_recent_posts(self, limit: int = 10, organization_id: str = None) -> list:
        """
        Get recent posts from user or organization.

        Args:
            limit (int): Number of posts to retrieve
            organization_id (str, optional): Organization ID. If None, gets user posts.

        Returns:
            list: List of recent posts
        """
        try:
            headers = self.get_headers()

            if organization_id:
                url = f"{self.base_url}/organizations/{organization_id}/posts"
            else:
                url = f"{self.base_url}/me/posts"

            params = {"q": "authors", "count": limit}

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                return response.json().get("elements", [])
            else:
                raise APIError(
                    f"Failed to get recent posts: {response.status_code}",
                    response.status_code,
                    response.json(),
                )

        except Exception as e:
            raise APIError(f"Failed to get recent posts: {str(e)}")
