#!/usr/bin/env python3
"""
ScrapingBee Production Scraper for realestate.com.au
Optimized for trial account: 1000 credits, concurrency 5
"""

import time
import json
import random
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys

sys.path.append(str(Path(__file__).parent))


class ScrapingBeeProductionScraper:
    """Production scraper using ScrapingBee for Kasada bypass"""

    def __init__(self, api_key, target_properties=100):
        self.api_key = api_key
        self.target_properties = target_properties
        self.client = ScrapingBeeClient(api_key=api_key)
        self.scraped_properties = []
        self.credits_used = 0
        self.max_concurrency = 5  # Trial account limit

    def test_scrapingbee_kasada_bypass(self):
        """Test ScrapingBee against Kasada protection"""

        print("🐝 TESTING SCRAPINGBEE KASADA BYPASS")
        print("="*60)

        # Optimal parameters for Kasada bypass
        kasada_params = {
            'render_js': True,           # Essential for JavaScript challenges
            'premium_proxy': True,       # Use premium residential proxies
            'country_code': 'AU',        # Australian IP addresses
            'device': 'desktop',         # Desktop device simulation
            'window_width': 1366,
            'window_height': 768,
            'wait_browser': 'networkidle',  # Wait for complete load
            'wait': 5000,               # Additional wait for challenges
            'block_ads': True,          # Block ads for faster loading
            'stealth_proxy': True,      # Enable stealth mode
            'session_id': random.randint(1000, 9999),  # Session persistence
        }

        print("🎯 Testing Brisbane property listings...")
        print("Parameters optimized for Kasada bypass:")
        for key, value in kasada_params.items():
            if key != 'session_id':
                print(f"  {key}: {value}")

        try:
            start_time = time.time()

            response = self.client.get(
                'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                params=kasada_params,
                timeout=90  # Extended timeout for challenge resolution
            )

            test_time = time.time() - start_time
            self.credits_used += 1

            print(f"⏱️ Request time: {test_time:.1f} seconds")
            print(f"📊 Response status: {response.status_code}")
            print(f"📊 Content length: {len(response.content) if response.content else 0}")
            print(f"💳 Credits used: {self.credits_used}/1000")

            if response.status_code == 200:
                print("🚀 SCRAPINGBEE KASADA BYPASS SUCCESSFUL!")

                # Analyze content quality
                content = response.text.lower()
                property_indicators = ['property', 'bedroom', 'bathroom', 'real estate', 'listing', '$']
                found_indicators = [ind for ind in property_indicators if ind in content]

                print(f"🎯 Property indicators found: {found_indicators[:6]}")

                if len(found_indicators) >= 4:
                    print("✅ STRONG PROPERTY CONTENT CONFIRMED!")

                    # Quick property count check
                    soup = BeautifulSoup(response.text, 'html.parser')
                    potential_properties = soup.select('article, [class*="card"], [class*="property"], [class*="listing"]')
                    print(f"📊 Potential property elements: {len(potential_properties)}")

                    if len(potential_properties) > 10:
                        print("🎉 BREAKTHROUGH! Ready for production scraping!")
                        return True, kasada_params

                    else:
                        print("⚠️ Limited property elements found")

                else:
                    print("⚠️ Got 200 but weak property content")

            elif response.status_code == 429:
                print("❌ ScrapingBee also getting rate limited")
            else:
                print(f"❌ ScrapingBee failed: {response.status_code}")

        except Exception as e:
            print(f"❌ ScrapingBee test failed: {e}")

        return False, {}

    def extract_properties_from_response(self, html_content):
        """Extract properties from ScrapingBee response"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Multiple selector strategies
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
                    print(f"  Found {len(elements)} elements with: {selector}")

                    for i, element in enumerate(elements):
                        try:
                            prop_data = {}

                            # Extract title/address
                            title_candidates = [
                                element.find(['h2', 'h3'], string=lambda text: text and len(text.strip()) > 15),
                                element.find('span', string=lambda text: text and any(word in text.lower() for word in ['street', 'road', 'avenue'])),
                                element.find(['div'], string=lambda text: text and len(text.strip()) > 20)
                            ]

                            for title_elem in title_candidates:
                                if title_elem:
                                    title_text = title_elem.get_text(strip=True)
                                    if len(title_text) > 15:
                                        prop_data['title'] = title_text
                                        break

                            # Extract price
                            price_elem = element.find(string=lambda text: text and '$' in text and any(c.isdigit() for c in text))
                            if price_elem:
                                prop_data['price'] = price_elem.strip()

                            # Extract URL
                            link_elem = element.find('a', href=True)
                            if link_elem:
                                href = link_elem['href']
                                if href.startswith('/'):
                                    href = urljoin('https://www.realestate.com.au', href)
                                prop_data['url'] = href
                                prop_data['id'] = self.extract_property_id(href)

                            # Extract property features
                            feature_texts = element.find_all(string=lambda text: text and
                                                           any(word in text.lower() for word in ['bed', 'bath', 'car', 'garage']))
                            if feature_texts:
                                prop_data['features'] = [t.strip() for t in feature_texts[:5] if t.strip()]

                            if prop_data.get('title') and len(prop_data['title']) > 15:
                                properties.append(prop_data)

                        except Exception as e:
                            continue  # Skip problematic elements

                    break  # Use first successful selector

            print(f"  ✅ Extracted {len(properties)} properties")
            return properties

        except Exception as e:
            print(f"❌ Property extraction failed: {e}")
            return []

    def extract_property_id(self, url):
        """Extract property ID from URL"""
        import re
        match = re.search(r'/property/[^/]*?-(\d+)-', url)
        if match:
            return match.group(1)

        match = re.search(r'property/(\d+)', url)
        if match:
            return match.group(1)

        return f"scrapingbee_{random.randint(10000, 99999)}"

    def scrape_single_page(self, page_info):
        """Scrape a single page with ScrapingBee"""

        page_num, base_params = page_info
        url = f'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-{page_num}'

        print(f"📄 Scraping page {page_num}: {url}")

        try:
            # Add session variation for each page
            params = base_params.copy()
            params['session_id'] = random.randint(1000, 9999)

            response = self.client.get(url, params=params, timeout=90)

            self.credits_used += 1

            print(f"  Page {page_num} status: {response.status_code} (Credits: {self.credits_used}/1000)")

            if response.status_code == 200:
                # Extract properties
                properties = self.extract_properties_from_response(response.text)

                if properties:
                    print(f"  ✅ Page {page_num}: Found {len(properties)} properties")
                    return properties
                else:
                    print(f"  ⚠️ Page {page_num}: No properties extracted")

            elif response.status_code == 429:
                print(f"  ❌ Page {page_num}: Rate limited")
            else:
                print(f"  ❌ Page {page_num}: Failed {response.status_code}")

        except Exception as e:
            print(f"  ❌ Page {page_num} error: {e}")

        return []

    def run_production_scrape_with_timing(self):
        """Run production scrape with full timing analysis"""

        print(f"🚀 SCRAPINGBEE PRODUCTION SCRAPE")
        print(f"Target: {self.target_properties} properties")
        print(f"Credits available: 1000")
        print(f"Max concurrency: {self.max_concurrency}")
        print("="*70)

        # Test single page first
        print("🧪 Testing single page for validation...")

        base_params = {
            'render_js': True,
            'premium_proxy': True,
            'country_code': 'AU',
            'device': 'desktop',
            'window_width': 1366,
            'window_height': 768,
            'wait_browser': 'networkidle',
            'wait': 5000,
            'block_ads': True,
            'stealth_proxy': True,
        }

        test_success, validated_params = self.test_scrapingbee_kasada_bypass()

        if not test_success:
            print("❌ ScrapingBee test failed - cannot proceed with production scrape")
            return False

        print(f"\n✅ Test successful! Proceeding with production scrape...")

        # Calculate pages needed (assuming 20 properties per page)
        pages_needed = min((self.target_properties // 20) + 1, 10)  # Max 10 pages
        credits_needed = pages_needed

        print(f"📊 Production plan:")
        print(f"  Pages to scrape: {pages_needed}")
        print(f"  Credits needed: ~{credits_needed}")
        print(f"  Credits remaining after: {1000 - credits_needed}")

        if credits_needed > 900:  # Leave some buffer
            print("⚠️ High credit usage - reducing scope to conserve credits")
            pages_needed = 5

        # Prepare page jobs for concurrent scraping
        page_jobs = [(page_num, validated_params) for page_num in range(1, pages_needed + 1)]

        start_time = time.time()
        all_properties = []

        print(f"\n🔄 Starting concurrent scraping ({self.max_concurrency} concurrent)...")

        # Execute with controlled concurrency
        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            # Submit jobs
            future_to_page = {
                executor.submit(self.scrape_single_page, job): job[0]
                for job in page_jobs
            }

            # Collect results
            for future in as_completed(future_to_page):
                page_num = future_to_page[future]
                try:
                    page_properties = future.result()
                    if page_properties:
                        all_properties.extend(page_properties)
                        print(f"✅ Page {page_num} completed: {len(page_properties)} properties")

                        # Stop if we've reached target
                        if len(all_properties) >= self.target_properties:
                            print(f"🎯 Target reached! {len(all_properties)} properties")
                            break

                    else:
                        print(f"❌ Page {page_num} yielded no properties")

                except Exception as e:
                    print(f"❌ Page {page_num} failed: {e}")

        total_time = time.time() - start_time

        # Save results and provide timing analysis
        if all_properties:
            saved_count = self.save_scrapingbee_properties(all_properties)

            print(f"\n🎉 SCRAPINGBEE PRODUCTION SCRAPE COMPLETE!")
            print(f"📊 PERFORMANCE METRICS:")
            print(f"  Properties found: {len(all_properties)}")
            print(f"  Properties saved: {saved_count}")
            print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print(f"  Credits used: {self.credits_used}/1000")
            print(f"  Credits remaining: {1000 - self.credits_used}")

            if saved_count > 0:
                avg_time = total_time / saved_count
                print(f"  Average time per property: {avg_time:.2f} seconds")
                print(f"  Properties per hour: {3600/avg_time:.0f}")

                # Calculate scaling estimates
                credits_per_100 = (100 / saved_count) * self.credits_used
                time_per_100 = (100 / saved_count) * total_time / 60

                print(f"\n📈 SCALING ESTIMATES:")
                print(f"  Credits needed for 100 properties: ~{credits_per_100:.0f}")
                print(f"  Time for 100 properties: ~{time_per_100:.1f} minutes")

            if saved_count >= self.target_properties:
                print(f"🏆 MISSION ACCOMPLISHED!")
                return True

            elif saved_count > 0:
                print(f"⚠️ Partial success: {saved_count}/{self.target_properties}")
                print("Can scale up with additional credits")
                return True

        else:
            print(f"\n❌ No properties scraped")
            print(f"Credits used: {self.credits_used}")

        return False

    def save_scrapingbee_properties(self, properties):
        """Save properties with detailed metadata"""

        if not properties:
            return 0

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
                    'features': prop.get('features', []),
                    'scraped_at': timestamp,
                    'method': 'scrapingbee_kasada_bypass',
                    'service': 'scrapingbee_premium_trial',
                    'protection_bypassed': 'kasada_enterprise',
                    'status': 'active',
                    'address': {'full': prop.get('title', '')},
                    'property_type': '',
                    'bedrooms': None,
                    'bathrooms': None,
                    'parking': None,
                    'images': [],
                    'agent': {}
                }

                # Parse features for structured data
                if prop.get('features'):
                    for feature in prop['features']:
                        feature_lower = feature.lower()
                        if 'bed' in feature_lower:
                            import re
                            bed_match = re.search(r'(\d+)', feature)
                            if bed_match:
                                detailed_prop['bedrooms'] = int(bed_match.group(1))

                        if 'bath' in feature_lower:
                            import re
                            bath_match = re.search(r'(\d+)', feature)
                            if bath_match:
                                detailed_prop['bathrooms'] = int(bath_match.group(1))

                        if 'car' in feature_lower or 'garage' in feature_lower:
                            import re
                            car_match = re.search(r'(\d+)', feature)
                            if car_match:
                                detailed_prop['parking'] = int(car_match.group(1))

                filename = f"{property_id}_scrapingbee.json"
                filepath = data_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(detailed_prop, f, indent=2, ensure_ascii=False)

                saved_count += 1

            except Exception as e:
                print(f"❌ Save error: {e}")

        print(f"💾 Saved {saved_count} properties via ScrapingBee")
        return saved_count

    def get_property_details(self, property_url, base_params):
        """Get detailed property information from individual property page"""

        try:
            print(f"    🔍 Getting details for: {property_url}")

            # Use same parameters but with different session
            detail_params = base_params.copy()
            detail_params['session_id'] = random.randint(1000, 9999)

            response = self.client.get(property_url, params=detail_params, timeout=60)
            self.credits_used += 1

            if response.status_code == 200:
                # Extract detailed information
                soup = BeautifulSoup(response.text, 'html.parser')

                details = {}

                # Extract description
                desc_selectors = ['.property-description', '[class*="description"]', 'section p']
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        details['description'] = desc_elem.get_text(strip=True)
                        break

                # Extract images
                img_selectors = ['.property-images img', '.gallery img', 'img']
                images = []
                for selector in img_selectors:
                    img_elements = soup.select(selector)
                    for img in img_elements[:10]:  # Limit to 10 images
                        src = img.get('src') or img.get('data-src')
                        if src and not src.startswith('data:'):
                            if src.startswith('/'):
                                src = urljoin('https://www.realestate.com.au', src)
                            images.append({'url': src, 'alt': f'Property image'})

                if images:
                    details['images'] = images

                return details

        except Exception as e:
            print(f"    ❌ Detail extraction error: {e}")

        return {}


def run_scrapingbee_with_api_key(api_key, target_properties=20):
    """Run ScrapingBee scraper with provided API key"""

    print(f"🐝 SCRAPINGBEE PRODUCTION TEST")
    print(f"API Key: {api_key[:10]}...")
    print(f"Target: {target_properties} properties")
    print("="*70)

    scraper = ScrapingBeeProductionScraper(api_key, target_properties)

    # Run production scrape
    success = scraper.run_production_scrape_with_timing()

    if success:
        print(f"\n🎯 SCRAPINGBEE SUCCESS!")
        print("Ready to scale to full 100 properties if needed")

        # Show final status
        from main import show_status
        show_status()

        return True

    else:
        print(f"\n⚠️ ScrapingBee needs optimization or has API issues")
        return False


def main():
    """Main execution - waiting for API key"""

    print("🚀 SCRAPINGBEE KASADA BYPASS IMPLEMENTATION")
    print("="*70)

    # Your ScrapingBee API key
    api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"

    if False:  # API key provided
        print("⚠️ WAITING FOR SCRAPINGBEE API KEY")
        print("Please provide your ScrapingBee trial API key to proceed")
        print("\n📋 READY TO TEST:")
        print("1. ScrapingBee trial: 1000 credits, concurrency 5")
        print("2. Kasada bypass parameters optimized")
        print("3. Production scraper ready")
        print("4. Full timing analysis included")

        return False

    # Run with provided API key
    return run_scrapingbee_with_api_key(api_key, target_properties=20)


if __name__ == "__main__":
    success = main()

    if success:
        print(f"\n🏆 SCRAPINGBEE KASADA BYPASS SUCCESSFUL!")
        print("This approach will reliably get your 100 properties!")
    else:
        print(f"\n📝 Provide API key to proceed with ScrapingBee testing")