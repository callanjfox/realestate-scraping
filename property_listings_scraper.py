#!/usr/bin/env python3
"""
Property Listings Scraper - Stage 1 of Two-Stage System
Extracts property URLs from Brisbane search result pages with pagination support
"""

from scrapingbee import ScrapingBeeClient
from lxml import html as lxml_html
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

class PropertyListingsScraper:
    """Scraper for property search result pages with pagination and incremental sync"""

    def __init__(self):
        self.api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.base_url = "https://www.realestate.com.au"

        # Create tracking directory
        self.tracking_dir = Path("data/tracking")
        self.tracking_dir.mkdir(parents=True, exist_ok=True)

        # Create listings debug directory
        self.listings_dir = Path("data/listings")
        self.listings_dir.mkdir(parents=True, exist_ok=True)

    def scrape_listings_page(self, url, page_num=1):
        """Scrape property URLs from a single listings page"""

        print(f"\n📄 SCRAPING LISTINGS PAGE {page_num}")
        print(f"URL: {url}")
        print("-" * 60)

        try:
            # ScrapingBee request for listings page
            params = {
                'render_js': True,
                'block_resources': False,  # Load all resources for complete page
                'stealth_proxy': True,
                'country_code': 'AU'
            }

            print(f"📡 Making ScrapingBee request...")
            response = self.client.get(url, params=params, timeout=120)

            if response.status_code == 200:
                print(f"✅ Page fetched successfully ({len(response.text):,} chars)")

                # Save HTML for debugging
                self.save_listings_html(response.text, page_num)

                # Extract property URLs
                property_urls = self.extract_property_urls_from_html(response.text)

                if property_urls:
                    print(f"🏠 Found {len(property_urls)} property URLs")

                    # Show sample URLs
                    for i, url in enumerate(property_urls[:3], 1):
                        property_id = self.extract_property_id_from_url(url)
                        print(f"  {i}. {property_id}: {url}")

                    if len(property_urls) > 3:
                        print(f"  ... and {len(property_urls) - 3} more")

                    return property_urls
                else:
                    print(f"❌ No property URLs found")
                    return []

            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error scraping page {page_num}: {e}")
            return []

    def extract_property_urls_from_html(self, html_content):
        """Extract property URLs from search results HTML"""

        property_urls = []

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            tree = lxml_html.fromstring(html_content)

            print(f"  🔍 Searching for property links...")

            # Method 1: Look for property links with specific patterns
            property_patterns = [
                r'/property-[^/]+-qld-[^/]+-\d{9}',  # Main property URL pattern
                r'/property-[^/]+-qld-[^/]+-\d{8}',   # Alternative 8-digit pattern
            ]

            for pattern in property_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    full_url = urljoin(self.base_url, match)
                    if full_url not in property_urls:
                        property_urls.append(full_url)

            # Method 2: Look for anchor tags with property links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if '/property-' in href and '-qld-' in href and re.search(r'-\d{8,9}', href):
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    if href not in property_urls:
                        property_urls.append(href)

            # Method 3: XPath approach for property cards
            try:
                property_elements = tree.xpath('//a[contains(@href, "/property-") and contains(@href, "-qld-")]')
                for element in property_elements:
                    href = element.get('href', '')
                    if href and re.search(r'-\d{8,9}', href):
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        if href not in property_urls:
                            property_urls.append(href)
            except:
                pass

            print(f"  📊 Extraction methods found {len(property_urls)} total URLs")

        except Exception as e:
            print(f"  ❌ Error extracting URLs: {e}")

        return list(set(property_urls))  # Remove duplicates

    def extract_property_id_from_url(self, url):
        """Extract property ID from property URL"""
        match = re.search(r'-(\d{8,9})(?:\?|#|$)', url)
        return match.group(1) if match else None

    def find_next_page_url(self, html_content, current_url):
        """Find next page URL for pagination"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Method 1: Look for "Next" link
            next_links = soup.find_all('a', text=re.compile(r'Next|>|→'))
            for link in next_links:
                href = link.get('href', '')
                if href and 'list-' in href:
                    return urljoin(self.base_url, href)

            # Method 2: Look for pagination links
            pagination_links = soup.find_all('a', href=re.compile(r'list-\d+'))
            if pagination_links:
                # Get the highest page number + 1
                current_page = self.extract_page_number(current_url)
                next_page = current_page + 1

                for link in pagination_links:
                    href = link.get('href', '')
                    if f'list-{next_page}' in href:
                        return urljoin(self.base_url, href)

            # Method 3: Construct next page URL manually
            current_page = self.extract_page_number(current_url)
            if current_page:
                next_page = current_page + 1
                next_url = re.sub(r'list-\d+', f'list-{next_page}', current_url)
                return next_url

        except Exception as e:
            print(f"  ❌ Error finding next page: {e}")

        return None

    def extract_page_number(self, url):
        """Extract current page number from URL"""
        match = re.search(r'list-(\d+)', url)
        return int(match.group(1)) if match else 1

    def save_listings_html(self, html_content, page_num):
        """Save listings HTML for debugging"""
        html_file = self.listings_dir / f"listings_page_{page_num}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  💾 Listings HTML saved: {html_file}")

    def scrape_multiple_pages(self, start_url, max_pages=2):
        """Scrape multiple pages of listings"""

        print(f"🚀 SCRAPING BRISBANE PROPERTY LISTINGS")
        print(f"Start URL: {start_url}")
        print(f"Max pages: {max_pages}")
        print("="*70)

        all_property_urls = []
        current_url = start_url
        page_num = 1

        for page in range(max_pages):
            if not current_url:
                print(f"❌ No more pages to scrape")
                break

            # Scrape current page
            page_urls = self.scrape_listings_page(current_url, page_num)

            if page_urls:
                all_property_urls.extend(page_urls)
                print(f"  ✅ Page {page_num}: {len(page_urls)} properties found")

                # Find next page URL if not last page
                if page < max_pages - 1:
                    # Get the HTML again to find next page (we need the response)
                    params = {
                        'render_js': True,
                        'block_resources': False,
                        'stealth_proxy': True,
                        'country_code': 'AU'
                    }

                    try:
                        response = self.client.get(current_url, params=params, timeout=120)
                        if response.status_code == 200:
                            next_url = self.find_next_page_url(response.text, current_url)
                            if next_url and next_url != current_url:
                                current_url = next_url
                                page_num += 1
                                print(f"  🔄 Next page: {current_url}")
                                time.sleep(3)  # Respectful delay between pages
                            else:
                                print(f"  ⏹️ No next page found")
                                break
                    except Exception as e:
                        print(f"  ❌ Error finding next page: {e}")
                        break
            else:
                print(f"  ❌ Page {page_num}: No properties found")
                break

        # Remove duplicates and show summary
        unique_urls = list(set(all_property_urls))

        print(f"\n🎉 LISTINGS SCRAPING COMPLETE!")
        print(f"📊 Total properties found: {len(unique_urls)}")
        print(f"📄 Pages scraped: {page_num}")

        # Extract and show property IDs
        property_ids = []
        for url in unique_urls:
            prop_id = self.extract_property_id_from_url(url)
            if prop_id:
                property_ids.append(prop_id)

        print(f"🆔 Unique property IDs: {len(property_ids)}")

        if property_ids:
            print(f"📋 Sample property IDs: {property_ids[:5]}")

        # Save results
        self.save_listings_results(unique_urls, property_ids)

        return unique_urls, property_ids

    def save_listings_results(self, property_urls, property_ids):
        """Save listings scraping results"""

        results = {
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'total_properties': len(property_urls),
            'total_unique_ids': len(property_ids),
            'property_urls': property_urls,
            'property_ids': property_ids
        }

        results_file = self.tracking_dir / "latest_listings_scrape.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {results_file}")


def test_listings_scraper():
    """Test the listings scraper on first 2 pages"""

    print("🧪 TESTING LISTINGS SCRAPER")
    print("="*50)

    scraper = PropertyListingsScraper()

    # Test URL provided by user
    start_url = "https://www.realestate.com.au/buy/property-house-in-brisbane+-+greater+region,+qld/list-1?activeSort=list-date&source=refinement"

    # Test first 2 pages
    property_urls, property_ids = scraper.scrape_multiple_pages(start_url, max_pages=2)

    if property_urls:
        print(f"\n✅ LISTINGS SCRAPER TEST SUCCESSFUL!")
        print(f"🏠 Found {len(property_urls)} property URLs")
        print(f"🆔 Found {len(property_ids)} property IDs")
        return True
    else:
        print(f"\n❌ Listings scraper test failed")
        return False


if __name__ == "__main__":
    test_listings_scraper()