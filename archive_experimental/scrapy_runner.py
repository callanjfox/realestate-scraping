#!/usr/bin/env python3
"""
Scrapy runner for testing the real estate spider
"""

import sys
import os
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from realestate_scraper.spiders.realestate_spider import RealEstateSpider


def run_spider(max_properties=10, url=None, use_proxy=False, scraperapi_key=None, proxy_server=None, proxy_username=None, proxy_password=None):
    """Run the real estate spider with specified parameters"""

    # Get project settings
    settings = get_project_settings()

    # Override settings for this run
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    # Configure proxy if requested
    if use_proxy and scraperapi_key:
        custom_settings.update({
            'PROXY_ENABLED': True,
            'SCRAPERAPI_KEY': scraperapi_key,
        })
        print(f"Using ScraperAPI with key: {scraperapi_key[:10]}...")
    elif use_proxy and proxy_server:
        custom_settings.update({
            'PROXY_ENABLED': True,
            'PROXY_SERVER': proxy_server,
            'PROXY_USERNAME': proxy_username,
            'PROXY_PASSWORD': proxy_password,
        })
        print(f"Using proxy server: {proxy_server}")
    else:
        print("Running without proxy")

    # Update settings
    settings.update(custom_settings)

    # Default URL
    if not url:
        url = 'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'

    print(f"Starting Scrapy spider...")
    print(f"URL: {url}")
    print(f"Max properties: {max_properties}")
    print(f"Proxy enabled: {use_proxy}")

    # Create and start crawler process
    process = CrawlerProcess(settings)

    # Add spider with arguments
    process.crawl(RealEstateSpider,
                  url=url,
                  max_properties=max_properties)

    # Start the reactor
    process.start()


def main():
    """Main function with command line arguments"""
    import argparse

    parser = argparse.ArgumentParser(description='Test Scrapy Real Estate Spider')
    parser.add_argument('--max-properties', type=int, default=10,
                       help='Maximum properties to scrape (default: 10)')
    parser.add_argument('--url',
                       default='https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                       help='Base URL for scraping')
    parser.add_argument('--proxy', action='store_true',
                       help='Enable proxy usage')
    parser.add_argument('--scraperapi-key',
                       help='ScraperAPI key')
    parser.add_argument('--proxy-server',
                       help='Proxy server URL')
    parser.add_argument('--proxy-username',
                       help='Proxy username')
    parser.add_argument('--proxy-password',
                       help='Proxy password')

    args = parser.parse_args()

    # Run spider
    run_spider(
        max_properties=args.max_properties,
        url=args.url,
        use_proxy=args.proxy,
        scraperapi_key=args.scraperapi_key,
        proxy_server=args.proxy_server,
        proxy_username=args.proxy_username,
        proxy_password=args.proxy_password
    )


if __name__ == '__main__':
    main()