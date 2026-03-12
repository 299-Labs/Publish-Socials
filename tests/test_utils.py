"""
Tests for utility functions.
"""
import unittest
from unittest.mock import patch
from utils import ContentFormatter, validate_article, sanitize_filename, generate_slug
from errors import ValidationError, ContentTooLongError, MissingRequiredFieldError


class TestContentFormatter(unittest.TestCase):
    """Test cases for ContentFormatter class."""
    
    def setUp(self):
        """Set up test environment."""
        self.formatter = ContentFormatter()
    
    def test_format_for_platform_x(self):
        """Test formatting content for X platform."""
        content = "Hello **world**! #test"
        title = "Test Title"
        
        result = self.formatter.format_for_platform(content, 'x', title)
        
        # Should include title
        self.assertIn("Test Title", result)
        # Should remove markdown
        self.assertNotIn("**", result)
        # Should preserve hashtags
        self.assertIn("#test", result)
        # Should be within X character limit
        self.assertLessEqual(len(result), 280)
    
    def test_format_for_platform_reddit(self):
        """Test formatting content for Reddit platform."""
        content = "Hello **world**! [link](http://example.com)"
        title = "Test Title"
        
        result = self.formatter.format_for_platform(content, 'reddit', title)
        
        # Should include title
        self.assertIn("Test Title", result)
        # Should preserve markdown
        self.assertIn("**", result)
        self.assertIn("[link]", result)
    
    def test_format_for_platform_medium(self):
        """Test formatting content for Medium platform."""
        content = "Hello **world**!"
        title = "Test Title"
        
        result = self.formatter.format_for_platform(content, 'medium', title)
        
        # Should include title as HTML
        self.assertIn("<h1>Test Title</h1>", result)
        # Should convert markdown to HTML
        self.assertIn("<strong>world</strong>", result)
    
    def test_format_for_platform_linkedin(self):
        """Test formatting content for LinkedIn platform."""
        content = "Hello **world**!"
        title = "Test Title"
        
        result = self.formatter.format_for_platform(content, 'linkedin', title)
        
        # Should include title
        self.assertIn("Test Title", result)
        # Should remove markdown
        self.assertNotIn("**", result)
    
    def test_format_for_unknown_platform(self):
        """Test formatting content for unknown platform."""
        content = "Hello world!"
        
        with self.assertRaises(ValidationError):
            self.formatter.format_for_platform(content, 'unknown')
    
    def test_apply_template(self):
        """Test applying templates to articles."""
        article = {
            'title': 'Test Title',
            'content': 'Test content',
            'tags': ['tag1', 'tag2'],
            'publish_date': '2024-01-01'
        }
        
        template = "# {title}\n\n{content}\n\nTags: {tags}"
        
        result = self.formatter.apply_template(article, template)
        
        self.assertIn("Test Title", result)
        self.assertIn("Test content", result)
        self.assertIn("tag1, tag2", result)
    
    def test_apply_template_missing_field(self):
        """Test applying template with missing field."""
        article = {'title': 'Test'}
        template = "{missing_field}"
        
        with self.assertRaises(ValidationError):
            self.formatter.apply_template(article, template)
    
    def test_extract_hashtags(self):
        """Test extracting hashtags from content."""
        content = "Hello #world! This is a #test post with #multiple hashtags."
        
        hashtags = self.formatter.extract_hashtags(content)
        
        self.assertIn('world', hashtags)
        self.assertIn('test', hashtags)
        self.assertIn('multiple', hashtags)
        self.assertEqual(len(hashtags), 3)
    
    def test_extract_mentions(self):
        """Test extracting mentions from content."""
        content = "Hello @user1! This is a @test mention."
        
        mentions = self.formatter.extract_mentions(content)
        
        self.assertIn('user1', mentions)
        self.assertIn('test', mentions)
        self.assertEqual(len(mentions), 2)
    
    def test_sanitize_content(self):
        """Test sanitizing content for platforms."""
        content = "  Hello   world!  \n\n  Multiple   spaces  "
        
        # Test X platform sanitization
        result = self.formatter.sanitize_content(content, 'x')
        self.assertEqual(result, "Hello world! Multiple spaces")
        
        # Test LinkedIn platform sanitization
        result = self.formatter.sanitize_content(content, 'linkedin')
        self.assertEqual(result, "Hello world! Multiple spaces")
    
    def test_truncate_content(self):
        """Test truncating content to maximum length."""
        content = "This is a very long content that needs to be truncated."
        
        # Test truncation
        result = self.formatter.truncate_content(content, 20)
        self.assertLessEqual(len(result), 20)
        self.assertTrue(result.endswith("..."))
        
        # Test content that doesn't need truncation
        result = self.formatter.truncate_content(content, 100)
        self.assertEqual(result, content)


class TestValidateArticle(unittest.TestCase):
    """Test cases for validate_article function."""
    
    def test_valid_article(self):
        """Test validation of valid article."""
        article = {
            'title': 'Test Title',
            'content': 'Test content that is long enough to be valid.',
            'tags': ['tag1', 'tag2']
        }
        
        # Should not raise any exception
        validate_article(article)
    
    def test_missing_title(self):
        """Test validation with missing title."""
        article = {'content': 'Test content'}
        
        with self.assertRaises(MissingRequiredFieldError):
            validate_article(article)
    
    def test_missing_content(self):
        """Test validation with missing content."""
        article = {'title': 'Test Title'}
        
        with self.assertRaises(MissingRequiredFieldError):
            validate_article(article)
    
    def test_empty_title(self):
        """Test validation with empty title."""
        article = {
            'title': '',
            'content': 'Test content'
        }
        
        with self.assertRaises(MissingRequiredFieldError):
            validate_article(article)
    
    def test_empty_content(self):
        """Test validation with empty content."""
        article = {
            'title': 'Test Title',
            'content': ''
        }
        
        with self.assertRaises(MissingRequiredFieldError):
            validate_article(article)
    
    def test_short_content(self):
        """Test validation with content that is too short."""
        article = {
            'title': 'Test Title',
            'content': 'Short'
        }
        
        with self.assertRaises(ValidationError):
            validate_article(article)
    
    def test_long_title(self):
        """Test validation with title that is too long."""
        article = {
            'title': 'A' * 201,
            'content': 'Test content'
        }
        
        with self.assertRaises(ValidationError):
            validate_article(article)
    
    def test_invalid_tags(self):
        """Test validation with invalid tags format."""
        article = {
            'title': 'Test Title',
            'content': 'Test content',
            'tags': 'not_a_list'
        }
        
        with self.assertRaises(ValidationError):
            validate_article(article)
    
    def test_invalid_publish_date(self):
        """Test validation with invalid publish date format."""
        article = {
            'title': 'Test Title',
            'content': 'Test content',
            'publish_date': 'invalid-date'
        }
        
        with self.assertRaises(ValidationError):
            validate_article(article)


class TestSanitizeFilename(unittest.TestCase):
    """Test cases for sanitize_filename function."""
    
    def test_basic_filename(self):
        """Test basic filename sanitization."""
        filename = "test file.txt"
        result = sanitize_filename(filename)
        self.assertEqual(result, "test file.txt")
    
    def test_filename_with_invalid_chars(self):
        """Test filename with invalid characters."""
        filename = 'test<>:"/\\|?*.txt'
        result = sanitize_filename(filename)
        self.assertEqual(result, "test.txt")
    
    def test_filename_with_spaces_and_dots(self):
        """Test filename with leading/trailing spaces and dots."""
        filename = "  .test file.  "
        result = sanitize_filename(filename)
        self.assertEqual(result, "test file")
    
    def test_long_filename(self):
        """Test filename that is too long."""
        filename = "a" * 300 + ".txt"
        result = sanitize_filename(filename)
        self.assertLessEqual(len(result), 255)
        self.assertTrue(result.endswith(".txt"))
    
    def test_empty_filename(self):
        """Test empty filename."""
        filename = ""
        result = sanitize_filename(filename)
        self.assertEqual(result, "")


class TestGenerateSlug(unittest.TestCase):
    """Test cases for generate_slug function."""
    
    def test_basic_slug(self):
        """Test basic slug generation."""
        title = "Hello World"
        result = generate_slug(title)
        self.assertEqual(result, "hello-world")
    
    def test_slug_with_special_chars(self):
        """Test slug generation with special characters."""
        title = "Hello, World! @#$%"
        result = generate_slug(title)
        self.assertEqual(result, "hello-world")
    
    def test_slug_with_multiple_spaces(self):
        """Test slug generation with multiple consecutive spaces."""
        title = "Hello    World"
        result = generate_slug(title)
        self.assertEqual(result, "hello-world")
    
    def test_slug_with_leading_trailing_spaces(self):
        """Test slug generation with leading/trailing spaces."""
        title = "  Hello World  "
        result = generate_slug(title)
        self.assertEqual(result, "hello-world")
    
    def test_slug_with_hyphens(self):
        """Test slug generation with existing hyphens."""
        title = "Hello-World-Test"
        result = generate_slug(title)
        self.assertEqual(result, "hello-world-test")
    
    def test_empty_title(self):
        """Test slug generation with empty title."""
        title = ""
        result = generate_slug(title)
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()