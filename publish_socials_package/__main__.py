#!/usr/bin/env python3
"""
Command-line interface for Publish-Socials.

This module provides the main entry point for the publish-socials command.
"""

import argparse
import sys
from .publish_socials import Publisher
from .config import Config


def main():
    """Main entry point for the publish-socials command."""
    parser = argparse.ArgumentParser(
        description="Publish content to multiple social media platforms"
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to configuration file (default: .env)",
        default=".env",
    )
    parser.add_argument(
        "--platform",
        "-p",
        help="Specific platform to publish to (x, reddit, medium, substack, linkedin)",
        choices=["x", "reddit", "medium", "substack", "linkedin"],
    )
    parser.add_argument("--title", "-t", help="Title of the content")
    parser.add_argument(
        "--content", "-C", help="Content to publish (supports markdown)"
    )
    parser.add_argument("--tags", "-g", help="Comma-separated tags")
    parser.add_argument("--subreddit", "-s", help="Subreddit for Reddit posts")
    parser.add_argument(
        "--test", "-T", action="store_true", help="Test connections to all platforms"
    )
    parser.add_argument("--template", help="Path to markdown template file")

    args = parser.parse_args()

    try:
        # Initialize configuration
        config = Config(args.config)
        config.load()

        # Initialize publisher
        publisher = Publisher(config)

        if args.test:
            # Test all connections
            print("Testing connections to all platforms...")
            results = publisher.test_all_connections()
            for platform, status in results.items():
                status_text = "✓" if status else "✗"
                print(
                    f"{status_text} {platform}: {'Connected' if status else 'Failed'}"
                )
            return

        # Validate required arguments
        if not args.title and not args.content:
            print("Error: Either --title or --content is required")
            sys.exit(1)

        # Prepare content
        content = {
            "title": args.title or "",
            "content": args.content or "",
            "tags": args.tags.split(",") if args.tags else [],
            "publish_date": None,
        }

        if args.platform:
            # Publish to specific platform
            if args.platform == "reddit" and args.subreddit:
                publisher.publish_to_reddit(content, args.subreddit)
            else:
                publish_method = getattr(publisher, f"publish_to_{args.platform}")
                publish_method(content)
            print(f"Successfully published to {args.platform}")
        else:
            # Publish to all platforms
            if args.template:
                with open(args.template, "r") as f:
                    template = f.read()
                publisher.publish_with_template(content, template)
            else:
                publisher.publish_to_all(content)
            print("Successfully published to all platforms")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
