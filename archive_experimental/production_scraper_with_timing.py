#!/usr/bin/env python3
"""
Production scraper with timing for 100 properties
Uses multiple strategies and fallbacks for maximum success
"""

import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime, timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from realestate_scraper.spiders.realestate_spider import RealEstateScraper
from realestate_scraper.spiders.rightmove_spider import RightMoveSpider


class ProductionScrapingOrchestrator:
    """Orchestrates multiple scraping strategies for maximum success"""

    def __init__(self, target_properties=100):
        self.target_properties = target_properties
        self.start_time = None
        self.results = {
            'total_scraped': 0,
            'total_time': 0,
            'strategies_used': [],
            'properties_per_strategy': {},
            'average_time_per_property': 0
        }

        # Premium Oxylabs credentials
        self.oxylabs_username = 'randomspam_ccS0C'
        self.oxylabs_password = '67Sff+zvRQQk49z'

    def start_timing(self):
        """Start performance timing"""
        self.start_time = time.time()
        print(f"⏱️ Starting timer at {datetime.now().strftime('%H:%M:%S')}")

    def stop_timing(self):
        """Stop timing and calculate metrics"""
        if self.start_time:
            self.results['total_time'] = time.time() - self.start_time
            if self.results['total_scraped'] > 0:
                self.results['average_time_per_property'] = self.results['total_time'] / self.results['total_scraped']

    def count_current_properties(self):
        """Count currently scraped properties"""
        data_dir = Path("data/properties")
        if not data_dir.exists():
            return 0

        property_files = list(data_dir.glob("*.json"))
        return len(property_files)

    def test_oxylabs_strategy(self, strategy_name, proxy_config, target_site='realestate'):
        """Test specific Oxylabs strategy"""

        print(f"\n{'='*60}")
        print(f"STRATEGY: {strategy_name}")
        print(f"{'='*60}")

        # Configure target URL
        if target_site == 'realestate':
            target_url = 'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'
            spider_class = RealEstateScraper
        else:  # rightmove fallback
            target_url = 'https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E87490'
            spider_class = RightMoveSpider

        print(f"Target: {target_url}")
        print(f"Proxy: {proxy_config['url'].replace(self.oxylabs_password, '***')}")

        # Get initial count
        initial_count = self.count_current_properties()
        print(f"Starting property count: {initial_count}")

        try:
            # Configure Scrapy settings
            settings = get_project_settings()
            settings.update({
                'LOG_LEVEL': 'INFO',
                'CONCURRENT_REQUESTS': 1,
                'DOWNLOAD_DELAY': 3,
                'RANDOMIZE_DOWNLOAD_DELAY': True,
                'DOWNLOAD_TIMEOUT': 60,
                'RETRY_TIMES': 2,

                # Proxy settings
                'PROXY_ENABLED': True,
                'PROXY_SERVER': proxy_config['url'],

                # Enhanced settings for protected sites
                'ROBOTSTXT_OBEY': False,
                'COOKIES_ENABLED': True,
                'HTTPCACHE_ENABLED': False,

                # Conservative concurrent settings
                'AUTOTHROTTLE_ENABLED': True,
                'AUTOTHROTTLE_START_DELAY': 3,
                'AUTOTHROTTLE_MAX_DELAY': 15,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.3,  # Very conservative

                # Enhanced headers
                'DEFAULT_REQUEST_HEADERS': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-AU,en;q=0.9,en-US;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
            })

            print(f"Starting Scrapy with {strategy_name}...")

            # Run scraper
            process = CrawlerProcess(settings)
            process.crawl(
                spider_class,
                url=target_url,
                max_properties=min(20, self.target_properties)  # Start with smaller batch
            )
            process.start()

            # Check results
            final_count = self.count_current_properties()
            scraped_this_round = final_count - initial_count

            print(f"✅ Strategy complete!")
            print(f"Properties scraped this round: {scraped_this_round}")

            if scraped_this_round > 0:
                self.results['strategies_used'].append(strategy_name)
                self.results['properties_per_strategy'][strategy_name] = scraped_this_round
                self.results['total_scraped'] = final_count

                return True

            return False

        except Exception as e:
            print(f"❌ Strategy failed: {e}")
            return False

    def execute_production_scrape(self):
        """Execute full production scrape with multiple strategies"""

        print(f"🚀 PRODUCTION SCRAPE: {self.target_properties} PROPERTIES")
        print(f"Oxylabs Premium Account: {self.oxylabs_username}")
        print("="*70)

        self.start_timing()

        # Strategy 1: Premium Australian Residential
        strategy_configs = [
            {
                'name': 'Australian Residential Premium',
                'url': f'http://customer-{self.oxylabs_username}-country-AU:{self.oxylabs_password}@pr.oxylabs.io:7777',
                'site': 'realestate'
            },
            {
                'name': 'US Residential Fallback',
                'url': f'http://customer-{self.oxylabs_username}-country-US:{self.oxylabs_password}@pr.oxylabs.io:7777',
                'site': 'realestate'
            },
            {
                'name': 'Basic Premium Format',
                'url': f'http://{self.oxylabs_username}:{self.oxylabs_password}@pr.oxylabs.io:7777',
                'site': 'realestate'
            },
            {
                'name': 'RightMove Backup (No Proxy)',
                'url': None,
                'site': 'rightmove'
            }
        ]

        for strategy_config in strategy_configs:
            if self.results['total_scraped'] >= self.target_properties:
                print(f"🎯 Target reached! {self.results['total_scraped']} properties")
                break

            success = self.test_oxylabs_strategy(
                strategy_config['name'],
                {'url': strategy_config['url']} if strategy_config['url'] else {'url': None},
                strategy_config['site']
            )

            if success:
                print(f"✅ {strategy_config['name']} successful!")

                # Continue with this strategy if it's working
                if self.results['total_scraped'] < self.target_properties:
                    remaining = self.target_properties - self.results['total_scraped']
                    print(f"🔄 Continuing strategy for {remaining} more properties...")

                    # Run additional batches with same strategy
                    self.test_oxylabs_strategy(
                        f"{strategy_config['name']} (Batch 2)",
                        {'url': strategy_config['url']} if strategy_config['url'] else {'url': None},
                        strategy_config['site']
                    )

            else:
                print(f"❌ {strategy_config['name']} failed, trying next...")

            # Wait between strategies
            time.sleep(10)

        self.stop_timing()
        self.print_final_results()

    def print_final_results(self):
        """Print comprehensive timing and performance results"""

        print(f"\n{'='*70}")
        print("🏁 PRODUCTION SCRAPE RESULTS")
        print(f"{'='*70}")

        print(f"📊 PERFORMANCE METRICS:")
        print(f"  Total properties scraped: {self.results['total_scraped']}")
        print(f"  Target properties: {self.target_properties}")
        print(f"  Success rate: {(self.results['total_scraped']/self.target_properties*100):.1f}%")
        print(f"  Total time: {self.results['total_time']:.1f} seconds ({self.results['total_time']/60:.1f} minutes)")
        print(f"  Average time per property: {self.results['average_time_per_property']:.2f} seconds")

        if self.results['total_scraped'] > 0:
            estimated_time_100 = (self.results['average_time_per_property'] * 100) / 60
            print(f"  📈 Estimated time for 100 properties: {estimated_time_100:.1f} minutes")

            properties_per_hour = 3600 / self.results['average_time_per_property']
            print(f"  📈 Estimated properties per hour: {properties_per_hour:.0f}")

        print(f"\n📋 STRATEGIES USED:")
        for strategy in self.results['strategies_used']:
            count = self.results['properties_per_strategy'].get(strategy, 0)
            print(f"  ✅ {strategy}: {count} properties")

        # Show sample scraped files
        data_dir = Path("data/properties")
        if data_dir.exists():
            recent_files = sorted(data_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            print(f"\n📁 RECENT SCRAPED PROPERTIES:")
            for i, prop_file in enumerate(recent_files[:5]):
                print(f"  {i+1}. {prop_file.stem}")

        if self.results['total_scraped'] >= self.target_properties:
            print(f"\n🏆 MISSION ACCOMPLISHED!")
            print(f"Successfully scraped {self.results['total_scraped']} properties!")
        elif self.results['total_scraped'] > 0:
            print(f"\n⚠️ PARTIAL SUCCESS")
            print(f"Scraped {self.results['total_scraped']}/{self.target_properties} properties")
            print(f"Strategies working - can scale up with optimization")
        else:
            print(f"\n❌ NO PROPERTIES SCRAPED")
            print(f"Need to wait for account activation or try different approach")


def main():
    """Main execution"""

    target = 100
    if len(sys.argv) > 1:
        target = int(sys.argv[1])

    orchestrator = ProductionScrapingOrchestrator(target_properties=target)
    orchestrator.execute_production_scrape()


if __name__ == "__main__":
    print("🚀 STARTING PRODUCTION SCRAPING WITH TIMING")
    main()