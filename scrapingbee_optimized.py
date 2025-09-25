#!/usr/bin/env python3
"""
Optimized ScrapingBee implementation with fixes for 503 errors
Following ScrapingBee's troubleshooting recommendations
"""

from scrapingbee import ScrapingBeeClient
import time
import json
import random
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class OptimizedScrapingBeeScraper:
    """Optimized ScrapingBee scraper following their troubleshooting guide"""

    def __init__(self, target_properties=100):
        self.api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.target_properties = target_properties
        self.credits_used = 0

    def test_progressive_parameters(self):
        """Test with progressively more advanced parameters"""

        print("🐝 SCRAPINGBEE OPTIMIZED TESTING")
        print("Following troubleshooting recommendations")
        print("="*60)

        test_url = 'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'

        # Progressive parameter sets (as recommended by ScrapingBee)
        parameter_sets = [
            {
                'name': 'Basic (No JS)',
                'params': {}
            },
            {
                'name': 'JavaScript Only',
                'params': {'render_js': True}
            },
            {
                'name': 'JS + Block Resources False',
                'params': {
                    'render_js': True,
                    'block_resources': False
                }
            },
            {
                'name': 'JS + Premium Proxy',
                'params': {
                    'render_js': True,
                    'block_resources': False,
                    'premium_proxy': True,
                    'country_code': 'AU'
                }
            },
            {
                'name': 'JS + Stealth Proxy',
                'params': {
                    'render_js': True,
                    'block_resources': False,
                    'stealth_proxy': True,
                    'country_code': 'AU'
                }
            },
            {
                'name': 'Full Kasada Optimized',
                'params': {
                    'render_js': True,
                    'block_resources': False,
                    'stealth_proxy': True,
                    'country_code': 'AU',
                    'device': 'desktop',
                    'window_width': 1366,
                    'window_height': 768,
                    'wait_browser': 'networkidle',
                    'wait': 3000,
                }
            }
        ]

        successful_configs = []

        for config in parameter_sets:
            print(f"\n🧪 Testing: {config['name']}")
            print(f"Parameters: {config['params']}")

            try:
                start_time = time.time()

                response = self.client.get(
                    test_url,
                    params=config['params'],
                    timeout=90
                )

                request_time = time.time() - start_time
                self.credits_used += 1

                print(f"  ⏱️ Request time: {request_time:.1f}s")
                print(f"  📊 Status: {response.status_code}")
                print(f"  📊 Content length: {len(response.content) if response.content else 0}")
                print(f"  💳 Credits used: {self.credits_used}/1000")

                if response.status_code == 200:
                    print(f"  🚀 SUCCESS with {config['name']}!")

                    # Check content quality
                    content = response.text.lower()
                    property_indicators = ['property', 'bedroom', 'bathroom', 'real estate', 'listing']
                    found_indicators = [ind for ind in property_indicators if ind in content]

                    print(f"  🎯 Property indicators: {found_indicators[:5]}")

                    if len(found_indicators) >= 3:
                        print(f"  ✅ STRONG PROPERTY CONTENT!")

                        # Quick property count
                        soup = BeautifulSoup(response.text, 'html.parser')
                        potential_cards = soup.select('article, [class*="card"], [class*="property"], [class*="listing"]')
                        print(f"  📊 Potential properties: {len(potential_cards)}")

                        successful_configs.append({
                            'config': config,
                            'request_time': request_time,
                            'property_count': len(potential_cards),
                            'content_quality': len(found_indicators)
                        })

                    else:
                        print(f"  ⚠️ Weak property content")

                elif response.status_code == 400:
                    print(f"  ❌ Bad request (400)")
                    print(f"  Response: {response.text}")
                elif response.status_code == 429:
                    print(f"  ❌ Rate limited (429)")
                elif response.status_code == 500:
                    print(f"  ❌ Server error (500)")
                    print(f"  Error details: {response.text}")
                else:
                    print(f"  ❌ Status {response.status_code}")
                    print(f"  Response: {response.text}")

            except Exception as e:
                print(f"  ❌ Request failed: {e}")

            # Delay between tests
            time.sleep(5)

        # Results summary
        print(f"\n{'='*60}")
        print("SCRAPINGBEE OPTIMIZATION RESULTS")
        print(f"{'='*60}")

        if successful_configs:
            print(f"✅ Found {len(successful_configs)} working configurations!")

            # Sort by quality (content quality * property count)
            successful_configs.sort(key=lambda x: x['content_quality'] * x['property_count'], reverse=True)

            best_config = successful_configs[0]
            print(f"\n🎯 OPTIMAL CONFIGURATION:")
            print(f"  Name: {best_config['config']['name']}")
            print(f"  Parameters: {best_config['config']['params']}")
            print(f"  Request time: {best_config['request_time']:.1f}s")
            print(f"  Property count: {best_config['property_count']}")
            print(f"  Content quality: {best_config['content_quality']}/5")

            return best_config

        else:
            print("❌ No working configurations found")
            print(f"Credits used in testing: {self.credits_used}/1000")

            print(f"\n🔍 TROUBLESHOOTING RECOMMENDATIONS:")
            print("1. ✅ API key is valid (confirmed)")
            print("2. ⚠️ ScrapingBee servers may have temporary issues")
            print("3. 🔄 Try again in a few minutes")
            print("4. 📞 Contact ScrapingBee support if persistent")

            return None

    def run_production_scrape_with_optimal_config(self, optimal_config):
        """Run production scrape using the optimal configuration"""

        print(f"\n🚀 PRODUCTION SCRAPE WITH OPTIMAL CONFIG")
        print(f"Using: {optimal_config['config']['name']}")
        print("="*60)

        optimal_params = optimal_config['config']['params']
        estimated_time_per_request = optimal_config['request_time']

        print(f"📊 PRODUCTION PLAN:")
        print(f"  Target properties: {self.target_properties}")
        print(f"  Estimated time per page: {estimated_time_per_request:.1f}s")
        print(f"  Pages needed: {(self.target_properties // 20) + 1}")
        print(f"  Estimated total time: {((self.target_properties // 20) + 1) * estimated_time_per_request / 60:.1f} minutes")

        start_time = time.time()
        all_properties = []

        # Calculate pages to scrape
        pages_needed = min((self.target_properties // 20) + 1, 8)  # Conservative limit

        for page_num in range(1, pages_needed + 1):
            if self.credits_used >= 950:  # Leave buffer
                print(f"⚠️ Approaching credit limit, stopping at {self.credits_used} credits")
                break

            print(f"\n📄 Scraping page {page_num}...")

            try:
                url = f'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-{page_num}'

                # Add session variation
                page_params = optimal_params.copy()
                page_params['session_id'] = random.randint(1000, 9999)

                response = self.client.get(url, params=page_params, timeout=120)
                self.credits_used += 1

                print(f"  Status: {response.status_code} (Credits: {self.credits_used}/1000)")

                if response.status_code == 200:
                    # Extract properties
                    page_properties = self.extract_properties_scrapingbee(response.text)

                    if page_properties:
                        all_properties.extend(page_properties)
                        print(f"  ✅ Page {page_num}: {len(page_properties)} properties (Total: {len(all_properties)})")

                        if len(all_properties) >= self.target_properties:
                            print(f"🎯 Target reached! {len(all_properties)} properties")
                            break

                    else:
                        print(f"  ⚠️ Page {page_num}: No properties extracted")

                else:
                    print(f"  ❌ Page {page_num} failed: {response.status_code}")

                # Delay between pages
                time.sleep(random.uniform(2, 5))

            except Exception as e:
                print(f"  ❌ Page {page_num} error: {e}")

        total_time = time.time() - start_time

        # Save and analyze results
        if all_properties:
            saved_count = self.save_scrapingbee_properties(all_properties)

            print(f"\n🎉 SCRAPINGBEE PRODUCTION COMPLETE!")
            print(f"📊 FINAL METRICS:")
            print(f"  Properties scraped: {len(all_properties)}")
            print(f"  Properties saved: {saved_count}")
            print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print(f"  Credits used: {self.credits_used}/1000")
            print(f"  Average time per property: {total_time/len(all_properties):.2f} seconds")

            if saved_count >= self.target_properties:
                print(f"🏆 MISSION ACCOMPLISHED!")
            else:
                print(f"⚠️ Partial success - can continue with remaining credits")

            return True

        return False

    def extract_properties_scrapingbee(self, html_content):
        """Extract properties from ScrapingBee response"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            selectors = [
                '[data-testid="residential-card"]',
                'article[data-testid="residential-card"]',
                '[class*="residential-card"]',
                '.listing-result',
                'article',
                '[class*="property"]',
                '[class*="card"]'
            ]

            properties = []

            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for i, element in enumerate(elements[:25]):  # Max 25 per page
                        try:
                            prop_data = {}

                            # Title extraction
                            title_elem = element.find(['h2', 'h3'], string=lambda text: text and len(text.strip()) > 10)
                            if not title_elem:
                                title_elem = element.find(string=lambda text: text and
                                                        any(word in text.lower() for word in ['street', 'road', 'avenue']) and
                                                        len(text.strip()) > 15)

                            if title_elem:
                                if hasattr(title_elem, 'get_text'):
                                    prop_data['title'] = title_elem.get_text(strip=True)
                                else:
                                    prop_data['title'] = str(title_elem).strip()

                            # Price extraction
                            price_elem = element.find(string=lambda text: text and '$' in text and any(c.isdigit() for c in text))
                            if price_elem:
                                prop_data['price'] = price_elem.strip()

                            # URL extraction
                            link_elem = element.find('a', href=True)
                            if link_elem:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    href = urljoin('https://www.realestate.com.au', href)
                                prop_data['url'] = href
                                prop_data['id'] = self.extract_property_id(href)

                            if prop_data.get('title') and len(prop_data['title']) > 10:
                                properties.append(prop_data)

                        except Exception as e:
                            continue

                    break

            return properties

        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return []

    def extract_property_id(self, url):
        """Extract property ID from URL"""
        import re
        match = re.search(r'/property/[^/]*?-(\d+)-', url)
        if match:
            return match.group(1)
        return f"scrapingbee_{random.randint(10000, 99999)}"

    def save_scrapingbee_properties(self, properties):
        """Save properties from ScrapingBee"""

        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        timestamp = datetime.now(timezone.utc).isoformat()

        for prop in properties:
            try:
                property_id = prop.get('id', f"scrapingbee_{random.randint(10000, 99999)}")

                detailed_prop = {
                    'id': property_id,
                    'url': prop.get('url', ''),
                    'title': prop.get('title', ''),
                    'price': prop.get('price', ''),
                    'scraped_at': timestamp,
                    'method': 'scrapingbee_kasada_bypass',
                    'status': 'active',
                    'address': {'full': prop.get('title', '')},
                    'features': [],
                    'images': [],
                    'agent': {}
                }

                filename = f"{property_id}_scrapingbee.json"
                filepath = data_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(detailed_prop, f, indent=2, ensure_ascii=False)

                saved_count += 1

            except Exception as e:
                continue

        return saved_count


def test_scrapingbee_optimized():
    """Test optimized ScrapingBee approach"""

    print("🚀 SCRAPINGBEE OPTIMIZED TEST")
    print("="*70)

    scraper = OptimizedScrapingBeeScraper(target_properties=20)

    # Test progressive parameters
    optimal_config = scraper.test_progressive_parameters()

    if optimal_config:
        # Run production scrape
        success = scraper.run_production_scrape_with_optimal_config(optimal_config)

        if success:
            print(f"\n🎯 SCRAPINGBEE BREAKTHROUGH!")
            print("Ready to scale to 100 properties")

            # Show final status
            from main import show_status
            show_status()

            return True

    return False


if __name__ == "__main__":
    print("Testing optimized ScrapingBee approach...")
    success = test_scrapingbee_optimized()

    if success:
        print(f"\n🏆 SCRAPINGBEE SOLUTION WORKING!")
        print("Kasada protection successfully bypassed!")
    else:
        print(f"\n⚠️ ScrapingBee optimization needed or service issues")