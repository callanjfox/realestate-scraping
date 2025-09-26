#!/usr/bin/env python3
"""
Efficient Single Request Property Scraper
Make ONE request per property, extract ALL data, save HTML for inspection
"""

from scrapingbee import ScrapingBeeClient
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


class EfficientSingleRequestScraper:
    """Extract ALL data from single ScrapingBee request"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.credits_used = 0

    def scrape_single_property_complete(self, property_url):
        """Make ONE request and extract ALL possible data"""

        print(f"🎯 EFFICIENT SINGLE-REQUEST SCRAPING")
        print(f"Property: {property_url}")
        print(f"Strategy: ONE request → Extract ALL data → Save HTML for inspection")
        print("="*70)

        # Use proven working configuration
        params = {
            'render_js': True,
            'block_resources': False,
            'stealth_proxy': True,
            'country_code': 'AU'
        }

        print(f"🐝 ScrapingBee parameters: {params}")
        print(f"💳 Expected cost: ~75 credits (stealth proxy)")

        try:
            print(f"\n📡 Making single ScrapingBee request...")
            start_time = time.time()

            response = self.client.get(property_url, params=params, timeout=120)

            request_time = time.time() - start_time
            self.credits_used += 75  # Stealth proxy cost

            print(f"⏱️ Request time: {request_time:.1f} seconds")
            print(f"📊 Status: {response.status_code}")
            print(f"📊 Content length: {len(response.content)}")
            print(f"💳 Credits used: ~{self.credits_used}")

            if response.status_code == 200:
                print("✅ SUCCESS! Property page retrieved")

                # Save HTML for inspection
                property_id = self.extract_property_id(property_url)
                html_saved = self.save_html_for_inspection(response.text, property_id)

                # Extract ALL data from this single response
                complete_data = self.extract_everything_from_html(response.text, property_url)

                if complete_data:
                    # Download images efficiently
                    if complete_data.get('images'):
                        downloaded_images = self.download_real_property_images(complete_data)
                        complete_data['downloaded_images'] = downloaded_images

                    # Save complete property data
                    saved = self.save_complete_property(complete_data)

                    if saved:
                        print(f"\n🎉 COMPLETE SINGLE-REQUEST EXTRACTION SUCCESSFUL!")
                        self.print_extraction_summary(complete_data)
                        return True, complete_data

            elif response.status_code == 500:
                print(f"❌ Server error: {response.text}")
            else:
                print(f"❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Request failed: {e}")

        return False, None

    def save_html_for_inspection(self, html_content, property_id):
        """Save HTML for offline inspection and debugging"""

        print(f"💾 Saving HTML for inspection...")

        # Create inspection directory
        inspection_dir = Path("data/html_inspection")
        inspection_dir.mkdir(parents=True, exist_ok=True)

        # Save raw HTML
        html_file = inspection_dir / f"{property_id}_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  ✅ HTML saved: {html_file}")
        print(f"  🔍 Inspect with: cat {html_file}")
        print(f"  🌐 Or open in browser for visual inspection")

        return str(html_file)

    def extract_everything_from_html(self, html_content, property_url):
        """Extract ALL possible data from single HTML response"""

        print(f"\n📝 EXTRACTING ALL DATA FROM SINGLE RESPONSE")
        print("="*50)

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            property_details = {
                'id': self.extract_property_id(property_url),
                'url': property_url,
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'method': 'efficient_single_request_scrapingbee'
            }

            # 1. TITLE/ADDRESS
            print("  🏠 Extracting title/address...")
            title = self.extract_title_comprehensive(soup)
            if title:
                property_details['title'] = title
                print(f"    ✅ {title}")

            # 2. PRICE
            print("  💰 Extracting price...")
            price = self.extract_price_comprehensive(soup)
            if price:
                property_details['price'] = price
                print(f"    ✅ {price}")

            # 3. BEDROOMS, BATHROOMS, PARKING (looking below address as you mentioned)
            print("  🛏️ Extracting bedrooms, bathrooms, parking...")
            self.extract_property_stats_below_address(soup, property_details)

            # 4. PROPERTY FEATURES (targeting specific section)
            print("  📋 Extracting Property Features section...")
            features = self.extract_property_features_section(soup)
            if features:
                property_details['features'] = features
                print(f"    ✅ {len(features)} features found")

            # 5. DESCRIPTION
            print("  📄 Extracting description...")
            description = self.extract_description_comprehensive(soup)
            if description:
                property_details['description'] = description
                print(f"    ✅ {len(description)} characters")

            # 6. REAL PROPERTY IMAGES (not UI icons)
            print("  📸 Extracting real property images...")
            images = self.extract_real_property_photos(soup)
            if images:
                property_details['images'] = images
                print(f"    ✅ {len(images)} real property images")

            # 7. AGENT INFORMATION
            print("  👤 Extracting agent information...")
            agent = self.extract_agent_comprehensive(soup)
            if agent:
                property_details['agent'] = agent
                print(f"    ✅ Agent: {agent.get('name', 'Found')}")

            # 8. PROPERTY TYPE
            property_details['property_type'] = self.determine_property_type_from_url_and_content(soup, property_url)

            return property_details

        except Exception as e:
            print(f"❌ Complete extraction failed: {e}")
            return None

    def extract_title_comprehensive(self, soup):
        """Extract title with multiple strategies"""
        selectors = [
            'h1[data-testid*="address"]',
            'h1.property-title',
            'h1',
            '.property-header h1',
            '[data-testid*="property-title"]'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 10:
                    return title
        return None

    def extract_price_comprehensive(self, soup):
        """Extract price with comprehensive selectors"""
        selectors = [
            '.property-price',
            '[data-testid*="price"]',
            '.price-wrapper',
            '.listing-price',
            '[class*="price"]'
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                price = elem.get_text(strip=True)
                if price and ('$' in price or 'auction' in price.lower() or 'contact' in price.lower()):
                    return price
        return None

    def extract_property_stats_below_address(self, soup, property_details):
        """Extract bedrooms, bathrooms, parking from area below address"""

        # Strategy 1: Look for elements immediately after address/title
        title_elem = soup.find('h1')
        if title_elem:
            # Find next elements that might contain stats
            next_elements = title_elem.find_next_siblings()
            stats_text = ""

            for elem in next_elements[:5]:  # Check next 5 elements
                stats_text += " " + elem.get_text()

            # Also check parent's next siblings
            parent = title_elem.parent
            if parent:
                for elem in parent.find_next_siblings()[:3]:
                    stats_text += " " + elem.get_text()

        else:
            stats_text = soup.get_text()

        # Strategy 2: Look for specific property stats sections
        stats_sections = [
            '.property-stats',
            '.property-info',
            '.key-features',
            '[data-testid*="features"]',
            '.listing-features'
        ]

        for selector in stats_sections:
            section = soup.select_one(selector)
            if section:
                stats_text += " " + section.get_text()

        # Extract numbers with improved patterns
        stats_lower = stats_text.lower()

        # Bedrooms - multiple patterns
        bed_patterns = [
            r'(\d+)\s*bed(?:room)?s?\b',
            r'(\d+)\s*br\b',
            r'\bbed(?:room)?s?\s*(\d+)',
        ]

        for pattern in bed_patterns:
            matches = re.findall(pattern, stats_lower)
            if matches:
                valid_beds = [int(m) for m in matches if 1 <= int(m) <= 10]
                if valid_beds:
                    property_details['bedrooms'] = valid_beds[0]
                    print(f"    ✅ Bedrooms: {valid_beds[0]}")
                    break

        # Bathrooms - enhanced patterns (user mentioned they're below address)
        bath_patterns = [
            r'(\d+)\s*bath(?:room)?s?\b',
            r'(\d+)\s*ba\b',
            r'\bbath(?:room)?s?\s*(\d+)',
            r'(\d+)\s*bathroom',
        ]

        for pattern in bath_patterns:
            matches = re.findall(pattern, stats_lower)
            if matches:
                valid_baths = [int(m) for m in matches if 1 <= int(m) <= 10]
                if valid_baths:
                    property_details['bathrooms'] = valid_baths[0]
                    print(f"    ✅ Bathrooms: {valid_baths[0]}")
                    break

        # Parking - comprehensive patterns
        parking_patterns = [
            r'(\d+)\s*car(?:\s*space)?s?\b',
            r'(\d+)\s*garage\b',
            r'(\d+)\s*parking\b',
            r'\bgarage\s*(\d+)',
            r'\bparking\s*(\d+)',
        ]

        for pattern in parking_patterns:
            matches = re.findall(pattern, stats_lower)
            if matches:
                valid_parking = [int(m) for m in matches if 1 <= int(m) <= 10]
                if valid_parking:
                    property_details['parking'] = valid_parking[0]
                    print(f"    ✅ Parking: {valid_parking[0]}")
                    break

    def extract_property_features_section(self, soup):
        """Extract from specific 'Property Features' section"""

        # Target "Property Features" section specifically
        feature_section_selectors = [
            'section:has-text("Property Features")',
            'div:has-text("Property Features")',
            'h2:contains("Property Features") + ul',
            'h3:contains("Property Features") + ul',
            '.property-features',
            '[data-testid*="features"]'
        ]

        features = []

        # Try to find Property Features section
        for selector_base in ['.property-features', '[data-testid*="features"]', '.key-features']:
            section = soup.select_one(selector_base)
            if section:
                # Look for list items
                feature_items = section.select('li, span, div')
                for item in feature_items:
                    feature_text = item.get_text(strip=True)
                    if feature_text and len(feature_text) > 2 and len(feature_text) < 100:
                        features.append(feature_text)

                if features:
                    break

        # Fallback: Look for any features list
        if not features:
            all_lists = soup.select('ul li, ol li')
            for item in all_lists:
                text = item.get_text(strip=True)
                # Filter for property-like features
                if text and any(word in text.lower() for word in
                               ['air', 'pool', 'garden', 'kitchen', 'floor', 'balcony', 'parking', 'security']):
                    features.append(text)

        return features[:20]  # Limit to 20 features

    def extract_description_comprehensive(self, soup):
        """Extract property description comprehensively"""

        desc_selectors = [
            '.property-description',
            '[data-testid*="description"]',
            '.description',
            '.property-content',
            '.listing-description',
            'section[class*="description"]',
            '.property-details .description'
        ]

        descriptions = []

        for selector in desc_selectors:
            # Try both the element itself and paragraphs within it
            elements = soup.select(f'{selector}, {selector} p')
            if elements:
                for elem in elements:
                    desc_text = elem.get_text(strip=True)
                    if desc_text and len(desc_text) > 30:  # Substantial content
                        descriptions.append(desc_text)

                if descriptions:
                    break

        return ' '.join(descriptions) if descriptions else None

    def extract_real_property_photos(self, soup):
        """Extract real property photos (not UI icons)"""

        # Target actual property image galleries
        image_gallery_selectors = [
            '.property-gallery img',
            '.image-gallery img',
            '[data-testid*="gallery"] img',
            '.property-images img',
            '.media-gallery img',
            '.photo-carousel img',
            '.property-photos img'
        ]

        real_images = []

        for selector in image_gallery_selectors:
            img_elements = soup.select(selector)
            if img_elements:
                print(f"    Testing image selector: {selector} ({len(img_elements)} images)")

                for img in img_elements:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

                    if src and self.is_real_property_photo(src):
                        if src.startswith('/'):
                            src = urljoin('https://www.realestate.com.au', src)
                        elif src.startswith('//'):
                            src = 'https:' + src

                        real_images.append({
                            'url': src,
                            'alt': img.get('alt', 'Property photo'),
                            'width': img.get('width'),
                            'height': img.get('height')
                        })

                # If we found real images with this selector, use them
                if real_images:
                    print(f"    ✅ Found {len(real_images)} real property photos")
                    break

        return real_images

    def is_real_property_photo(self, url):
        """Determine if URL is a real property photo vs UI icon"""

        if not url:
            return False

        url_lower = url.lower()

        # Exclude UI icons and placeholders
        ui_indicators = [
            'dora', 'explorer', 'phone-icon', 'placeholder', 'auth-to-enquire',
            'icon', 'logo', 'button', 'svg', 'ui', 'interface'
        ]

        # Exclude if it's clearly a UI element
        if any(indicator in url_lower for indicator in ui_indicators):
            return False

        # Include if it looks like a real photo
        photo_indicators = [
            'property', 'house', 'apartment', 'room', 'kitchen', 'bathroom',
            'bedroom', 'living', 'exterior', 'interior', 'photo', 'image',
            '.jpg', '.jpeg', '.png', '.webp'
        ]

        # Must have at least one photo indicator
        return any(indicator in url_lower for indicator in photo_indicators)

    def extract_agent_comprehensive(self, soup):
        """Extract agent info comprehensively"""

        agent_info = {}

        # Agent section selectors
        agent_selectors = [
            '.agent-info',
            '.listing-agent',
            '[data-testid*="agent"]',
            '.property-agent',
            '.contact-agent'
        ]

        for selector in agent_selectors:
            agent_section = soup.select_one(selector)
            if agent_section:
                # Agent name
                name_elem = agent_section.find(['h3', 'h4', 'h5'])
                if name_elem:
                    agent_info['name'] = name_elem.get_text(strip=True)

                # Agency
                agency_text = agent_section.get_text()
                agency_match = re.search(r'([A-Za-z\s]+(?:Real Estate|Realty|Properties))', agency_text)
                if agency_match:
                    agent_info['agency'] = agency_match.group(1).strip()

                # Phone
                phone_match = re.search(r'(\d{4}\s*\d{3}\s*\d{3})', agency_text)
                if phone_match:
                    agent_info['phone'] = phone_match.group(1)

                break

        return agent_info

    def extract_property_id(self, url):
        """Extract property ID from URL"""
        patterns = [
            r'-(\d{8,10})(?:\?|#|$)',  # 8-10 digit ID at end
            r'property-[^-]+-[^-]+-[^-]+-(\d+)',
            r'/property/[^/]*?-(\d+)-',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return f"efficient_{random.randint(100000, 999999)}"

    def determine_property_type_from_url_and_content(self, soup, url):
        """Determine property type from URL and content"""
        url_lower = url.lower()

        # Check URL first
        if 'house' in url_lower:
            return 'house'
        elif 'apartment' in url_lower or 'unit' in url_lower:
            return 'apartment'
        elif 'townhouse' in url_lower:
            return 'townhouse'

        # Check page content
        content = soup.get_text().lower()
        if 'house' in content[:1000]:  # Check first 1000 chars
            return 'house'
        elif 'apartment' in content[:1000] or 'unit' in content[:1000]:
            return 'apartment'

        return 'unknown'

    def download_real_property_images(self, property_details):
        """Download only real property images"""

        property_id = property_details['id']
        images = property_details.get('images', [])

        if not images:
            print("    ⚠️ No real property images to download")
            return []

        # Create images directory
        images_dir = Path(f"data/images/{property_id}")
        images_dir.mkdir(parents=True, exist_ok=True)

        print(f"    📸 Downloading {len(images)} real property images...")

        downloaded = []

        for i, img_info in enumerate(images):
            try:
                img_url = img_info['url']
                print(f"      Downloading {i+1}: {img_url}")

                img_response = requests.get(img_url, timeout=30, verify=False)

                if img_response.status_code == 200:
                    # Determine extension from content type or URL
                    content_type = img_response.headers.get('content-type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'  # Default

                    filename = f"property_photo_{i+1:03d}{ext}"
                    filepath = images_dir / filename

                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)

                    downloaded.append({
                        'original_url': img_url,
                        'local_path': str(filepath),
                        'filename': filename,
                        'size_bytes': len(img_response.content),
                        'content_type': content_type
                    })

                    print(f"        ✅ {filename} ({len(img_response.content):,} bytes)")

                else:
                    print(f"        ❌ Download failed: {img_response.status_code}")

            except Exception as e:
                print(f"        ❌ Image {i+1} error: {e}")

        return downloaded

    def save_complete_property(self, property_details):
        """Save complete property with all extracted data"""

        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        property_id = property_details['id']
        filename = f"{property_id}_complete_efficient.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_details, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved complete property: {filepath}")
        return True

    def print_extraction_summary(self, property_details):
        """Print summary of extracted data"""

        print(f"\n📊 EXTRACTION SUMMARY:")
        print(f"  Property ID: {property_details.get('id')}")
        print(f"  Title: {property_details.get('title', 'Missing')}")
        print(f"  Price: {property_details.get('price', 'Missing')}")
        print(f"  Bedrooms: {property_details.get('bedrooms', 'Missing')}")
        print(f"  Bathrooms: {property_details.get('bathrooms', 'Missing')}")
        print(f"  Parking: {property_details.get('parking', 'Missing')}")
        print(f"  Property Type: {property_details.get('property_type', 'Unknown')}")
        print(f"  Description: {len(property_details.get('description', ''))} characters")
        print(f"  Features: {len(property_details.get('features', []))} items")
        print(f"  Real images: {len(property_details.get('images', []))}")
        print(f"  Downloaded: {len(property_details.get('downloaded_images', []))}")
        print(f"  Agent: {property_details.get('agent', {}).get('name', 'Missing')}")

        if property_details.get('features'):
            print(f"  Sample features: {property_details['features'][:3]}")


def test_efficient_approach():
    """Test efficient single-request approach"""

    print("🚀 TESTING EFFICIENT SINGLE-REQUEST APPROACH")
    print("="*70)

    scraper = EfficientSingleRequestScraper()

    # Test with known property
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    success, details = scraper.scrape_single_property_complete(test_url)

    if success:
        print(f"\n🎯 READY TO INSPECT YOUR DATA:")
        print(f"  Property JSON: cat data/properties/{details['id']}_complete_efficient.json")
        print(f"  HTML for debugging: cat data/html_inspection/{details['id']}_page.html")
        print(f"  Images: ls data/images/{details['id']}/")

        return True

    return False


if __name__ == "__main__":
    success = test_efficient_approach()

    if success:
        print(f"\n🏆 EFFICIENT EXTRACTION SUCCESSFUL!")
        print("Ready to debug and perfect the selectors")
    else:
        print(f"\n⚠️ Need to troubleshoot efficient approach")