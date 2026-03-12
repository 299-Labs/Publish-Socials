#!/usr/bin/env python3
"""
Example usage of the Publisher application.

This script demonstrates how to use the Publisher to publish articles
across multiple platforms: X (Twitter), Reddit, Medium, Substack, and LinkedIn.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from publisher import Publisher
from config import Config


def create_sample_article():
    """Create a sample article for demonstration."""
    return {
        "title": "My First Multi-Platform Article",
        "content": """
# The Future of Content Publishing

In today's digital age, content creators face the challenge of reaching audiences across multiple platforms. Each platform has its own unique audience, formatting requirements, and engagement patterns.

## Why Multi-Platform Publishing Matters

- **Broader Reach**: Different platforms attract different demographics
- **Content Repurposing**: One piece of content can be adapted for multiple formats
- **Audience Engagement**: Meet your audience where they already are
- **Brand Consistency**: Maintain a consistent voice across platforms

## Best Practices

1. **Adapt Content**: Don't just copy-paste - adapt for each platform
2. **Timing**: Post when your audience is most active on each platform
3. **Engagement**: Respond to comments and interactions
4. **Analytics**: Track performance to optimize future posts

---

*This article was published using the Publisher tool to demonstrate multi-platform content distribution.*
        """,
        "tags": ["content-creation", "digital-marketing", "social-media", "publishing"],
        "publish_date": datetime.now().isoformat(),
        "author": "Your Name",
        "summary": "Exploring the importance of multi-platform content publishing in the digital age.",
        "excerpt": "Learn why content creators should embrace multi-platform publishing to reach broader audiences and maximize engagement."
    }


def create_template():
    """Create a template for formatting articles."""
    return """
# {title}

{content}

**Tags**: {tags}

*Published on {publish_date}*

---

*This article was published using the Publisher tool.*
"""


def main():
    """Main function to demonstrate Publisher usage."""
    print("🚀 Publisher Example Usage")
    print("=" * 50)
    
    # Initialize publisher
    print("1. Initializing Publisher...")
    try:
        publisher = Publisher()
        print("✓ Publisher initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Publisher: {e}")
        return
    
    # Test platform connections
    print("\n2. Testing platform connections...")
    try:
        connection_results = publisher.test_all_connections()
        
        for platform, result in connection_results.items():
            if result['success']:
                print(f"✓ {platform.capitalize()}: Connected")
            else:
                print(f"✗ {platform.capitalize()}: {result['error']}")
    except Exception as e:
        print(f"✗ Failed to test connections: {e}")
    
    # Create sample article
    print("\n3. Creating sample article...")
    article = create_sample_article()
    print(f"✓ Article created: '{article['title']}'")
    
    # Publish to all platforms
    print("\n4. Publishing to all platforms...")
    try:
        results = publisher.publish_to_all(article)
        
        print("\n📊 Publishing Results:")
        print("-" * 30)
        
        for platform, result in results.items():
            if result['success']:
                print(f"✓ {platform.capitalize()}: Published successfully")
                print(f"  URL: {result['result'].get('url', 'N/A')}")
            else:
                print(f"✗ {platform.capitalize()}: {result['error']}")
            print()
            
    except Exception as e:
        print(f"✗ Failed to publish: {e}")
    
    # Example: Publish with template
    print("5. Publishing with template...")
    try:
        template = create_template()
        template_results = publisher.publish_with_template(
            article, 
            template, 
            platforms=['x', 'medium']  # Only publish to X and Medium with template
        )
        
        print("\n📊 Template Publishing Results:")
        print("-" * 35)
        
        for platform, result in template_results.items():
            if result['success']:
                print(f"✓ {platform.capitalize()}: Published with template")
            else:
                print(f"✗ {platform.capitalize()}: {result['error']}")
                
    except Exception as e:
        print(f"✗ Failed to publish with template: {e}")
    
    # Example: Publish to specific platforms
    print("\n6. Publishing to specific platforms...")
    try:
        # Publish only to Reddit
        reddit_result = publisher.publish_to_reddit(
            article, 
            subreddit="test"  # Replace with actual subreddit
        )
        print(f"✓ Reddit: Published to r/test")
        print(f"  URL: {reddit_result.get('url', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Reddit publishing failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Example usage completed!")
    print("\n💡 Next Steps:")
    print("1. Create a .env file with your API credentials")
    print("2. Configure the platforms you want to use")
    print("3. Customize the article content and templates")
    print("4. Run this script again to see actual publishing")


def setup_environment():
    """Set up the environment for the example."""
    print("🔧 Environment Setup")
    print("=" * 30)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating template...")
        
        # Create environment template
        Config.create_env_template('.env.example')
        print("✓ Created .env.example file")
        print("📝 Please copy .env.example to .env and fill in your API credentials")
        
        # Create a basic .env file with placeholders
        with open('.env', 'w') as f:
            f.write("# Example .env file\n")
            f.write("# Copy this to .env and fill in your actual credentials\n\n")
            f.write("# X (Twitter) API\n")
            f.write("X_API_KEY=your_x_api_key\n")
            f.write("X_API_SECRET=your_x_api_secret\n")
            f.write("X_ACCESS_TOKEN=your_x_access_token\n")
            f.write("X_ACCESS_SECRET=your_x_access_secret\n")
            f.write("X_BEARER_TOKEN=your_x_bearer_token\n\n")
            f.write("# Reddit API\n")
            f.write("REDDIT_CLIENT_ID=your_reddit_client_id\n")
            f.write("REDDIT_CLIENT_SECRET=your_reddit_client_secret\n")
            f.write("REDDIT_USER_AGENT=your_reddit_user_agent\n")
            f.write("REDDIT_USERNAME=your_reddit_username\n")
            f.write("REDDIT_PASSWORD=your_reddit_password\n\n")
            f.write("# Medium API\n")
            f.write("MEDIUM_API_TOKEN=your_medium_api_token\n")
            f.write("MEDIUM_USER_ID=your_medium_user_id\n\n")
            f.write("# Substack Configuration\n")
            f.write("SUBSTACK_EMAIL=your_substack_email\n")
            f.write("SUBSTACK_PASSWORD=your_substack_password\n")
            f.write("SUBSTACK_DOMAIN=your_substack_domain\n\n")
            f.write("# LinkedIn API\n")
            f.write("LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token\n")
            f.write("LINKEDIN_PROFILE_URN=your_linkedin_profile_urn\n")
            f.write("LINKEDIN_CLIENT_ID=your_linkedin_client_id\n")
            f.write("LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret\n")
        
        print("✓ Created basic .env file with placeholders")
    else:
        print("✓ .env file already exists")
    
    print("\n📋 Required Dependencies:")
    print("- requests>=2.31.0")
    print("- python-dotenv>=1.0.0")
    print("- markdown>=3.5.0")
    print("\n💡 Install with: pip install -r requirements.txt")


if __name__ == "__main__":
    # Setup environment first
    setup_environment()
    
    print("\n" + "=" * 60)
    
    # Run main example
    main()