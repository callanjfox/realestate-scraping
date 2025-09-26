#!/usr/bin/env python3
"""
Single Property Perfection - Complete Details + Images
Focus: Perfect the extraction of all details from ONE property page efficiently
"""

import time
import json
import requests
from pathlib import Path
from datetime import datetime, timezone
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


class SinglePropertyPerfection:
    """Perfect single property extraction for maximum detail and credit efficiency"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.credits_used = 0

    def test_credit_efficient_parameters(self):
        """Test different parameter combinations for credit efficiency"""

        print("💳 TESTING CREDIT-EFFICIENT PARAMETERS")
        print("JS rendering = 5 credits, Premium proxy = 10 credits")
        print("="*60)

        # Use one of our known working property URLs
        test_property_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

        # Test different parameter combinations
        parameter_sets = [
            {
                'name': 'Basic (1 credit)',
                'params': {'country_code': 'AU'},
                'expected_credits': 1
            },
            {
                'name': 'JS Only (5 credits)',
                'params': {'render_js': True, 'country_code': 'AU'},
                'expected_credits': 5
            },
            {
                'name': 'Premium Proxy (10 credits)',
                'params': {'premium_proxy': True, 'country_code': 'AU'},
                'expected_credits': 10
            },
            {
                'name': 'JS + Premium (15 credits)',
                'params': {'render_js': True, 'premium_proxy': True, 'country_code': 'AU'},
                'expected_credits': 15
            }
        ]

        working_configs = []

        for config in parameter_sets:
            print(f"\n🧪 Testing: {config['name']} (Expected: {config['expected_credits']} credits)")

            try:
                credits_before = self.credits_used

                response = self.client.get(
                    test_property_url,
                    params=config['params'],
                    timeout=90
                )

                credits_after = self.credits_used + 1  # Estimate
                actual_credits = credits_after - credits_before

                print(f"  Status: {response.status_code}")
                print(f"  Content length: {len(response.content)}")
                print(f"  Estimated credits used: {actual_credits}")

                if response.status_code == 200:
                    # Quick content quality check
                    content = response.text.lower()
                    quality_indicators = ['bedroom', 'bathroom', 'description', 'agent', 'features']
                    found_indicators = [ind for ind in quality_indicators if ind in content]

                    print(f"  Quality indicators: {found_indicators}")

                    if len(found_indicators) >= 3:
                        print(f"  ✅ HIGH QUALITY CONTENT!")
                        working_configs.append({
                            'config': config,
                            'response': response,
                            'quality_score': len(found_indicators)
                        })
                    else:
                        print(f"  ⚠️ Low quality content")

                elif response.status_code == 429:
                    print(f"  ❌ Rate limited")
                else:
                    print(f"  ❌ Failed: {response.status_code}")

                self.credits_used += actual_credits

            except Exception as e:
                print(f"  ❌ Error: {e}")

            # Small delay between tests
            time.sleep(3)

        # Choose optimal configuration
        if working_configs:
            # Sort by quality score vs cost ratio
            working_configs.sort(key=lambda x: x['quality_score'] / x['config']['expected_credits'], reverse=True)

            best_config = working_configs[0]
            print(f"\n🎯 OPTIMAL CONFIGURATION:")
            print(f"  Name: {best_config['config']['name']}")
            print(f"  Parameters: {best_config['config']['params']}")
            print(f"  Quality score: {best_config['quality_score']}/5")
            print(f"  Credit efficiency: {best_config['quality_score'] / best_config['config']['expected_credits']:.2f}")

            return best_config

        return None

    def extract_complete_property_details(self, html_content, property_url):
        """Extract ALL possible details from individual property page"""

        print("📝 EXTRACTING COMPLETE PROPERTY DETAILS")
        print("="*50)

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Initialize property details
            property_details = {
                'id': self.extract_property_id(property_url),
                'url': property_url,
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'method': 'single_property_perfection_scrapingbee'
            }

            # 1. TITLE/ADDRESS - Multiple strategies
            print("  🏠 Extracting title/address...")
            title_selectors = [
                'h1[data-testid*="address"]',
                'h1.property-title',
                'h1',
                '.property-header h1',
                '[data-testid*="property-title"]'
            ]

            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        property_details['title'] = title
                        print(f"    ✅ Title: {title}")
                        break

            # 2. PRICE - Comprehensive extraction
            print("  💰 Extracting price...")
            price_selectors = [
                '.property-price',
                '[data-testid*="price"]',
                '.price-wrapper',
                '.listing-price',
                '[class*="price"]'
            ]

            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text and ('$' in price_text or 'auction' in price_text.lower() or 'contact' in price_text.lower()):
                        property_details['price'] = price_text
                        print(f"    ✅ Price: {price_text}")
                        break

            # 3. BEDROOMS, BATHROOMS, PARKING - Comprehensive search
            print("  🛏️ Extracting bedrooms, bathrooms, parking...")
            self.extract_property_features_comprehensive(soup, property_details)

            # 4. DESCRIPTION - Multiple strategies
            print("  📄 Extracting description...")
            description_selectors = [
                '.property-description',
                '[data-testid*="description"]',
                '.description',
                '.property-content',
                '.listing-description',
                'section[class*="description"]'
            ]

            descriptions = []
            for selector in description_selectors:
                desc_elements = soup.select(f'{selector} p, {selector}')
                if desc_elements:
                    for elem in desc_elements:
                        desc_text = elem.get_text(strip=True)
                        if desc_text and len(desc_text) > 20:
                            descriptions.append(desc_text)

                    if descriptions:
                        break

            if descriptions:
                full_description = ' '.join(descriptions)
                property_details['description'] = full_description
                print(f"    ✅ Description: {len(full_description)} characters")
            else:
                print(f"    ⚠️ No description found")

            # 5. FEATURES LIST
            print("  📋 Extracting features...")
            features = self.extract_feature_list(soup)
            if features:
                property_details['features'] = features
                print(f"    ✅ Features: {len(features)} items")

            # 6. IMAGES - Comprehensive extraction
            print("  📸 Extracting images...")
            images = self.extract_all_images(soup, property_url)
            if images:
                property_details['images'] = images
                print(f"    ✅ Images: {len(images)} found")

            # 7. AGENT INFORMATION
            print("  👤 Extracting agent info...")
            agent_info = self.extract_agent_information(soup)
            if agent_info:
                property_details['agent'] = agent_info
                print(f"    ✅ Agent: {agent_info.get('name', 'Unknown')}")

            # 8. PROPERTY TYPE
            property_details['property_type'] = self.determine_property_type(soup, property_url)

            return property_details

        except Exception as e:
            print(f"❌ Complete extraction failed: {e}")
            return None

    def extract_property_features_comprehensive(self, soup, property_details):
        """Comprehensive extraction of bedrooms, bathrooms, parking"""

        # Get all text content for analysis
        page_text = soup.get_text().lower()

        # Enhanced regex patterns for bedrooms
        bedroom_patterns = [
            r'(\d+)\s*bed(?:room)?s?(?:\s|,|$)',
            r'(\d+)\s*br(?:\s|,|$)',
            r'bed(?:room)?s?\s*(\d+)',
            r'(\d+)(?:\s*-\s*\d+)?\s*bed',
        ]

        for pattern in bedroom_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                try:
                    # Take the most common number or first valid one
                    bedroom_counts = [int(m) for m in matches if 1 <= int(m) <= 10]
                    if bedroom_counts:
                        property_details['bedrooms'] = bedroom_counts[0]
                        print(f"    ✅ Bedrooms: {bedroom_counts[0]}")
                        break
                except:
                    continue

        # Enhanced regex patterns for bathrooms
        bathroom_patterns = [
            r'(\d+)\s*bath(?:room)?s?(?:\s|,|$)',
            r'(\d+)\s*ba(?:\s|,|$)',
            r'bath(?:room)?s?\s*(\d+)',
            r'(\d+)(?:\s*-\s*\d+)?\s*bath',
        ]

        for pattern in bathroom_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                try:
                    bathroom_counts = [int(m) for m in matches if 1 <= int(m) <= 10]
                    if bathroom_counts:
                        property_details['bathrooms'] = bathroom_counts[0]
                        print(f"    ✅ Bathrooms: {bathroom_counts[0]}")
                        break
                except:
                    continue

        # Enhanced regex patterns for parking
        parking_patterns = [
            r'(\d+)\s*car(?:\s*space)?s?(?:\s|,|$)',
            r'(\d+)\s*garage(?:\s|,|$)',
            r'(\d+)\s*parking(?:\s*space)?s?(?:\s|,|$)',
            r'garage\s*(\d+)',
            r'parking\s*(\d+)',
        ]

        for pattern in parking_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                try:
                    parking_counts = [int(m) for m in matches if 1 <= int(m) <= 10]
                    if parking_counts:
                        property_details['parking'] = parking_counts[0]
                        print(f"    ✅ Parking: {parking_counts[0]}")
                        break
                except:
                    continue

    def extract_feature_list(self, soup):
        """Extract list of property features"""

        feature_selectors = [
            '.property-features li',
            '.features li',
            '[data-testid*="features"] li',
            '.key-features li',
            'ul[class*="feature"] li',
            '.property-info li'
        ]

        features = []
        for selector in feature_selectors:
            feature_elements = soup.select(selector)
            if feature_elements:
                features = [elem.get_text(strip=True) for elem in feature_elements
                           if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 3]
                if features:
                    break

        return features[:15]  # Limit to 15 features

    def extract_all_images(self, soup, property_url):
        """Extract all property images with comprehensive selectors"""

        images = []

        # Image selectors ordered by priority
        img_selectors = [
            '.property-gallery img',
            '.image-gallery img',
            '[data-testid*="gallery"] img',
            '.property-images img',
            '.media-gallery img',
            '.photo-gallery img',
            'img[src*="property"]',
            'img[alt*="property" i]',
            'img[src*="images"]'
        ]

        for selector in img_selectors:
            img_elements = soup.select(selector)
            if img_elements:
                print(f"    Using image selector: {selector} ({len(img_elements)} images)")

                for img in img_elements:
                    img_src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

                    if img_src and not img_src.startswith('data:'):
                        # Make absolute URL
                        if img_src.startswith('/'):
                            img_src = urljoin('https://www.realestate.com.au', img_src)
                        elif img_src.startswith('//'):
                            img_src = 'https:' + img_src

                        # Validate image URL
                        if self.is_valid_property_image(img_src):
                            images.append({
                                'url': img_src,
                                'alt': img.get('alt', 'Property image'),
                                'width': img.get('width'),
                                'height': img.get('height'),
                                'title': img.get('title', '')
                            })

                break  # Use first successful selector

        # Remove duplicates
        unique_images = []
        seen_urls = set()

        for img in images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)

        return unique_images

    def is_valid_property_image(self, url):
        """Validate if URL is a property image"""

        if not url or len(url) < 10:
            return False

        # Check for image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        url_lower = url.lower()

        # Must have image extension or be from image domain
        has_extension = any(ext in url_lower for ext in image_extensions)
        is_image_domain = any(domain in url_lower for domain in ['images', 'photos', 'media', 'cdn'])

        # Exclude common non-property images
        exclude_keywords = ['logo', 'icon', 'avatar', 'thumbnail', 'watermark']
        is_excluded = any(keyword in url_lower for keyword in exclude_keywords)

        return (has_extension or is_image_domain) and not is_excluded

    def extract_agent_information(self, soup):
        """Extract agent/agency contact information"""

        agent_info = {}

        # Agent selectors
        agent_selectors = [
            '.agent-info',
            '.listing-agent',
            '[data-testid*="agent"]',
            '.property-agent',
            '.contact-agent',
            '.agent-details'
        ]

        agent_section = None
        for selector in agent_selectors:
            section = soup.select_one(selector)
            if section:
                agent_section = section
                break

        if agent_section:
            # Extract agent name
            name_patterns = [
                agent_section.find(['h3', 'h4', 'h5']),
                agent_section.find('span', class_=lambda x: x and 'name' in x),
                agent_section.find(string=lambda text: text and
                                 len(text.strip()) > 5 and len(text.strip()) < 50 and
                                 not any(word in text.lower() for word in ['agency', 'real estate', 'phone', 'email']))
            ]

            for pattern in name_patterns:
                if pattern:
                    if hasattr(pattern, 'get_text'):
                        name = pattern.get_text(strip=True)
                    else:
                        name = str(pattern).strip()

                    if name and 5 <= len(name) <= 50:
                        agent_info['name'] = name
                        break

            # Extract agency
            agency_elem = agent_section.find(string=lambda text: text and
                                           any(word in text.lower() for word in ['real estate', 'realty', 'properties', 'agency']))
            if agency_elem:
                agent_info['agency'] = agency_elem.strip()

            # Extract phone
            phone_elem = agent_section.find(string=lambda text: text and
                                          re.search(r'\(?\d{2,4}\)?\s*\d{3,4}\s*\d{3,4}', text))
            if phone_elem:
                phone_match = re.search(r'\(?\d{2,4}\)?\s*\d{3,4}\s*\d{3,4}', phone_elem)
                if phone_match:
                    agent_info['phone'] = phone_match.group(0)

        return agent_info

    def determine_property_type(self, soup, property_url):
        """Determine property type from page content and URL"""

        # Check URL for type indicators
        url_lower = property_url.lower()
        if 'house' in url_lower:
            return 'house'
        elif 'apartment' in url_lower or 'unit' in url_lower:
            return 'apartment'
        elif 'townhouse' in url_lower:
            return 'townhouse'

        # Check page content
        page_text = soup.get_text().lower()
        type_keywords = {
            'house': ['house', 'home', 'detached'],
            'apartment': ['apartment', 'unit', 'flat'],
            'townhouse': ['townhouse', 'town house'],
            'villa': ['villa'],
            'land': ['land', 'vacant']
        }

        for prop_type, keywords in type_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                return prop_type

        return 'unknown'

    def download_property_images(self, property_details):
        """Download all images for the property"""

        property_id = property_details['id']
        images = property_details.get('images', [])

        if not images:
            print("    ⚠️ No images to download")
            return []

        # Create property-specific image directory
        images_dir = Path(f"data/images/{property_id}")
        images_dir.mkdir(parents=True, exist_ok=True)

        print(f"    📸 Downloading {len(images)} images to {images_dir}...")

        downloaded_images = []

        for i, img_info in enumerate(images):
            try:
                img_url = img_info['url']
                print(f"      Image {i+1}: {img_url}")

                # Download image
                img_response = requests.get(img_url, timeout=30, verify=False)

                if img_response.status_code == 200:
                    # Determine file extension
                    content_type = img_response.headers.get('content-type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        # Try to get from URL
                        parsed_url = urlparse(img_url)
                        if parsed_url.path:
                            url_ext = Path(parsed_url.path).suffix.lower()
                            if url_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
                                ext = url_ext
                            else:
                                ext = '.jpg'  # Default
                        else:
                            ext = '.jpg'

                    # Save image
                    img_filename = f"image_{i+1:03d}{ext}"
                    img_path = images_dir / img_filename

                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)

                    downloaded_images.append({
                        'original_url': img_url,
                        'local_path': str(img_path),
                        'filename': img_filename,
                        'size_bytes': len(img_response.content),
                        'content_type': content_type
                    })

                    print(f"        ✅ Downloaded: {img_filename} ({len(img_response.content)} bytes)")

                else:
                    print(f"        ❌ Download failed: {img_response.status_code}")

            except Exception as e:
                print(f"        ❌ Image {i+1} error: {e}")

        print(f"    📊 Successfully downloaded: {len(downloaded_images)}/{len(images)} images")
        return downloaded_images

    def extract_property_id(self, url):
        """Extract property ID from URL"""

        patterns = [
            r'/property-[^-]+-[^-]+-[^-]+-(\d+)',
            r'/property/[^/]*?-(\d+)-',
            r'property/(\d+)',
            r'-(\d+)(?:\?|#|$)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return f"single_perfect_{random.randint(10000, 99999)}"

    def save_perfect_property(self, property_details):
        """Save perfectly extracted property"""

        if not property_details:
            return False

        property_id = property_details['id']

        # Create complete property record
        complete_property = {
            'id': property_id,
            'url': property_details['url'],
            'title': property_details.get('title', ''),
            'price': property_details.get('price', ''),
            'bedrooms': property_details.get('bedrooms'),
            'bathrooms': property_details.get('bathrooms'),
            'parking': property_details.get('parking'),
            'property_type': property_details.get('property_type', ''),
            'description': property_details.get('description', ''),
            'features': property_details.get('features', []),
            'images': property_details.get('images', []),
            'downloaded_images': property_details.get('downloaded_images', []),
            'agent': property_details.get('agent', {}),
            'scraped_at': property_details['scraped_at'],
            'last_updated': property_details['scraped_at'],
            'method': 'single_property_perfection_complete',
            'service': 'scrapingbee_optimized',
            'status': 'active',
            'address': {'full': property_details.get('title', '')},
            'land_size': None,
            'building_size': None,
            'listing_date': None
        }

        # Save to JSON
        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{property_id}_perfect.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_property, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved complete property: {filepath}")
        return True

    def test_single_property_perfection(self, property_url):
        """Test complete extraction on single property"""

        print(f"🎯 TESTING SINGLE PROPERTY PERFECTION")
        print(f"Target: {property_url}")
        print("="*70)

        # First test optimal parameters
        optimal_config = self.test_credit_efficient_parameters()

        if not optimal_config:
            print("❌ No working configuration found")
            return False

        print(f"\n🏠 SCRAPING COMPLETE PROPERTY DETAILS")
        print(f"Using: {optimal_config['config']['name']}")
        print("="*50)

        try:
            # Get complete property details
            property_details = self.extract_complete_property_details(
                optimal_config['response'].text,
                property_url
            )

            if property_details:
                # Download images
                if property_details.get('images'):
                    downloaded_images = self.download_property_images(property_details)
                    property_details['downloaded_images'] = downloaded_images

                # Save complete property
                save_success = self.save_perfect_property(property_details)

                if save_success:
                    print(f"\n🎉 SINGLE PROPERTY PERFECTION COMPLETE!")
                    print(f"📊 EXTRACTED DATA:")
                    print(f"  Title: {property_details.get('title', 'Missing')}")
                    print(f"  Price: {property_details.get('price', 'Missing')}")
                    print(f"  Bedrooms: {property_details.get('bedrooms', 'Missing')}")
                    print(f"  Bathrooms: {property_details.get('bathrooms', 'Missing')}")
                    print(f"  Parking: {property_details.get('parking', 'Missing')}")
                    print(f"  Description: {len(property_details.get('description', ''))} characters")
                    print(f"  Features: {len(property_details.get('features', []))} items")
                    print(f"  Images: {len(property_details.get('images', []))} found")
                    print(f"  Downloaded: {len(property_details.get('downloaded_images', []))} images")
                    print(f"  Agent: {property_details.get('agent', {}).get('name', 'Missing')}")

                    print(f"\n💳 Credits used: {self.credits_used}")

                    return True

        except Exception as e:
            print(f"❌ Single property perfection failed: {e}")

        return False


def run_single_property_test():
    """Run single property perfection test"""

    print("🚀 SINGLE PROPERTY PERFECTION TEST")
    print("Focus: Extract ALL details from ONE property efficiently")
    print("="*70)

    # Use a known working property URL from our previous results
    test_property_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    scraper = SinglePropertyPerfection()

    success = scraper.test_single_property_perfection(test_property_url)

    if success:
        print(f"\n✅ SINGLE PROPERTY PERFECTION SUCCESSFUL!")
        print("Ready to test second property")

        # Test second property
        print(f"\n🔄 TESTING SECOND PROPERTY...")
        second_url = "https://www.realestate.com.au/property-apartment-qld-south+bank-148928524"

        second_success = scraper.test_single_property_perfection(second_url)

        if second_success:
            print(f"\n🎯 TWO PROPERTY PERFECTION COMPLETE!")
            print("Approach validated - ready for scaling")

            print(f"\n📋 VIEW YOUR PERFECT DATA:")
            print(f"  python3 view_data.py 5")
            print(f"  ls data/images/  # Check downloaded images")
            print(f"  cat data/properties/*_perfect.json  # View complete JSON")

            return True

    return False


if __name__ == "__main__":
    success = run_single_property_test()

    if success:
        print(f"\n🏆 PROPERTY PERFECTION ACHIEVED!")
        print("Complete details + images extraction validated")
    else:
        print(f"\n⚠️ Property perfection needs optimization")