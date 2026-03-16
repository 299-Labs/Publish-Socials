"""
Tests for the main Publisher class.
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

from publish_socials_package.config import Config
from publish_socials_package.errors import ConfigurationError, PublishingError
from publish_socials_package.publish_socials import Publisher


class TestPublisher(unittest.TestCase):
    """Test cases for Publisher class."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = Mock(spec=Config)
        self.mock_config.validate_platform_config.return_value = True

    @patch("publish_socials_package.publish_socials.XPublisher")
    @patch("publish_socials_package.publish_socials.RedditPublisher")
    @patch("publish_socials_package.publish_socials.MediumPublisher")
    @patch("publish_socials_package.publish_socials.SubstackPublisher")
    @patch("publish_socials_package.publish_socials.LinkedInPublisher")
    def test_publisher_initialization(
        self, mock_linkedin, mock_substack, mock_medium, mock_reddit, mock_x
    ):
        """Test Publisher initialization."""
        # Mock platform publishers
        mock_x_instance = Mock()
        mock_reddit_instance = Mock()
        mock_medium_instance = Mock()
        mock_substack_instance = Mock()
        mock_linkedin_instance = Mock()

        mock_x.return_value = mock_x_instance
        mock_reddit.return_value = mock_reddit_instance
        mock_medium.return_value = mock_medium_instance
        mock_substack.return_value = mock_substack_instance
        mock_linkedin.return_value = mock_linkedin_instance

        # Initialize publisher
        publisher = Publisher(self.mock_config)

        # Verify initialization
        self.assertEqual(publisher.config, self.mock_config)
        self.assertIsNotNone(publisher.formatter)

        # Verify platform publishers were initialized
        mock_x.assert_called_once_with(self.mock_config)
        mock_reddit.assert_called_once_with(self.mock_config)
        mock_medium.assert_called_once_with(self.mock_config)
        mock_substack.assert_called_once_with(self.mock_config)
        mock_linkedin.assert_called_once_with(self.mock_config)

    def test_publish_to_all_success(self):
        """Test publishing to all platforms successfully."""
        # Create mock platform publishers
        mock_x = Mock()
        mock_x.publish.return_value = {"success": True, "result": {"id": "x123"}}

        mock_reddit = Mock()
        mock_reddit.publish.return_value = {"success": True, "result": {"id": "r123"}}

        mock_medium = Mock()
        mock_medium.publish.return_value = {"success": True, "result": {"id": "m123"}}

        mock_substack = Mock()
        mock_substack.publish.return_value = {"success": True, "result": {"id": "s123"}}

        mock_linkedin = Mock()
        mock_linkedin.publish.return_value = {"success": True, "result": {"id": "l123"}}

        # Create publisher with mocked platforms
        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        # Create test content
        content = {"title": "Test Content", "content": "Test content", "tags": ["test"]}

        # Publish to all platforms
        results = publisher.publish_to_all(content)

        # Verify results
        self.assertEqual(len(results), 5)
        self.assertTrue(results["x"]["success"])
        self.assertTrue(results["reddit"]["success"])
        self.assertTrue(results["medium"]["success"])
        self.assertTrue(results["substack"]["success"])
        self.assertTrue(results["linkedin"]["success"])

        # Verify platform methods were called
        mock_x.publish.assert_called_once_with(content)
        mock_reddit.publish.assert_called_once_with(content, None)
        mock_medium.publish.assert_called_once_with(content)
        mock_substack.publish.assert_called_once_with(content)
        mock_linkedin.publish.assert_called_once_with(content)

    def test_publish_to_all_with_failures(self):
        """Test publishing to all platforms with some failures."""
        # Create mock platform publishers with some failures
        mock_x = Mock()
        mock_x.publish.return_value = {"success": True, "result": {"id": "x123"}}

        mock_reddit = Mock()
        mock_reddit.publish.side_effect = PublishingError("Reddit failed")

        mock_medium = Mock()
        mock_medium.publish.return_value = {"success": True, "result": {"id": "m123"}}

        mock_substack = Mock()
        mock_substack.publish.side_effect = ConfigurationError("Substack config error")

        mock_linkedin = Mock()
        mock_linkedin.publish.return_value = {"success": True, "result": {"id": "l123"}}

        # Create publisher with mocked platforms
        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        # Create test article
        article = {"title": "Test Article", "content": "Test content", "tags": ["test"]}

        # Publish to all platforms
        results = publisher.publish_to_all(article)

        # Verify results
        self.assertEqual(len(results), 5)
        self.assertTrue(results["x"]["success"])
        self.assertFalse(results["reddit"]["success"])
        self.assertTrue(results["medium"]["success"])
        self.assertFalse(results["substack"]["success"])
        self.assertTrue(results["linkedin"]["success"])

        # Verify error messages
        self.assertIn("Reddit failed", results["reddit"]["error"])
        self.assertIn("Substack config error", results["substack"]["error"])

    def test_publish_to_all_custom_platforms(self):
        """Test publishing to specific platforms only."""
        # Create mock platform publishers
        mock_x = Mock()
        mock_x.publish.return_value = {"success": True, "result": {"id": "x123"}}

        mock_reddit = Mock()
        mock_reddit.publish.return_value = {"success": True, "result": {"id": "r123"}}

        mock_medium = Mock()
        mock_medium.publish.return_value = {"success": True, "result": {"id": "m123"}}

        mock_substack = Mock()
        mock_substack.publish.return_value = {"success": True, "result": {"id": "s123"}}

        mock_linkedin = Mock()
        mock_linkedin.publish.return_value = {"success": True, "result": {"id": "l123"}}

        # Create publisher with mocked platforms
        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        # Create test article
        article = {"title": "Test Article", "content": "Test content", "tags": ["test"]}

        # Publish to specific platforms
        platforms = ["x", "medium", "linkedin"]
        results = publisher.publish_to_all(article, platforms)

        # Verify results
        self.assertEqual(len(results), 3)
        self.assertIn("x", results)
        self.assertIn("medium", results)
        self.assertIn("linkedin", results)
        self.assertNotIn("reddit", results)
        self.assertNotIn("substack", results)

    def test_publish_to_individual_platforms(self):
        """Test publishing to individual platforms."""
        # Create mock platform publishers
        mock_x = Mock()
        mock_x.publish.return_value = {"success": True, "result": {"id": "x123"}}

        mock_reddit = Mock()
        mock_reddit.publish.return_value = {"success": True, "result": {"id": "r123"}}

        mock_medium = Mock()
        mock_medium.publish.return_value = {"success": True, "result": {"id": "m123"}}

        mock_substack = Mock()
        mock_substack.publish.return_value = {"success": True, "result": {"id": "s123"}}

        mock_linkedin = Mock()
        mock_linkedin.publish.return_value = {"success": True, "result": {"id": "l123"}}

        # Create publisher with mocked platforms
        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        # Create test article
        article = {"title": "Test Article", "content": "Test content", "tags": ["test"]}

        # Test individual platform publishing
        x_result = publisher.publish_to_x(article)
        reddit_result = publisher.publish_to_reddit(article)
        medium_result = publisher.publish_to_medium(article)
        substack_result = publisher.publish_to_substack(article)
        linkedin_result = publisher.publish_to_linkedin(article)

        # Verify results
        self.assertEqual(x_result, {"success": True, "result": {"id": "x123"}})
        self.assertEqual(reddit_result, {"success": True, "result": {"id": "r123"}})
        self.assertEqual(medium_result, {"success": True, "result": {"id": "m123"}})
        self.assertEqual(substack_result, {"success": True, "result": {"id": "s123"}})
        self.assertEqual(linkedin_result, {"success": True, "result": {"id": "l123"}})

    def test_publish_to_reddit_with_subreddit(self):
        """Test publishing to Reddit with specific subreddit."""
        mock_reddit = Mock()
        mock_reddit.publish.return_value = {"success": True, "result": {"id": "r123"}}

        publisher = Publisher(config=self.mock_config)
        publisher.reddit_publisher = mock_reddit

        article = {"title": "Test Article", "content": "Test content"}

        result = publisher.publish_to_reddit(article, subreddit="programming")

        mock_reddit.publish.assert_called_once_with(article, "programming")
        self.assertEqual(result, {"success": True, "result": {"id": "r123"}})

    def test_publish_with_template(self):
        """Test publishing with template."""
        # Mock formatter instance
        mock_formatter = Mock()
        mock_formatter.apply_template.return_value = "Formatted content"

        # Mock platform publishers
        mock_x = Mock()
        mock_x.publish.return_value = {"success": True, "result": {"id": "x123"}}

        mock_medium = Mock()
        mock_medium.publish.return_value = {"success": True, "result": {"id": "m123"}}

        # Create publisher and replace the formatter instance
        publisher = Publisher(config=self.mock_config)
        publisher.formatter = mock_formatter
        publisher.x_publisher = mock_x
        publisher.medium_publisher = mock_medium

        article = {
            "title": "Test Article",
            "content": "Original content",
            "tags": ["test"],
        }

        template = "# {title}\n\n{content}\n\nTags: {tags}"
        platforms = ["x", "medium"]

        results = publisher.publish_with_template(article, template, platforms)

        # Verify template was applied
        mock_formatter.apply_template.assert_called_once_with(article, template)

        # Verify article content was updated
        expected_article = article.copy()
        expected_article["content"] = "Formatted content"

        # Verify platforms were called with updated article
        mock_x.publish.assert_called_once_with(expected_article)
        mock_medium.publish.assert_called_once_with(expected_article)

    def test_get_platform_status(self):
        """Test getting platform connection status."""
        # Mock platform publishers
        mock_x = Mock()
        mock_x.is_connected.return_value = True

        mock_reddit = Mock()
        mock_reddit.is_connected.return_value = False

        mock_medium = Mock()
        mock_medium.is_connected.return_value = True

        mock_substack = Mock()
        mock_substack.is_connected.return_value = True

        mock_linkedin = Mock()
        mock_linkedin.is_connected.return_value = False

        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        status = publisher.get_platform_status()

        self.assertEqual(status["x"]["connected"], True)
        self.assertEqual(status["reddit"]["connected"], False)
        self.assertEqual(status["medium"]["connected"], True)
        self.assertEqual(status["substack"]["connected"], True)
        self.assertEqual(status["linkedin"]["connected"], False)

    def test_test_all_connections(self):
        """Test testing all platform connections."""
        # Mock platform publishers
        mock_x = Mock()
        mock_x.test_connection.return_value = {"success": True, "user": "testuser"}

        mock_reddit = Mock()
        mock_reddit.test_connection.side_effect = Exception("Reddit error")

        mock_medium = Mock()
        mock_medium.test_connection.return_value = {
            "success": True,
            "user": "mediumuser",
        }

        mock_substack = Mock()
        mock_substack.test_connection.side_effect = Exception("Substack error")

        mock_linkedin = Mock()
        mock_linkedin.test_connection.return_value = {
            "success": True,
            "user": "linkedinuser",
        }

        publisher = Publisher(config=self.mock_config)
        publisher.x_publisher = mock_x
        publisher.reddit_publisher = mock_reddit
        publisher.medium_publisher = mock_medium
        publisher.substack_publisher = mock_substack
        publisher.linkedin_publisher = mock_linkedin

        results = publisher.test_all_connections()

        self.assertEqual(len(results), 5)
        self.assertTrue(results["x"]["success"])
        self.assertFalse(results["reddit"]["success"])
        self.assertTrue(results["medium"]["success"])
        self.assertFalse(results["substack"]["success"])
        self.assertTrue(results["linkedin"]["success"])

        self.assertEqual(results["x"]["result"]["user"], "testuser")
        self.assertIn("Reddit error", results["reddit"]["error"])
        self.assertEqual(results["medium"]["result"]["user"], "mediumuser")
        self.assertIn("Substack error", results["substack"]["error"])
        self.assertEqual(results["linkedin"]["result"]["user"], "linkedinuser")


if __name__ == "__main__":
    unittest.main()
