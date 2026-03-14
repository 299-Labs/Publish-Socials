"""
Reddit Publisher module.
"""

import logging
from typing import Any, Dict, Optional

import praw
from ..errors import APIError, AuthenticationError, PublishingError
from ..utils import ContentFormatter


class RedditPublisher:
    """
    Publisher for Reddit platform.
    """

    def __init__(self, config):
        """
        Initialize Reddit publisher.

        Args:
            config: Configuration object
        """
        self.config = config
        self.formatter = ContentFormatter()
        self.logger = logging.getLogger(__name__)

        # Validate configuration
        if not self.config.validate_platform_config("reddit"):
            raise AuthenticationError("Reddit platform not properly configured")

        # Initialize Reddit instance
        self.reddit = self._initialize_reddit()

    def _initialize_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client."""
        try:
            reddit = praw.Reddit(
                client_id=self.config.get("reddit", "client_id"),
                client_secret=self.config.get("reddit", "client_secret"),
                user_agent=self.config.get("reddit", "user_agent"),
                username=self.config.get("reddit", "username"),
                password=self.config.get("reddit", "password"),
            )

            # Test authentication
            reddit.auth.limits

            return reddit

        except Exception as e:
            raise AuthenticationError(f"Failed to initialize Reddit client: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if connected to Reddit API.

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
        Test connection to Reddit API.

        Returns:
            dict: Connection test result
        """
        try:
            # Test by getting current user
            user = self.reddit.user.me()

            return {
                "success": True,
                "user": user.name,
                "has_verified_email": user.has_verified_email,
            }

        except Exception as e:
            raise APIError(f"Connection test failed: {str(e)}")

    def publish(
        self, article: Dict[str, Any], subreddit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Publish article to Reddit.

        Args:
            article (dict): Article data
            subreddit (str, optional): Subreddit to post to

        Returns:
            dict: Publishing result
        """
        try:
            # Format content for Reddit
            content = self.formatter.format_for_platform(
                article["content"], "reddit", article.get("title")
            )

            # Determine subreddit
            if not subreddit:
                subreddit = self._get_default_subreddit()

            # Create post
            submission = self._create_post(
                subreddit=subreddit,
                title=article["title"],
                content=content,
                flair_id=article.get("flair_id"),
                nsfw=article.get("nsfw", False),
                spoiler=article.get("spoiler", False),
            )

            return {
                "success": True,
                "post_id": submission.id,
                "url": submission.url,
                "subreddit": submission.subreddit.display_name,
                "title": submission.title,
            }

        except Exception as e:
            self.logger.error(f"Failed to publish to Reddit: {str(e)}")
            raise PublishingError(f"Failed to publish to Reddit: {str(e)}")

    def _get_default_subreddit(self) -> str:
        """Get default subreddit from configuration."""
        default_subreddit = self.config.get("reddit", "default_subreddit")
        if not default_subreddit:
            raise PublishingError("No default subreddit specified and none provided")
        return default_subreddit

    def _create_post(
        self,
        subreddit: str,
        title: str,
        content: str,
        flair_id: Optional[str] = None,
        nsfw: bool = False,
        spoiler: bool = False,
    ) -> Any:
        """
        Create a Reddit post.

        Args:
            subreddit (str): Subreddit name
            title (str): Post title
            content (str): Post content
            flair_id (str, optional): Flair ID
            nsfw (bool): Whether post is NSFW
            spoiler (bool): Whether post is a spoiler

        Returns:
            praw.models.Submission: Created submission
        """
        subreddit_obj = self.reddit.subreddit(subreddit)

        # Create self-post
        submission = subreddit_obj.submit(
            title=title, selftext=content, flair_id=flair_id, nsfw=nsfw, spoiler=spoiler
        )

        return submission

    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """
        Get information about a subreddit.

        Args:
            subreddit_name (str): Subreddit name

        Returns:
            dict: Subreddit information
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            return {
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": subreddit.public_description,
                "subscribers": subreddit.subscribers,
                "active_users": subreddit.active_user_count,
                "created_utc": subreddit.created_utc,
                "over18": subreddit.over18,
                "spoilers_enabled": subreddit.spoilers_enabled,
                "submission_type": subreddit.submission_type,
            }

        except Exception as e:
            raise APIError(f"Failed to get subreddit info: {str(e)}")

    def get_user_subreddits(self) -> list:
        """
        Get list of subreddits the user can post to.

        Returns:
            list: List of subreddit names
        """
        try:
            subreddits = []
            for subreddit in self.reddit.user.subreddits(limit=None):
                subreddits.append(subreddit.display_name)
            return subreddits

        except Exception as e:
            raise APIError(f"Failed to get user subreddits: {str(e)}")

    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific post.

        Args:
            post_id (str): Post ID

        Returns:
            dict: Post statistics
        """
        try:
            submission = self.reddit.submission(id=post_id)

            return {
                "id": submission.id,
                "title": submission.title,
                "score": submission.score,
                "upvotes": submission.ups,
                "downvotes": submission.downs,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "url": submission.url,
                "is_self": submission.is_self,
                "selftext": submission.selftext,
                "subreddit": submission.subreddit.display_name,
                "author": str(submission.author),
                "upvote_ratio": submission.upvote_ratio,
                "gilded": submission.gilded,
                "locked": submission.locked,
                "stickied": submission.stickied,
            }

        except Exception as e:
            raise APIError(f"Failed to get post stats: {str(e)}")

    def comment_on_post(self, post_id: str, comment: str) -> Dict[str, Any]:
        """
        Comment on a post.

        Args:
            post_id (str): Post ID
            comment (str): Comment content

        Returns:
            dict: Comment result
        """
        try:
            submission = self.reddit.submission(id=post_id)
            comment_obj = submission.reply(comment)

            return {
                "success": True,
                "comment_id": comment_obj.id,
                "url": comment_obj.permalink,
            }

        except Exception as e:
            raise PublishingError(f"Failed to comment on post: {str(e)}")

    def get_flairs(self, subreddit_name: str) -> list:
        """
        Get available flairs for a subreddit.

        Args:
            subreddit_name (str): Subreddit name

        Returns:
            list: List of available flairs
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            flairs = []

            for flair in subreddit.flair.link_templates:
                flairs.append(
                    {
                        "id": flair["id"],
                        "text": flair["text"],
                        "css_class": flair.get("css_class", ""),
                        "mod_only": flair.get("mod_only", False),
                    }
                )

            return flairs

        except Exception as e:
            raise APIError(f"Failed to get flairs: {str(e)}")
