#!/usr/bin/env python3
"""
Main script to run the Real Estate Scraper
Provides a CLI interface for different scraping operations.
Now supports both Scrapy (recommended) and legacy Playwright approaches.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to path for Scrapy imports
sys.path.append(str(Path(__file__).parent))

# Legacy Playwright imports
from scraper import RealEstateScraper
from incremental_sync import IncrementalSyncer, PeriodicSyncer

# New Scrapy imports
from realestate_scraper.spiders.realestate_spider import RealEstateSpider


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Real Estate Scraper for realestate.com.au')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Full scrape command
    full_parser = subparsers.add_parser('full', help='Run full scrape of properties')
    full_parser.add_argument('--max-properties', type=int, default=100,
                           help='Maximum number of properties to scrape (default: 100)')
    full_parser.add_argument('--url', default='https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                           help='Base URL for property listings')
    full_parser.add_argument('--engine', choices=['scrapy', 'playwright'], default='scrapy',
                           help='Scraping engine to use (default: scrapy)')
    full_parser.add_argument('--proxy-server', help='Proxy server URL (e.g., http://proxy:8080)')
    full_parser.add_argument('--proxy-username', help='Proxy username')
    full_parser.add_argument('--proxy-password', help='Proxy password')
    full_parser.add_argument('--scraperapi-key', help='ScraperAPI key for proxy service')

    # Incremental sync command
    incremental_parser = subparsers.add_parser('sync', help='Run incremental sync')
    incremental_parser.add_argument('--max-properties', type=int, default=100,
                                  help='Maximum number of properties to check (default: 100)')
    incremental_parser.add_argument('--url', default='https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                                  help='Base URL for property listings')
    incremental_parser.add_argument('--engine', choices=['scrapy', 'playwright'], default='scrapy',
                                   help='Scraping engine to use (default: scrapy)')
    incremental_parser.add_argument('--proxy-server', help='Proxy server URL')
    incremental_parser.add_argument('--proxy-username', help='Proxy username')
    incremental_parser.add_argument('--proxy-password', help='Proxy password')
    incremental_parser.add_argument('--scraperapi-key', help='ScraperAPI key for proxy service')

    # Periodic sync command
    periodic_parser = subparsers.add_parser('periodic', help='Run periodic sync')
    periodic_parser.add_argument('--interval', type=int, default=24,
                               help='Sync interval in hours (default: 24)')
    periodic_parser.add_argument('--max-properties', type=int, default=100,
                               help='Maximum number of properties to check (default: 100)')
    periodic_parser.add_argument('--url', default='https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                               help='Base URL for property listings')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show scraper status')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # Prepare proxy configuration
    proxy_config = None
    if hasattr(args, 'proxy_server') and args.proxy_server:
        proxy_config = {
            'server': args.proxy_server,
            'username': args.proxy_username,
            'password': args.proxy_password
        }

    # Prepare ScraperAPI configuration
    scraperapi_key = getattr(args, 'scraperapi_key', None)
    engine = getattr(args, 'engine', 'scrapy')

    # Run the appropriate command
    if args.command == 'full':
        if engine == 'scrapy':
            run_scrapy_full_scrape(args.url, args.max_properties, proxy_config, scraperapi_key)
        else:
            asyncio.run(run_playwright_full_scrape(args.url, args.max_properties, proxy_config))
    elif args.command == 'sync':
        if engine == 'scrapy':
            # For sync, use incremental logic but with Scrapy for fresh data collection
            asyncio.run(run_scrapy_incremental_sync(args.url, args.max_properties, proxy_config, scraperapi_key))
        else:
            asyncio.run(run_incremental_sync(args.url, args.max_properties, proxy_config))
    elif args.command == 'periodic':
        asyncio.run(run_periodic_sync(args.url, args.max_properties, args.interval, proxy_config))
    elif args.command == 'status':
        show_status()


def run_scrapy_full_scrape(url: str, max_properties: int, proxy_config: dict = None, scraperapi_key: str = None):
    """Run full scrape using Scrapy engine"""
    print(f"Starting Scrapy full scrape for {max_properties} properties...")
    print(f"URL: {url}")
    print(f"Engine: Scrapy (recommended)")

    # Get Scrapy settings
    settings = get_project_settings()

    # Configure proxy settings
    if scraperapi_key:
        settings.update({
            'PROXY_ENABLED': True,
            'SCRAPERAPI_KEY': scraperapi_key,
        })
        print(f"Using ScraperAPI with key: {scraperapi_key[:10]}...")
    elif proxy_config and proxy_config.get('server'):
        settings.update({
            'PROXY_ENABLED': True,
            'PROXY_SERVER': proxy_config['server'],
            'PROXY_USERNAME': proxy_config.get('username'),
            'PROXY_PASSWORD': proxy_config.get('password'),
        })
        print(f"Using proxy: {proxy_config['server']}")
    else:
        print("Running without proxy")

    # Create crawler process
    process = CrawlerProcess(settings)
    process.crawl(RealEstateSpider, url=url, max_properties=max_properties)
    process.start()

    print("\nScrapy full scrape completed!")
    show_status()


async def run_playwright_full_scrape(url: str, max_properties: int, proxy_config: dict = None):
    """Run full scrape using legacy Playwright engine"""
    print(f"Starting Playwright full scrape for {max_properties} properties...")
    print(f"URL: {url}")
    print(f"Engine: Playwright (legacy)")
    if proxy_config and proxy_config.get('server'):
        print(f"Using proxy: {proxy_config['server']}")

    scraper = RealEstateScraper(max_properties=max_properties, proxy_config=proxy_config)
    await scraper.run_full_scrape(url)

    print("\nPlaywright full scrape completed!")
    show_status()


async def run_scrapy_incremental_sync(url: str, max_properties: int, proxy_config: dict = None, scraperapi_key: str = None):
    """Run incremental sync using Scrapy for data collection"""
    print(f"Starting Scrapy incremental sync for up to {max_properties} properties...")
    print(f"URL: {url}")
    print(f"Engine: Scrapy (recommended)")

    # First, run a limited Scrapy crawl to get current listings
    print("Step 1: Collecting current property listings with Scrapy...")

    settings = get_project_settings()

    # Configure proxy settings
    if scraperapi_key:
        settings.update({
            'PROXY_ENABLED': True,
            'SCRAPERAPI_KEY': scraperapi_key,
        })
        print(f"Using ScraperAPI with key: {scraperapi_key[:10]}...")
    elif proxy_config and proxy_config.get('server'):
        settings.update({
            'PROXY_ENABLED': True,
            'PROXY_SERVER': proxy_config['server'],
            'PROXY_USERNAME': proxy_config.get('username'),
            'PROXY_PASSWORD': proxy_config.get('password'),
        })
        print(f"Using proxy: {proxy_config['server']}")

    # Run Scrapy crawl
    process = CrawlerProcess(settings)
    process.crawl(RealEstateSpider, url=url, max_properties=max_properties)
    process.start()

    # Then run incremental comparison
    print("Step 2: Analyzing changes...")
    syncer = IncrementalSyncer()
    await syncer.analyze_changes()

    print("\nScrapy incremental sync completed!")
    show_status()


async def run_incremental_sync(url: str, max_properties: int, proxy_config: dict = None):
    """Run incremental sync using legacy Playwright engine"""
    print(f"Starting Playwright incremental sync for up to {max_properties} properties...")
    print(f"URL: {url}")
    print(f"Engine: Playwright (legacy)")
    if proxy_config and proxy_config.get('server'):
        print(f"Using proxy: {proxy_config['server']}")

    syncer = IncrementalSyncer(proxy_config=proxy_config)
    await syncer.run_incremental_sync(url, max_properties)

    print("\nPlaywright incremental sync completed!")
    show_status()


async def run_periodic_sync(url: str, max_properties: int, interval_hours: int):
    """Run periodic sync"""
    print(f"Starting periodic sync (every {interval_hours} hours)...")
    print(f"URL: {url}")
    print(f"Max properties per sync: {max_properties}")
    print("Press Ctrl+C to stop")

    periodic_syncer = PeriodicSyncer(sync_interval_hours=interval_hours)
    await periodic_syncer.run_periodic_sync(url, max_properties)


def show_status():
    """Show current scraper status"""
    data_dir = Path("data")
    properties_dir = data_dir / "properties"
    logs_dir = data_dir / "logs"
    images_dir = data_dir / "images"

    print("\n" + "="*50)
    print("SCRAPER STATUS")
    print("="*50)

    # Count properties
    property_files = list(properties_dir.glob("*.json")) if properties_dir.exists() else []
    print(f"Total properties scraped: {len(property_files)}")

    # Count images
    if images_dir.exists():
        image_dirs = [d for d in images_dir.iterdir() if d.is_dir()]
        total_images = sum(len(list(d.glob("*.jpg"))) + len(list(d.glob("*.png"))) for d in image_dirs)
        print(f"Total images downloaded: {total_images}")
    else:
        print("Total images downloaded: 0")

    # Show recent activity
    last_sync_file = logs_dir / "last_sync.json"
    if last_sync_file.exists():
        try:
            import json
            with open(last_sync_file, 'r') as f:
                last_sync = json.load(f)
            print(f"Last sync: {last_sync.get('timestamp', 'Unknown')}")
            print(f"Failed properties: {last_sync.get('failed_count', 0)}")
        except:
            print("Last sync: Unable to read sync data")
    else:
        print("Last sync: Never")

    # Show incremental sync status
    incremental_sync_file = logs_dir / "last_incremental_sync.json"
    if incremental_sync_file.exists():
        try:
            import json
            with open(incremental_sync_file, 'r') as f:
                incremental_sync = json.load(f)
            changes = incremental_sync.get('changes', {})
            print(f"Last incremental sync: {incremental_sync.get('timestamp', 'Unknown')}")
            print(f"  - New properties: {len(changes.get('new', []))}")
            print(f"  - Changed properties: {len(changes.get('changed', []))}")
            print(f"  - Removed properties: {len(changes.get('removed', []))}")
        except:
            print("Last incremental sync: Unable to read sync data")

    print("="*50)


if __name__ == "__main__":
    main()