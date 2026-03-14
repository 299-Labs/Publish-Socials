# Publish-Socials

[![PyPI version](https://badge.fury.io/py/publish-socials.svg)](https://badge.fury.io/py/publish-socials)
[![Python Version](https://img.shields.io/pypi/pyversions/publish-socials.svg)](https://pypi.org/project/publish-socials/)
[![License](https://img.shields.io/pypi/l/publish-socials.svg)](https://pypi.org/project/publish-socials/)
[![Downloads](https://img.shields.io/pypi/dm/publish-socials.svg)](https://pypistats.org/packages/publish-socials)
[![CI/CD](https://github.com/299-Labs/Publish-Socials/actions/workflows/ci.yml/badge.svg)](https://github.com/299-Labs/Publish-Socials/actions)
[![Code Coverage](https://codecov.io/gh/299-Labs/Publish-Socials/branch/main/graph/badge.svg)](https://codecov.io/gh/299-Labs/Publish-Socials)

A multi-platform social media publishing tool that allows you to publish content across X (Twitter), Reddit, Medium, Substack, and LinkedIn from a single interface.

## Features

- **Multi-Platform Publishing**: Publish content to multiple platforms simultaneously
- **Template Support**: Use markdown templates for consistent formatting
- **API Integration**: Connect to platform APIs with secure configuration
- **Batch Publishing**: Publish to multiple platforms with a single command
- **Content Management**: Manage and track published content
- **Smart Formatting**: Automatically adapt content for each platform's requirements

## Supported Platforms

- **X (Twitter)**: Publish tweets and threads
- **Reddit**: Post to subreddits with proper formatting
- **Medium**: Publish articles with metadata
- **Substack**: Create and publish newsletters
- **LinkedIn**: Share posts on professional network

## Installation

### PyPI Installation (Recommended)
```bash
pip install Publish-Socials
```

### Development Installation
```bash
# Clone the repository
git clone https://github.com/299-Labs/Publish-Socials.git
cd Publish-Socials

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

### Publishing to PyPI

This project uses OpenID Connect (OIDC) for secure, credential-free publishing to PyPI. No API tokens are required!

**For Maintainers:**
- Releases are automatically published to PyPI when you create a GitHub release
- The workflow uses GitHub's OIDC integration with PyPI
- No manual intervention or API credentials needed

**To create a release:**
1. Update the version in `pyproject.toml`
2. Create and push a git tag: `git tag v1.0.1 && git push origin v1.0.1`
3. Create a GitHub release for the tag
4. PyPI package is automatically published via GitHub Actions

## Configuration

Create a `.env` file in your project directory with your API credentials:

```env
# X (Twitter) API
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_ACCESS_TOKEN=your_x_access_token
X_ACCESS_SECRET=your_x_access_secret

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Medium API
MEDIUM_API_TOKEN=your_medium_api_token
MEDIUM_USER_ID=your_medium_user_id

# Substack API
SUBSTACK_EMAIL=your_substack_email
SUBSTACK_PASSWORD=your_substack_password
SUBSTACK_DOMAIN=your_substack_domain

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PROFILE_URN=your_linkedin_profile_urn
```

## Usage

### Basic Publishing

```python
from publish_socials import Publisher

# Initialize publisher
publisher = Publisher()

# Create content
content = {
    "title": "Your Post Title",
    "content": "Your content in markdown",
    "tags": ["technology", "programming"],
    "publish_date": "2024-01-01"
}

# Publish to all platforms
publisher.publish_to_all(content)

# Publish to specific platforms
publisher.publish_to_x(content)
publisher.publish_to_reddit(content, subreddit="programming")
publisher.publish_to_medium(content)
publisher.publish_to_substack(content)
publisher.publish_to_linkedin(content)
```

### Using Templates

```python
# Use markdown templates
template = """
# {title}

{content}

Tags: {tags}
"""

content = {
    "title": "Your Post Title",
    "content": "Your content",
    "tags": ["technology", "programming"]
}

publisher.publish_with_template(content, template)
```

## API Documentation

### X (Twitter)

Publish tweets and threads to X.

**Configuration Required:**
- X_API_KEY
- X_API_SECRET
- X_ACCESS_TOKEN
- X_ACCESS_SECRET

**Usage:**
```python
publisher.publish_to_x(content)
```

### Reddit

Post content to specific subreddits with proper formatting.

**Configuration Required:**
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- REDDIT_USERNAME
- REDDIT_PASSWORD

**Usage:**
```python
publisher.publish_to_reddit(content, subreddit="programming")
```

### Medium

Publish articles with metadata and tags.

**Configuration Required:**
- MEDIUM_API_TOKEN
- MEDIUM_USER_ID

**Usage:**
```python
publisher.publish_to_medium(content)
```

### Substack

Create and publish newsletters.

**Configuration Required:**
- SUBSTACK_EMAIL
- SUBSTACK_PASSWORD
- SUBSTACK_DOMAIN

**Usage:**
```python
publisher.publish_to_substack(content)
```

### LinkedIn

Share posts on professional network.

**Configuration Required:**
- LINKEDIN_ACCESS_TOKEN
- LINKEDIN_PROFILE_URN

**Usage:**
```python
publisher.publish_to_linkedin(content)
```

## Error Handling

The publisher includes comprehensive error handling for:
- API authentication failures
- Rate limiting
- Network connectivity issues
- Invalid content formatting
- Platform-specific restrictions

## Development

### Adding New Platforms

To add support for a new platform:

1. Create a new method in the `Publisher` class
2. Add required configuration variables to the `.env` template
3. Implement error handling for platform-specific issues
4. Add tests for the new platform

### Testing

Run tests to ensure all platforms work correctly:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=publish_socials --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation for each platform
- Join our discussions

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Disclaimer

This tool is for educational and personal use. Users are responsible for:
- Complying with platform terms of service
- Respecting content ownership and copyright
- Following platform-specific posting guidelines
- Managing API rate limits appropriately
- Ensuring content quality and appropriateness

## Version History

- **1.0.0** - Initial release with support for X, Reddit, Medium, Substack, and LinkedIn

## Changelog

See [GitHub Releases](https://github.com/299-Labs/Publish-Socials/releases) for detailed changelog.
