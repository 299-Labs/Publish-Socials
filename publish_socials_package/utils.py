"""
Utility functions for the Publisher application.
"""

import html
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import markdown

from .errors import ContentTooLongError, MissingRequiredFieldError, ValidationError


class ContentFormatter:
    """
    Utility class for formatting and processing content for different platforms.
    """

    # Platform-specific content limits
    PLATFORM_LIMITS = {
        "x": 280,  # X/Twitter character limit
        "reddit": 40000,  # Reddit self-text limit
        "medium": 100000,  # Medium article limit (approximate)
        "substack": 50000,  # Substack newsletter limit (approximate)
        "linkedin": 3000,  # LinkedIn post limit
    }

    # Platform-specific formatting rules
    PLATFORM_FORMATTING = {
        "x": {
            "max_hashtags": 3,
            "max_mentions": 3,
            "supports_links": True,
            "supports_images": True,
        },
        "reddit": {
            "supports_markdown": True,
            "supports_links": True,
            "supports_images": True,
            "supports_tables": True,
        },
        "medium": {
            "supports_markdown": True,
            "supports_html": True,
            "supports_images": True,
            "supports_embeds": True,
        },
        "substack": {
            "supports_markdown": True,
            "supports_html": True,
            "supports_images": True,
            "supports_embeds": True,
        },
        "linkedin": {
            "supports_markdown": False,
            "supports_html": False,
            "supports_links": True,
            "supports_images": True,
        },
    }

    def format_for_platform(
        self, content: str, platform: str, title: Optional[str] = None
    ) -> str:
        """
        Format content for a specific platform.

        Args:
            content (str): Original content
            platform (str): Target platform
            title (str, optional): Article title

        Returns:
            str: Formatted content
        """
        platform = platform.lower()

        if platform not in self.PLATFORM_LIMITS:
            raise ValidationError(f"Unsupported platform: {platform}")

        # Convert markdown to HTML if needed
        if self.PLATFORM_FORMATTING[platform].get("supports_markdown"):
            content = self._convert_markdown_to_html(content)

        # Apply platform-specific formatting
        if platform == "x":
            content = self._format_for_x(content, title)
        elif platform == "reddit":
            content = self._format_for_reddit(content, title)
        elif platform in ["medium", "substack"]:
            content = self._format_for_longform(content, title, platform)
        elif platform == "linkedin":
            content = self._format_for_linkedin(content, title)

        # Validate content length
        max_length = self.PLATFORM_LIMITS[platform]
        if len(content) > max_length:
            raise ContentTooLongError(
                f"Content too long for {platform}. "
                f"Maximum length: {max_length}, actual length: {len(content)}"
            )

        return content

    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML."""
        return markdown.markdown(content, extensions=["fenced_code", "tables"])

    def _format_for_x(self, content: str, title: Optional[str]) -> str:
        """Format content for X (Twitter)."""
        # Remove HTML tags for X
        content = html.unescape(content)
        content = re.sub(r"<[^>]+>", "", content)

        # Add title if provided
        if title:
            content = f"{title}\n\n{content}"

        # Ensure content fits within character limit
        max_length = self.PLATFORM_LIMITS["x"]
        if len(content) > max_length:
            # Truncate and add ellipsis
            content = content[: max_length - 3] + "..."

        return content

    def _format_for_reddit(self, content: str, title: Optional[str]) -> str:
        """Format content for Reddit."""
        # Reddit supports markdown, so we can keep most formatting
        if title:
            content = f"## {title}\n\n{content}"

        return content

    def _format_for_longform(
        self, content: str, title: Optional[str], platform: str
    ) -> str:
        """Format content for Medium or Substack."""
        # Add title if provided
        if title:
            content = f"<h1>{title}</h1>\n\n{content}"

        return content

    def _format_for_linkedin(self, content: str, title: Optional[str]) -> str:
        """Format content for LinkedIn."""
        # Remove HTML tags for LinkedIn
        content = html.unescape(content)
        content = re.sub(r"<[^>]+>", "", content)

        # Add title if provided
        if title:
            content = f"{title}\n\n{content}"

        return content

    def apply_template(self, article: Dict[str, Any], template: str) -> str:
        """
        Apply a template to format an article.

        Args:
            article (dict): Article data
            template (str): Template string with placeholders

        Returns:
            str: Formatted content
        """
        # Validate required fields
        required_fields = ["title", "content"]
        for field in required_fields:
            if field not in article:
                raise MissingRequiredFieldError(f"Missing required field: {field}")

        # Prepare template variables
        template_vars = {
            "title": article.get("title", ""),
            "content": article.get("content", ""),
            "author": article.get("author", ""),
            "tags": ", ".join(article.get("tags", [])),
            "publish_date": article.get("publish_date", ""),
            "summary": article.get("summary", ""),
            "excerpt": article.get("excerpt", ""),
        }

        # Apply template
        try:
            formatted_content = template.format(**template_vars)
        except KeyError as e:
            raise ValidationError(f"Template contains unknown variable: {e}")
        except Exception as e:
            raise ValidationError(f"Template formatting error: {e}")

        return formatted_content

    def extract_hashtags(self, content: str) -> List[str]:
        """
        Extract hashtags from content.

        Args:
            content (str): Content to extract hashtags from

        Returns:
            list: List of hashtags
        """
        hashtags = re.findall(r"#(\w+)", content)
        return [tag.lower() for tag in hashtags]

    def extract_mentions(self, content: str) -> List[str]:
        """
        Extract mentions from content.

        Args:
            content (str): Content to extract mentions from

        Returns:
            list: List of mentions
        """
        mentions = re.findall(r"@(\w+)", content)
        return mentions

    def sanitize_content(self, content: str, platform: str) -> str:
        """
        Sanitize content for a specific platform.

        Args:
            content (str): Content to sanitize
            platform (str): Target platform

        Returns:
            str: Sanitized content
        """
        platform = platform.lower()

        # Remove platform-specific unsupported elements
        if platform == "x":
            # Remove HTML tags
            content = re.sub(r"<[^>]+>", "", content)
        elif platform == "linkedin":
            # Remove HTML tags
            content = re.sub(r"<[^>]+>", "", content)

        # Remove extra whitespace
        content = re.sub(r"\s+", " ", content).strip()

        return content

    def truncate_content(
        self, content: str, max_length: int, suffix: str = "..."
    ) -> str:
        """
        Truncate content to a maximum length.

        Args:
            content (str): Content to truncate
            max_length (int): Maximum length
            suffix (str): Suffix to add when truncating

        Returns:
            str: Truncated content
        """
        if len(content) <= max_length:
            return content

        # Find the last space before the max_length to avoid cutting words
        truncated = content[: max_length - len(suffix)]
        last_space = truncated.rfind(" ")

        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + suffix


def validate_article(article: Dict[str, Any]) -> None:
    """
    Validate article data.

    Args:
        article (dict): Article data to validate

    Raises:
        ValidationError: If validation fails
    """
    required_fields = ["title", "content"]

    # Check required fields
    for field in required_fields:
        if field not in article or not article[field]:
            raise MissingRequiredFieldError(f"Missing required field: {field}")

    # Validate field types
    if not isinstance(article["title"], str):
        raise ValidationError("Title must be a string")

    if not isinstance(article["content"], str):
        raise ValidationError("Content must be a string")

    # Validate optional fields
    if "tags" in article and not isinstance(article["tags"], list):
        raise ValidationError("Tags must be a list")

    if "publish_date" in article:
        try:
            datetime.fromisoformat(article["publish_date"])
        except ValueError:
            raise ValidationError(
                "Invalid publish_date format. Use ISO format (YYYY-MM-DD)"
            )

    # Validate content length
    if len(article["content"]) < 10:
        raise ValidationError("Content is too short")

    if len(article["title"]) > 200:
        raise ValidationError("Title is too long")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for file systems
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "", filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]

    return sanitized


def generate_slug(title: str) -> str:
    """
    Generate a URL-friendly slug from a title.

    Args:
        title (str): Title to convert to slug

    Returns:
        str: URL-friendly slug
    """
    # Convert to lowercase
    slug = title.lower()

    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")

    # Remove invalid characters
    slug = re.sub(r"[^a-z0-9\-]", "", slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug
