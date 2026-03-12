# Publisher

A multi-platform article publishing tool that allows you to publish articles across X (Twitter), Reddit, Medium, Substack, and LinkedIn from a single interface.

## Features

- **Multi-Platform Publishing**: Publish articles to multiple platforms simultaneously
- **Template Support**: Use markdown templates for consistent formatting
- **API Integration**: Connect to platform APIs with secure configuration
- **Batch Publishing**: Publish to multiple platforms with a single command
- **Content Management**: Manage and track published articles

## Supported Platforms

- **X (Twitter)**: Publish articles and threads
- **Reddit**: Post to subreddits with proper formatting
- **Medium**: Publish articles with metadata
- **Substack**: Create and publish newsletters
- **LinkedIn**: Share articles on professional network

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   # or
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with your API credentials:

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
from publisher import Publisher

# Initialize publisher
publisher = Publisher()

# Create article
article = {
    "title": "Your Article Title",
    "content": "Your article content in markdown",
    "tags": ["technology", "programming"],
    "publish_date": "2024-01-01"
}

# Publish to all platforms
publisher.publish_to_all(article)

# Publish to specific platforms
publisher.publish_to_x(article)
publisher.publish_to_reddit(article, subreddit="programming")
publisher.publish_to_medium(article)
publisher.publish_to_substack(article)
publisher.publish_to_linkedin(article)
```

### Using Templates

```python
# Use markdown templates
template = """
# {title}

{content}

Tags: {tags}
"""

article = {
    "title": "Your Article Title",
    "content": "Your article content",
    "tags": ["technology", "programming"]
}

publisher.publish_with_template(article, template)
```

## API Documentation

### X (Twitter)

Publish articles and threads to X.

**Configuration Required:**
- X_API_KEY
- X_API_SECRET
- X_ACCESS_TOKEN
- X_ACCESS_SECRET

**Usage:**
```python
publisher.publish_to_x(article)
```

### Reddit

Post articles to specific subreddits with proper formatting.

**Configuration Required:**
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- REDDIT_USERNAME
- REDDIT_PASSWORD

**Usage:**
```python
publisher.publish_to_reddit(article, subreddit="programming")
```

### Medium

Publish articles with metadata and tags.

**Configuration Required:**
- MEDIUM_API_TOKEN
- MEDIUM_USER_ID

**Usage:**
```python
publisher.publish_to_medium(article)
```

### Substack

Create and publish newsletters.

**Configuration Required:**
- SUBSTACK_EMAIL
- SUBSTACK_PASSWORD
- SUBSTACK_DOMAIN

**Usage:**
```python
publisher.publish_to_substack(article)
```

### LinkedIn

Share articles on professional network.

**Configuration Required:**
- LINKEDIN_ACCESS_TOKEN
- LINKEDIN_PROFILE_URN

**Usage:**
```python
publisher.publish_to_linkedin(article)
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
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation for each platform

## Disclaimer

This tool is for educational and personal use. Users are responsible for:
- Complying with platform terms of service
- Respecting content ownership and copyright
- Following platform-specific posting guidelines
- Managing API rate limits appropriately