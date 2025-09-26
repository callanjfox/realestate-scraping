#!/usr/bin/env python3
"""
Enhanced Property Scraper - Complete Details + Images
Two-phase approach:
1. Scrape listing pages for property URLs (proven working)
2. Scrape individual property pages for full details + images
"""

import time
import json
import random
import requests
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


class EnhancedPropertyScraper:
    """Two-phase scraper for complete property details"""

    def __init__(self, api_key, target_properties=20):
        self.api_key = api_key
        self.client = ScrapingBeeClient(api_key=api_key)
        self.target_properties = target_properties
        self.credits_used = 0

        # Proven working parameters
        self.listing_params = {
            'render_js': True,
            'block_resources': False,
            'stealth_proxy': True,
            'country_code': 'AU'
        }

        # Different parameters for individual property pages
        self.detail_params = {
            'render_js': True,
            'block_resources': False,
            'premium_proxy': True,  # Use premium for detail pages
            'country_code': 'AU',
            'wait': 3000,  # Extra wait for detail pages
        }

    def phase1_get_property_urls(self, max_pages=3):
        """Phase 1: Get property URLs from listing pages"""

        print("🔍 PHASE 1: EXTRACTING PROPERTY URLS")
        print("="*50)

        property_urls = []

        for page_num in range(1, max_pages + 1):
            if self.credits_used >= 900:  # Credit limit
                break

            print(f"\n📄 Listing page {page_num}...")

            try:
                url = f'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-{page_num}'

                response = self.client.get(url, params=self.listing_params, timeout=120)
                self.credits_used += 1

                print(f"  Status: {response.status_code} (Credits: {self.credits_used}/1000)")

                if response.status_code == 200:
                    # Extract property URLs
                    page_urls = self.extract_property_urls(response.text)

                    if page_urls:
                        property_urls.extend(page_urls)
                        print(f"  ✅ Found {len(page_urls)} property URLs (Total: {len(property_urls)})")

                        if len(property_urls) >= self.target_properties:
                            print(f"🎯 URL target reached: {len(property_urls)}")
                            break

                    else:
                        print(f"  ⚠️ No URLs extracted from page {page_num}")

                else:
                    print(f"  ❌ Page {page_num} failed: {response.status_code}")

                # Delay between listing pages
                time.sleep(random.uniform(3, 8))

            except Exception as e:
                print(f"  ❌ Page {page_num} error: {e}")

        # Limit to target and remove duplicates
        unique_urls = list(dict.fromkeys(property_urls))[:self.target_properties]

        print(f"\n✅ Phase 1 complete!")
        print(f"  Property URLs collected: {len(unique_urls)}")
        print(f"  Credits used: {self.credits_used}/1000")

        return unique_urls

    def extract_property_urls(self, html_content):
        """Extract property URLs from listing page"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Multiple strategies for URL extraction
            url_selectors = [
                'a[href*="/property-"]',  # Direct property links
                '[class*="residential-card"] a',  # Links within property cards
                'article a[href*="/property"]',  # Article links
                'a[href*="/property/"]',  # General property links
            ]

            urls = []

            for selector in url_selectors:
                links = soup.select(selector)
                if links:
                    print(f"    Using selector: {selector} ({len(links)} links)")

                    for link in links:
                        href = link.get('href')
                        if href and '/property' in href:
                            if href.startswith('/'):
                                href = urljoin('https://www.realestate.com.au', href)

                            # Validate URL format
                            if 'realestate.com.au/property' in href:
                                urls.append(href)

                    break  # Use first successful selector

            # Remove duplicates and return
            unique_urls = list(dict.fromkeys(urls))
            return unique_urls

        except Exception as e:
            print(f"    URL extraction error: {e}")
            return []

    def phase2_get_property_details(self, property_urls):
        """Phase 2: Get detailed information from individual property pages"""

        print(f"\n🏠 PHASE 2: EXTRACTING DETAILED PROPERTY INFORMATION")
        print(f"Scraping {len(property_urls)} individual property pages...")
        print("="*60)

        detailed_properties = []

        # Process properties sequentially to be conservative with credits
        for i, property_url in enumerate(property_urls):
            if self.credits_used >= 950:  # Conservative limit
                print(f"⚠️ Credit limit reached: {self.credits_used}/1000")
                break

            print(f"\n🏡 [{i+1:02d}/{len(property_urls)}] {property_url}")

            try:
                # Get detailed property information
                property_details = self.scrape_individual_property(property_url)

                if property_details:
                    detailed_properties.append(property_details)
                    print(f"    ✅ Complete details extracted")
                    print(f"    📊 Bedrooms: {property_details.get('bedrooms', 'N/A')}")
                    print(f"    📊 Bathrooms: {property_details.get('bathrooms', 'N/A')}")
                    print(f"    📊 Description: {len(property_details.get('description', ''))} chars")
                    print(f"    📊 Images: {len(property_details.get('images', []))}")

                else:
                    print(f"    ❌ Failed to extract details")

                # Delay between individual properties
                delay = random.uniform(5, 12)
                print(f"    ⏳ Delay: {delay:.1f}s")
                time.sleep(delay)

            except Exception as e:
                print(f"    ❌ Error: {e}")

        print(f"\n✅ Phase 2 complete!")
        print(f"  Detailed properties: {len(detailed_properties)}")
        print(f"  Total credits used: {self.credits_used}/1000")

        return detailed_properties

    def scrape_individual_property(self, property_url):
        """Scrape individual property page for complete details"""

        try:
            response = self.client.get(property_url, params=self.detail_params, timeout=90)
            self.credits_used += 1

            if response.status_code == 200:
                return self.extract_complete_property_details(response.text, property_url)
            else:
                print(f"      Detail page failed: {response.status_code}")
                return None

        except Exception as e:
            print(f"      Detail extraction error: {e}")
            return None

    def extract_complete_property_details(self, html_content, property_url):
        """Extract complete property details from individual property page"""

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            property_details = {}

            # Extract property ID from URL
            property_id = self.extract_property_id(property_url)
            property_details['id'] = property_id
            property_details['url'] = property_url

            # Title/Address - multiple strategies
            title_selectors = [
                'h1',
                '.property-title h1',
                '[data-testid*="address"] h1',
                '.listing-details h1',
                'h1[class*="address"]'
            ]

            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        property_details['title'] = title
                        break

            # Price - comprehensive extraction
            price_selectors = [
                '.property-price',
                '[data-testid*="price"]',
                '.price-wrapper',
                '.listing-details .price',
                '[class*="price"]'
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text and ('$' in price_text or 'auction' in price_text.lower()):
                        property_details['price'] = price_text
                        break

            # Bedrooms, Bathrooms, Parking - comprehensive extraction
            self.extract_property_features(soup, property_details)

            # Description - multiple strategies
            description_selectors = [
                '.property-description p',
                '[data-testid*="description"] p',
                '.description p',
                '.listing-details .description',
                '.property-content p',
                'section[class*="description"] p'
            ]

            descriptions = []
            for selector in description_selectors:
                desc_elements = soup.select(selector)
                if desc_elements:
                    desc_texts = [elem.get_text(strip=True) for elem in desc_elements if elem.get_text(strip=True)]
                    if desc_texts:
                        descriptions.extend(desc_texts)
                        break

            if descriptions:
                property_details['description'] = ' '.join(descriptions)

            # Property features list
            feature_selectors = [
                '.property-features li',
                '.features li',
                '[data-testid*="features"] li',
                '.key-features li',
                'ul[class*="feature"] li'
            ]

            features = []
            for selector in feature_selectors:
                feature_elements = soup.select(selector)
                if feature_elements:
                    features = [elem.get_text(strip=True) for elem in feature_elements if elem.get_text(strip=True)]
                    break

            property_details['features'] = features[:10]  # Limit features

            # Images - comprehensive extraction
            property_details['images'] = self.extract_property_images(soup, property_url)

            # Agent information
            property_details['agent'] = self.extract_agent_info(soup)

            # Property type
            property_details['property_type'] = self.extract_property_type(soup)

            # Timestamps
            property_details['scraped_at'] = datetime.now(timezone.utc).isoformat()
            property_details['last_updated'] = datetime.now(timezone.utc).isoformat()
            property_details['method'] = 'enhanced_scrapingbee_two_phase'
            property_details['status'] = 'active'

            return property_details

        except Exception as e:
            print(f"      Complete extraction error: {e}")
            return None

    def extract_property_features(self, soup, property_details):
        """Extract bedrooms, bathrooms, parking from property page"""

        # Strategy 1: Look for specific feature elements
        feature_selectors = [
            '.property-features',
            '.key-features',
            '[data-testid*="features"]',
            '.listing-details',
            '.property-info'
        ]

        all_feature_text = ""

        for selector in feature_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    all_feature_text += " " + elem.get_text()

        # Strategy 2: Look in entire page content
        if not all_feature_text.strip():
            all_feature_text = soup.get_text()

        # Extract using regex patterns
        text_lower = all_feature_text.lower()

        # Bedrooms
        bed_patterns = [
            r'(\d+)\s*bed(?:room)?s?',
            r'(\d+)\s*br',
            r'bed(?:room)?s?\s*(\d+)',
        ]

        for pattern in bed_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    bedrooms = int(match.group(1))
                    if 1 <= bedrooms <= 10:  # Reasonable range
                        property_details['bedrooms'] = bedrooms
                        break
                except:
                    continue

        # Bathrooms
        bath_patterns = [
            r'(\d+)\s*bath(?:room)?s?',
            r'(\d+)\s*ba',
            r'bath(?:room)?s?\s*(\d+)',
        ]

        for pattern in bath_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    bathrooms = int(match.group(1))
                    if 1 <= bathrooms <= 10:  # Reasonable range
                        property_details['bathrooms'] = bathrooms
                        break
                except:
                    continue

        # Parking/Garage
        parking_patterns = [
            r'(\d+)\s*car(?:\s*space)?s?',
            r'(\d+)\s*garage',
            r'(\d+)\s*parking',
            r'garage\s*(\d+)',
            r'parking\s*(\d+)',
        ]

        for pattern in parking_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    parking = int(match.group(1))
                    if 1 <= parking <= 10:  # Reasonable range
                        property_details['parking'] = parking
                        break
                except:
                    continue

    def extract_property_images(self, soup, property_url):
        """Extract all property images"""

        images = []

        # Image selectors
        img_selectors = [
            '.property-gallery img',
            '.image-gallery img',
            '[data-testid*="gallery"] img',
            '.property-images img',
            '.carousel img',
            'img[src*="property"]',
            'img[alt*="property" i]'
        ]

        for selector in img_selectors:
            img_elements = soup.select(selector)
            if img_elements:
                print(f"      Found {len(img_elements)} images with: {selector}")

                for img in img_elements:
                    img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

                    if img_src and not img_src.startswith('data:'):
                        # Make absolute URL
                        if img_src.startswith('/'):
                            img_src = urljoin('https://www.realestate.com.au', img_src)

                        # Validate image URL
                        if self.is_valid_image_url(img_src):
                            images.append({
                                'url': img_src,
                                'alt': img.get('alt', f'Property image'),
                                'width': img.get('width'),
                                'height': img.get('height')
                            })

                break  # Use first successful selector

        # Remove duplicates
        unique_images = []
        seen_urls = set()

        for img in images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)

        return unique_images[:15]  # Limit to 15 images

    def is_valid_image_url(self, url):
        """Check if URL is a valid image"""

        if not url:
            return False

        # Check for image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        url_lower = url.lower()

        return any(ext in url_lower for ext in image_extensions) or 'image' in url_lower

    def extract_agent_info(self, soup):
        """Extract agent/agency information"""

        agent_info = {}

        # Agent selectors
        agent_selectors = [
            '.agent-info',
            '.listing-agent',
            '[data-testid*="agent"]',
            '.property-agent',
            '.contact-agent'
        ]

        for selector in agent_selectors:
            agent_elem = soup.select_one(selector)
            if agent_elem:
                # Extract agent name
                name_elem = agent_elem.find(['h3', 'h4', 'span'], string=lambda text: text and len(text.strip()) > 3)
                if name_elem:
                    agent_info['name'] = name_elem.get_text(strip=True)

                # Extract agency
                agency_elem = agent_elem.find(string=lambda text: text and any(word in text.lower() for word in ['real estate', 'realty', 'properties']))
                if agency_elem:
                    agent_info['agency'] = agency_elem.strip()

                # Extract phone
                phone_elem = agent_elem.find(string=lambda text: text and re.search(r'\d{4}\s*\d{3}\s*\d{3}', text))
                if phone_elem:
                    agent_info['phone'] = phone_elem.strip()

                break

        return agent_info

    def extract_property_type(self, soup):
        """Extract property type (house, apartment, etc.)"""

        type_indicators = [
            ('house', ['house', 'home', 'detached']),
            ('apartment', ['apartment', 'unit', 'flat']),
            ('townhouse', ['townhouse', 'town house']),
            ('villa', ['villa']),
            ('land', ['land', 'vacant']),
        ]

        # Check page content
        page_text = soup.get_text().lower()

        for prop_type, keywords in type_indicators:
            if any(keyword in page_text for keyword in keywords):
                return prop_type

        return 'unknown'

    def extract_property_id(self, url):
        """Extract property ID from URL"""

        # realestate.com.au URL patterns
        patterns = [
            r'/property-[^-]+-[^-]+-[^-]+-(\d+)',
            r'/property/[^/]*?-(\d+)-',
            r'property/(\d+)',
            r'-(\d+)$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return f"enhanced_{random.randint(10000, 99999)}"

    def download_property_images(self, property_details):
        """Download images for a property"""

        property_id = property_details['id']
        images = property_details.get('images', [])

        if not images:
            return []

        # Create images directory
        images_dir = Path(f"data/images/{property_id}")
        images_dir.mkdir(parents=True, exist_ok=True)

        downloaded_images = []

        print(f"      📸 Downloading {len(images)} images...")

        for i, img_info in enumerate(images[:10]):  # Limit downloads
            try:
                img_url = img_info['url']

                # Download image
                img_response = requests.get(img_url, timeout=30, verify=False)

                if img_response.status_code == 200:
                    # Determine file extension
                    content_type = img_response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'  # Default

                    # Save image
                    img_filename = f"image_{i+1:03d}{ext}"
                    img_path = images_dir / img_filename

                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)

                    downloaded_images.append({
                        'url': img_url,
                        'local_path': str(img_path),
                        'filename': img_filename,
                        'size': len(img_response.content)
                    })

                    print(f"        ✅ Image {i+1}: {img_filename}")

            except Exception as e:
                print(f"        ❌ Image {i+1} error: {e}")

        return downloaded_images

    def save_enhanced_properties(self, detailed_properties):
        """Save enhanced properties with complete details"""

        if not detailed_properties:
            return 0

        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0

        for prop in detailed_properties:
            try:
                property_id = prop['id']

                # Download images
                if prop.get('images'):
                    downloaded_images = self.download_property_images(prop)
                    prop['downloaded_images'] = downloaded_images

                # Create complete property record
                complete_prop = {
                    'id': property_id,
                    'url': prop['url'],
                    'title': prop.get('title', ''),
                    'price': prop.get('price', ''),
                    'bedrooms': prop.get('bedrooms'),
                    'bathrooms': prop.get('bathrooms'),
                    'parking': prop.get('parking'),
                    'property_type': prop.get('property_type', ''),
                    'description': prop.get('description', ''),
                    'features': prop.get('features', []),
                    'images': prop.get('images', []),
                    'downloaded_images': prop.get('downloaded_images', []),
                    'agent': prop.get('agent', {}),
                    'scraped_at': prop['scraped_at'],
                    'last_updated': prop['last_updated'],
                    'method': prop['method'],
                    'status': 'active',
                    'address': {'full': prop.get('title', '')},
                    'land_size': None,
                    'building_size': None,
                    'listing_date': None
                }

                filename = f"{property_id}_enhanced.json"
                filepath = data_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(complete_prop, f, indent=2, ensure_ascii=False)

                saved_count += 1

            except Exception as e:
                print(f"Save error for {prop.get('id', 'unknown')}: {e}")

        return saved_count

    def run_enhanced_scraping(self):
        """Run complete enhanced scraping process"""

        print("🚀 ENHANCED PROPERTY SCRAPING")
        print(f"Target: {self.target_properties} properties with complete details")
        print("="*70)

        start_time = time.time()

        # Phase 1: Get property URLs
        property_urls = self.phase1_get_property_urls(max_pages=3)

        if not property_urls:
            print("❌ No property URLs found")
            return False

        # Phase 2: Get detailed information
        detailed_properties = self.phase2_get_property_details(property_urls[:self.target_properties])

        if detailed_properties:
            # Save enhanced properties
            saved_count = self.save_enhanced_properties(detailed_properties)

            total_time = time.time() - start_time

            print(f"\n🎉 ENHANCED SCRAPING COMPLETE!")
            print(f"📊 RESULTS:")
            print(f"  Properties with full details: {len(detailed_properties)}")
            print(f"  Properties saved: {saved_count}")
            print(f"  Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            print(f"  Credits used: {self.credits_used}/1000")

            if saved_count > 0:
                print(f"  Average time per property: {total_time/saved_count:.2f} seconds")
                print(f"  Credits per property: {self.credits_used/saved_count:.1f}")

            return saved_count >= (self.target_properties * 0.7)  # 70% success rate

        return False


def test_enhanced_scraping(target_properties=10):
    """Test enhanced scraping with complete details"""

    print("🧪 TESTING ENHANCED PROPERTY SCRAPING")
    print(f"Target: {target_properties} properties with complete details + images")
    print("="*70)

    # Your ScrapingBee API key
    api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"

    scraper = EnhancedPropertyScraper(api_key, target_properties)

    success = scraper.run_enhanced_scraping()

    if success:
        print(f"\n🎯 ENHANCED SCRAPING SUCCESSFUL!")
        print("Complete property details + images captured")

        # Show sample enhanced data
        print(f"\n📋 View enhanced data:")
        print(f"  python3 view_data.py")
        print(f"  ls data/images/  # View downloaded images")

        return True

    else:
        print(f"\n⚠️ Enhanced scraping needs optimization")
        return False


if __name__ == "__main__":
    import sys

    target = 10
    if len(sys.argv) > 1:
        target = int(sys.argv[1])

    success = test_enhanced_scraping(target_properties=target)

    if success:
        print(f"\n🏆 READY FOR ENHANCED 100-PROPERTY SCRAPE!")
    else:
        print(f"\n📊 Enhancement testing complete")