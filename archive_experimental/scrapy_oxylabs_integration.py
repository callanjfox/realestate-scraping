#!/usr/bin/env python3
"""
Scrapy integration with working Oxylabs proxy
"""

import sys
import os
from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from realestate_scraper.spiders.realestate_spider import RealEstateScraper


def run_scrapy_with_oxylabs(max_properties=10):
    """Run Scrapy with working Oxylabs proxy to scrape realestate.com.au"""

    print(f"🚀 SCRAPING REALESTATE.COM.AU WITH OXYLABS PROXY!")
    print(f"Target: {max_properties} properties")
    print(f"URL: https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1")

    # Working Oxylabs configuration
    username = 'randomspam_yJWgW'
    password = '_27LsLX+2g2yK76'
    working_proxy_url = f'http://{username}:{password}@dc.oxylabs.io:8001'

    print(f"Proxy: {username}:***@dc.oxylabs.io:8001")

    # Get project settings
    settings = get_project_settings()

    # Configure Scrapy for optimal performance with Oxylabs
    settings.update({
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 1,  # Conservative for proxy
        'DOWNLOAD_DELAY': 2,  # 2 second delays
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_TIMEOUT': 60,  # Longer timeout for proxy
        'RETRY_TIMES': 3,  # More retries with proxy

        # Proxy configuration
        'PROXY_ENABLED': True,
        'PROXY_SERVER': working_proxy_url,

        # Enhanced anti-detection settings
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': True,

        # User agent rotation
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'realestate_scraper.middlewares.ProxyMiddleware': 500,
            'realestate_scraper.middlewares.HeadersMiddleware': 600,
        },

        # Request headers
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-AU,en;q=0.9,en-US;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
    })

    print(f"\n{'='*60}")
    print("STARTING SCRAPY WITH OXYLABS PROXY")
    print(f"{'='*60}")

    try:
        # Create crawler process
        process = CrawlerProcess(settings)
        process.crawl(
            RealEstateScraper,
            url='https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
            max_properties=max_properties
        )
        process.start()

        print(f"\n🎉 SCRAPY OXYLABS INTEGRATION COMPLETED!")

        # Show results
        print(f"\n{'='*60}")
        print("RESULTS")
        print(f"{'='*60}")

        from main import show_status
        show_status()

        # Count scraped files
        data_dir = Path("data/properties")
        if data_dir.exists():
            property_files = list(data_dir.glob("*.json"))
            total_properties = len(property_files)

            print(f"\n📊 FINAL SUMMARY:")
            print(f"✅ Total properties scraped: {total_properties}")

            if total_properties >= max_properties:
                print(f"🎯 SUCCESS! Reached target of {max_properties} properties")
            elif total_properties > 0:
                print(f"⚠️ Partial success: {total_properties}/{max_properties} properties scraped")
                print("   (Some properties may have been blocked or failed)")
            else:
                print(f"❌ No properties scraped - proxy may still be getting 429s")

            # Show sample properties
            if total_properties > 0:
                print(f"\n📋 Sample scraped properties:")
                for i, prop_file in enumerate(property_files[:3]):
                    print(f"  {i+1}. {prop_file.stem}")

        return total_properties > 0

    except Exception as e:
        print(f"❌ Scrapy execution failed: {e}")
        return False


if __name__ == '__main__':
    print("🚀 OXYLABS + SCRAPY INTEGRATION TEST")
    print("="*60)

    success = run_scrapy_with_oxylabs(max_properties=10)

    if success:
        print(f"\n✅ MISSION ACCOMPLISHED!")
        print("Oxylabs proxy + Scrapy successfully scraping realestate.com.au")
    else:
        print(f"\n⚠️ NEEDS OPTIMIZATION")
        print("Proxy connection works but may need fine-tuning for consistent scraping")

    print(f"\n📋 REPORT COMPLETE")