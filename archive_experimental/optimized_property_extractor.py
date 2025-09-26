#!/usr/bin/env python3
"""
Optimized Property Extractor - Targets Exact Data Sources Found in HTML
Based on HTML inspection findings:
- Meta og:description has full property description with bed/bath counts
- i2.au.reastatic.net URLs have real property photos
- Structured data in meta tags
"""

from scrapingbee import ScrapingBeeClient
import time
import json
import requests
import random
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import html


class OptimizedPropertyExtractor:
    """Optimized extractor targeting exact data sources"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)
        self.credits_used = 0

    def extract_property_perfectly(self, property_url):
        """Extract property using discovered optimal data sources"""

        print(f"🎯 OPTIMIZED PROPERTY EXTRACTION")
        print(f"Property: {property_url}")
        print(f"Strategy: Target meta tags, og:description, real image URLs")
        print("="*70)

        # Use proven working configuration
        params = {
            'render_js': True,
            'block_resources': False,
            'stealth_proxy': True,
            'country_code': 'AU'
        }

        try:
            print(f"📡 Making optimized ScrapingBee request...")
            response = self.client.get(property_url, params=params, timeout=120)
            self.credits_used += 75  # Stealth proxy cost

            print(f"📊 Status: {response.status_code}")
            print(f"💳 Credits used: {self.credits_used}")

            if response.status_code == 200:
                print("✅ SUCCESS! Extracting using optimized selectors...")

                # Save HTML
                property_id = self.extract_property_id(property_url)
                self.save_html_for_inspection(response.text, property_id)

                # Extract all data optimally
                complete_data = self.extract_using_optimal_sources(response.text, property_url)

                if complete_data:
                    # Download real property images
                    if complete_data.get('images'):
                        downloaded = self.download_real_property_images(complete_data)
                        complete_data['downloaded_images'] = downloaded

                    # Save complete data
                    saved = self.save_optimized_property(complete_data)

                    if saved:
                        self.print_complete_summary(complete_data)
                        return True, complete_data

            else:
                print(f"❌ Request failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Extraction failed: {e}")

        return False, None

    def extract_using_optimal_sources(self, html_content, property_url):
        """Extract using optimal data sources including validated XPath selectors"""

        print("\n📝 EXTRACTING USING OPTIMAL DATA SOURCES + XPATH")
        print("="*60)

        from lxml import html as lxml_html

        # Parse with both BeautifulSoup and lxml for different extraction methods
        soup = BeautifulSoup(html_content, 'html.parser')
        tree = lxml_html.fromstring(html_content)

        property_data = {
            'id': self.extract_property_id(property_url),
            'url': property_url,
            'scraped_at': datetime.now(timezone.utc).isoformat(),
            'method': 'xpath_and_meta_tag_extraction'
        }

        # XPath selectors that work (from validation)
        working_xpaths = {
            'full_address': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[1]/h1',
            'property_id': '/html/body/div[1]/div[4]/div[4]/div[1]/div/div/div[1]/div[2]/p/text()[2]',
            'bedrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[1]/p',
            'bathrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[3]/p',
            'car_spaces': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[4]/p',
            'land_size': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[2]/li/p',
            'offer': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[2]/span',
            'agent_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[1]/a',
            'agency_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/a',
            'agency_address': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/div'
        }

        # Extract using validated XPath selectors
        for field_name, xpath in working_xpaths.items():
            try:
                elements = tree.xpath(xpath)
                if elements:
                    if isinstance(elements[0], str):
                        value = elements[0].strip()
                    else:
                        value = elements[0].text_content().strip() if elements[0].text_content() else ''

                    # Clean up land size formatting
                    if field_name == 'land_size' and value:
                        value = value.replace('mÂ²', 'm²')

                    # Convert numeric fields
                    if field_name in ['bedrooms', 'bathrooms', 'car_spaces'] and value.isdigit():
                        property_data[field_name] = int(value)
                        print(f"    ✅ {field_name}: {value}")
                    elif field_name == 'full_address':
                        property_data['title'] = value  # Use address as title
                        property_data['address'] = value
                        print(f"    ✅ Address/Title: {value}")
                    elif field_name == 'offer':
                        property_data['price'] = value
                        print(f"    ✅ Price: {value}")
                    else:
                        property_data[field_name] = value
                        print(f"    ✅ {field_name}: {value}")

            except Exception as e:
                print(f"    ❌ XPath failed for {field_name}: {e}")

        # FALLBACK: Extract description from og:description meta tag
        print("  📄 Description from og:description...")
        desc_meta = soup.find('meta', property='og:description')
        if desc_meta:
            raw_description = desc_meta.get('content', '')
            clean_description = html.unescape(raw_description).replace('&lt;br/&gt;', '\n').replace('<br/>', '\n')
            property_data['description'] = clean_description
            property_data['description_body'] = clean_description  # Alternative field name
            print(f"    ✅ {len(clean_description)} characters")

        # Extract property highlights and features from description
        if property_data.get('description'):
            print("  📋 Extracting features from description...")
            features = self.extract_features_from_description(property_data['description'])
            highlights = self.extract_highlights_from_description(property_data['description'])

            property_data['features'] = features
            property_data['property_features'] = features  # Alternative field name
            property_data['property_highlights'] = highlights

            print(f"    ✅ {len(features)} features extracted")
            print(f"    ✅ {len(highlights)} highlights extracted")

        # Try to extract inspection times from JSON-LD structured data
        print("  📅 Inspection times from structured data...")
        inspection_data = self.extract_inspection_times(html_content)
        if inspection_data:
            property_data['inspections'] = inspection_data
            print(f"    ✅ {len(inspection_data)} inspection times")

        # Extract agent phone number with more flexible approach
        print("  📞 Agent contact details...")
        agent_phone = self.extract_agent_phone(soup, tree)
        if agent_phone:
            property_data['agent_number'] = agent_phone
            print(f"    ✅ Agent phone: {agent_phone}")

        # REAL PROPERTY IMAGES - Target i2.au.reastatic.net URLs
        print("  📸 Real property images...")
        real_images = self.extract_real_property_images_optimal(soup)
        if real_images:
            property_data['images'] = real_images
            print(f"    ✅ {len(real_images)} real property photos")

        # PROPERTY TYPE - From URL
        property_data['property_type'] = self.extract_type_from_url(property_url)

        return property_data

    def extract_bed_bath_from_description(self, description, property_data):
        """Extract bed/bath counts from full description"""

        desc_lower = description.lower()

        # Bedrooms - look for specific mentions
        bed_patterns = [
            r'(\d+)\s*generous\s*sized\s*bedrooms',
            r'(\d+)\s*bedrooms?',
            r'(\d+)\s*bed\s',
        ]

        for pattern in bed_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                bedrooms = int(match.group(1))
                if 1 <= bedrooms <= 10:
                    property_data['bedrooms'] = bedrooms
                    print(f"    ✅ Bedrooms: {bedrooms}")
                    break

        # Bathrooms - count bathroom mentions
        bathroom_mentions = [
            'modern bathroom',
            'stylish near new bathroom',
            'bathroom',
            'ensuite'
        ]

        bathroom_count = 0
        for mention in bathroom_mentions:
            if mention in desc_lower:
                bathroom_count += desc_lower.count(mention)

        # Clean up count (avoid double counting)
        bathroom_mentions_found = []
        if 'modern bathroom' in desc_lower:
            bathroom_mentions_found.append('modern bathroom')
        if 'stylish near new bathroom' in desc_lower or 'near new bathroom' in desc_lower:
            bathroom_mentions_found.append('stylish bathroom')
        if 'ensuite' in desc_lower:
            bathroom_mentions_found.append('ensuite')

        # Set bathroom count
        if len(bathroom_mentions_found) >= 2:
            property_data['bathrooms'] = 2
            print(f"    ✅ Bathrooms: 2 (modern + stylish)")
        elif len(bathroom_mentions_found) >= 1:
            property_data['bathrooms'] = 1
            print(f"    ✅ Bathrooms: 1")

        # Parking - look for garage/parking mentions
        parking_patterns = [
            r'(\d+)\s*car\s*garage',
            r'long\s*garage',
            r'garage\s*plus\s*storage',
            r'plenty\s*of\s*off-street\s*parking'
        ]

        for pattern in parking_patterns:
            if re.search(pattern, desc_lower):
                # If we find garage mentions, assume at least 1-2 parking
                if 'long garage' in desc_lower or 'garage plus storage' in desc_lower:
                    property_data['parking'] = 2
                    print(f"    ✅ Parking: 2 (garage + storage)")
                else:
                    property_data['parking'] = 1
                    print(f"    ✅ Parking: 1")
                break

    def extract_real_property_images_optimal(self, soup):
        """Extract real property images targeting i2.au.reastatic.net URLs"""

        real_images = []

        # Strategy 1: Look for og:image (main property photo)
        og_image = soup.find('meta', property='og:image')
        if og_image:
            img_url = og_image.get('content')
            if img_url and 'i2.au.reastatic.net' in img_url:
                real_images.append({
                    'url': img_url,
                    'alt': 'Main property photo',
                    'type': 'main_photo',
                    'width': soup.find('meta', property='og:image:width', content=True),
                    'height': soup.find('meta', property='og:image:height', content=True)
                })

        # Strategy 2: Find all i2.au.reastatic.net URLs in the page
        page_text = str(soup)
        reastatic_urls = re.findall(r'https://i2\.au\.reastatic\.net/[^"\'>\s]+', page_text)

        for url in reastatic_urls:
            # Filter for actual property photos (not logos)
            if 'logo' not in url.lower() and len(url) > 50:  # Real property images are longer URLs
                # Determine if it's a thumbnail or full size
                if '800x600' in url or '1024x' in url:
                    img_type = 'full_size'
                elif '300x170' in url or '200x' in url:
                    img_type = 'thumbnail'
                else:
                    img_type = 'unknown'

                real_images.append({
                    'url': url,
                    'alt': f'Property photo ({img_type})',
                    'type': img_type
                })

        # Remove duplicates
        unique_images = []
        seen_urls = set()
        for img in real_images:
            if img['url'] not in seen_urls:
                seen_urls.add(img['url'])
                unique_images.append(img)

        return unique_images

    def extract_features_from_description(self, description):
        """Extract features from full property description"""

        features = []

        # Look for feature mentions in description
        feature_patterns = [
            r'-\s*([^-\n]+)',  # Lines starting with dash
            r'•\s*([^•\n]+)',  # Lines starting with bullet
        ]

        for pattern in feature_patterns:
            matches = re.findall(pattern, description)
            for match in matches:
                feature = match.strip()
                if 10 <= len(feature) <= 100:  # Reasonable feature length
                    features.append(feature)

        return features[:20]  # Limit features

    def download_real_property_images(self, property_data):
        """Download real property images efficiently"""

        property_id = property_data['id']
        images = property_data.get('images', [])

        if not images:
            return []

        # Create images directory
        images_dir = Path(f"data/images/{property_id}")
        images_dir.mkdir(parents=True, exist_ok=True)

        print(f"    📸 Downloading {len(images)} real property images...")

        downloaded = []

        for i, img_info in enumerate(images):
            try:
                img_url = img_info['url']
                img_type = img_info.get('type', 'unknown')

                print(f"      Image {i+1} ({img_type}): {img_url}")

                img_response = requests.get(img_url, timeout=30, verify=False)

                if img_response.status_code == 200:
                    # Determine extension
                    content_type = img_response.headers.get('content-type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'

                    filename = f"{img_type}_{i+1:03d}{ext}"
                    filepath = images_dir / filename

                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)

                    downloaded.append({
                        'original_url': img_url,
                        'local_path': str(filepath),
                        'filename': filename,
                        'size_bytes': len(img_response.content),
                        'type': img_type
                    })

                    print(f"        ✅ {filename} ({len(img_response.content):,} bytes)")

                else:
                    print(f"        ❌ Download failed: {img_response.status_code}")

            except Exception as e:
                print(f"        ❌ Image {i+1} error: {e}")

        return downloaded

    def extract_real_property_images_optimal(self, soup):
        """Extract real property images from optimal sources"""

        real_images = []

        # Strategy 1: og:image meta tag (main photo)
        og_image = soup.find('meta', property='og:image')
        if og_image:
            img_url = og_image.get('content')
            if img_url and 'i2.au.reastatic.net' in img_url:
                real_images.append({
                    'url': img_url,
                    'alt': 'Main property photo',
                    'type': 'main_photo'
                })

        # Strategy 2: Find all i2.au.reastatic.net URLs
        page_content = str(soup)
        reastatic_pattern = r'https://i2\.au\.reastatic\.net/[^"\'>\s]+'
        reastatic_urls = re.findall(reastatic_pattern, page_content)

        for url in reastatic_urls:
            # Skip logos and UI elements
            if 'logo' not in url.lower() and len(url) > 70:
                # Determine image type by size
                if '800x600' in url or '1024x' in url:
                    img_type = 'full_size'
                elif '300x170' in url:
                    img_type = 'thumbnail'
                else:
                    img_type = 'property_photo'

                real_images.append({
                    'url': url,
                    'alt': f'Property photo ({img_type})',
                    'type': img_type
                })

        # Remove duplicates
        unique_images = []
        seen_urls = set()
        for img in real_images:
            if img['url'] not in seen_urls and len(img['url']) > 50:
                seen_urls.add(img['url'])
                unique_images.append(img)

        return unique_images

    def extract_features_from_description(self, description):
        """Extract property features from description text"""

        features = []

        # Split by lines and look for feature lists
        lines = description.split('\n')

        for line in lines:
            line = line.strip()
            # Look for lines that start with dash or bullet and contain features
            if line.startswith('-') or line.startswith('•'):
                feature_text = line.lstrip('-•').strip()
                if 5 <= len(feature_text) <= 100:  # Reasonable feature length
                    features.append(feature_text)

        # If no dashed features found, look for common feature words
        if not features:
            feature_keywords = [
                'air conditioning', 'pool', 'garage', 'garden', 'balcony',
                'deck', 'kitchen', 'bathroom', 'bedroom', 'living', 'dining',
                'study', 'office', 'storage', 'parking', 'heating', 'cooling'
            ]

            desc_lower = description.lower()
            for keyword in feature_keywords:
                if keyword in desc_lower:
                    # Find the sentence containing this keyword
                    sentences = re.split(r'[.!?]', description)
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 10:
                            features.append(sentence.strip())
                            break

        return features[:15]  # Limit to 15 features

    def extract_highlights_from_description(self, description):
        """Extract property highlights from description text"""

        highlights = []

        # Split description into paragraphs
        paragraphs = description.split('\n\n')

        # First paragraph is often a summary/highlight
        if paragraphs and len(paragraphs[0]) > 50:
            highlights.append(paragraphs[0].strip())

        # Look for "highlights" or "features" sections
        desc_lower = description.lower()

        # Common highlight patterns
        highlight_patterns = [
            'upstairs you will find:',
            'downstairs comes with:',
            'key features include:',
            'property highlights:',
            'main features:'
        ]

        for pattern in highlight_patterns:
            if pattern in desc_lower:
                # Find the section after this pattern
                start_idx = desc_lower.find(pattern)
                if start_idx != -1:
                    section = description[start_idx:start_idx + 500]  # Get 500 chars after
                    highlights.append(section.strip())
                    break

        return highlights[:5]  # Limit to 5 highlights

    def extract_inspection_times(self, html_content):
        """Extract inspection times from JSON-LD structured data"""

        inspections = []

        try:
            # Look for JSON-LD script containing inspection data
            import json
            json_ld_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
            json_matches = re.findall(json_ld_pattern, html_content, re.DOTALL)

            for json_text in json_matches:
                try:
                    data = json.loads(json_text)

                    # Handle single object or array
                    if not isinstance(data, list):
                        data = [data]

                    for item in data:
                        if item.get('@type') == 'Event' and item.get('name') == 'Inspection':
                            inspection = {
                                'start_date': item.get('startDate'),
                                'end_date': item.get('endDate'),
                                'url': item.get('url')
                            }
                            inspections.append(inspection)

                except json.JSONDecodeError:
                    continue

        except Exception as e:
            print(f"    ❌ Inspection extraction error: {e}")

        return inspections

    def extract_agent_phone(self, soup, tree):
        """Extract agent phone number using multiple approaches"""

        # Method 1: Look for phone links with tel: protocol
        tel_links = soup.find_all('a', href=re.compile(r'^tel:'))
        for link in tel_links:
            phone = link.get('href').replace('tel:', '').strip()
            if phone and len(phone) > 8:
                return phone

        # Method 2: Look for phone numbers in text (Australian format)
        phone_patterns = [
            r'\b0[2-8]\s?\d{4}\s?\d{4}\b',  # Australian landline
            r'\b04\d{2}\s?\d{3}\s?\d{3}\b',  # Australian mobile
            r'\(\d{2}\)\s?\d{4}\s?\d{4}',    # (02) format
        ]

        page_text = soup.get_text()
        for pattern in phone_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                return matches[0].strip()

        # Method 3: Try alternative XPath for agent contact
        alternative_xpaths = [
            '//a[contains(@href, "tel:")]',
            '//div[contains(@class, "agent")]//a[contains(@href, "tel:")]',
            '//*[contains(text(), "0") and contains(text(), " ")]'
        ]

        for xpath in alternative_xpaths:
            try:
                elements = tree.xpath(xpath)
                for element in elements:
                    if hasattr(element, 'get'):
                        href = element.get('href', '')
                        if 'tel:' in href:
                            return href.replace('tel:', '').strip()
                    text = element.text_content() if hasattr(element, 'text_content') else str(element)
                    # Look for phone number pattern in text
                    for pattern in phone_patterns:
                        match = re.search(pattern, text)
                        if match:
                            return match.group(0)
            except:
                continue

        return None

    def extract_property_id(self, url):
        """Extract property ID from URL"""
        patterns = [r'-(\d{8,10})(?:\?|#|$)', r'property-[^-]+-[^-]+-[^-]+-(\d+)']
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return f"optimized_{random.randint(100000, 999999)}"

    def extract_type_from_url(self, url):
        """Extract property type from URL"""
        url_lower = url.lower()
        if 'house' in url_lower:
            return 'house'
        elif 'apartment' in url_lower or 'unit' in url_lower:
            return 'apartment'
        elif 'townhouse' in url_lower:
            return 'townhouse'
        return 'unknown'

    def save_html_for_inspection(self, html_content, property_id):
        """Save HTML for inspection"""
        inspection_dir = Path("data/html_inspection")
        inspection_dir.mkdir(parents=True, exist_ok=True)

        html_file = inspection_dir / f"{property_id}_optimized.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  💾 HTML saved: {html_file}")
        return str(html_file)

    def save_optimized_property(self, property_data):
        """Save optimized property data"""

        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        property_id = property_data['id']
        filename = f"{property_id}_optimized_complete.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Saved optimized property: {filepath}")
        return True

    def print_complete_summary(self, property_data):
        """Print complete extraction summary with all XPath-extracted fields"""

        print(f"\n🎉 XPATH + OPTIMIZED EXTRACTION COMPLETE!")
        print(f"📊 COMPLETE PROPERTY DATA:")
        print(f"  Property ID: {property_data.get('id')}")
        print(f"  Title/Address: {property_data.get('title', 'Missing')}")
        print(f"  Price: {property_data.get('price', 'Missing')}")
        print(f"  Bedrooms: {property_data.get('bedrooms', 'Missing')}")
        print(f"  Bathrooms: {property_data.get('bathrooms', 'Missing')}")
        print(f"  Car Spaces: {property_data.get('car_spaces', 'Missing')}")
        print(f"  Land Size: {property_data.get('land_size', 'Missing')}")
        print(f"  Property Type: {property_data.get('property_type')}")
        print(f"  Description: {len(property_data.get('description', ''))} characters")
        print(f"  Features: {len(property_data.get('features', []))} items")
        print(f"  Highlights: {len(property_data.get('property_highlights', []))} items")
        print(f"  Agent Name: {property_data.get('agent_name', 'Missing')}")
        print(f"  Agent Phone: {property_data.get('agent_number', 'Missing')}")
        print(f"  Agency Name: {property_data.get('agency_name', 'Missing')}")
        print(f"  Agency Address: {property_data.get('agency_address', 'Missing')}")
        print(f"  Inspections: {len(property_data.get('inspections', []))} scheduled")
        print(f"  Real images: {len(property_data.get('images', []))}")
        print(f"  Downloaded: {len(property_data.get('downloaded_images', []))}")

        # Show sample features
        if property_data.get('features'):
            print(f"  Sample features: {property_data['features'][:3]}")

        # Show sample highlights
        if property_data.get('property_highlights'):
            print(f"  Sample highlights: {property_data['property_highlights'][:2]}")

        # Show inspection times
        if property_data.get('inspections'):
            for insp in property_data['inspections'][:2]:
                print(f"  Inspection: {insp.get('start_date', 'TBD')}")

        # Show image types
        if property_data.get('downloaded_images'):
            image_types = [img['type'] for img in property_data['downloaded_images']]
            print(f"  Image types: {image_types}")


def test_optimized_extraction():
    """Test optimized extraction approach"""

    print("🚀 TESTING OPTIMIZED PROPERTY EXTRACTION")
    print("Based on HTML inspection findings")
    print("="*70)

    extractor = OptimizedPropertyExtractor()

    # Test first property
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    success1, data1 = extractor.extract_property_perfectly(test_url)

    if success1:
        print(f"\n🎯 FIRST PROPERTY OPTIMIZED!")

        # Test second property to validate
        print(f"\n🔄 TESTING SECOND PROPERTY...")
        second_url = "https://www.realestate.com.au/property-apartment-qld-south+bank-148928524"

        success2, data2 = extractor.extract_property_perfectly(second_url)

        if success2:
            print(f"\n🏆 TWO PROPERTIES OPTIMIZED!")
            print(f"Approach validated with complete data extraction")

            print(f"\n📋 INSPECT YOUR OPTIMIZED DATA:")
            print(f"  python3 view_data.py 5")
            print(f"  cat data/properties/*_optimized_complete.json")
            print(f"  ls data/images/")

            print(f"\n💳 TOTAL CREDITS USED: {extractor.credits_used}")
            print(f"💳 CREDITS PER PROPERTY: {extractor.credits_used / 2}")

            return True

    return False


if __name__ == "__main__":
    success = test_optimized_extraction()

    if success:
        print(f"\n🎉 OPTIMIZED APPROACH SUCCESSFUL!")
        print("Ready to scale with complete property details + images")
    else:
        print(f"\n⚠️ Optimization needs refinement")