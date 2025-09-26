#!/usr/bin/env python3
"""
ROBUST XPATH EXTRACTOR - More Flexible Approach
Uses semantic CSS selectors and flexible XPaths when specific paths fail
"""

from scrapingbee import ScrapingBeeClient
from lxml import html as lxml_html
from bs4 import BeautifulSoup
import json
import re
import html
from datetime import datetime, timezone
from pathlib import Path

class RobustXPathExtractor:
    """Robust extractor using flexible selectors when exact XPaths fail"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)

        # Your original XPaths (try first)
        self.target_xpaths = {
            'full_address': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[1]/h1',
            'property_id': '/html/body/div[1]/div[4]/div[4]/div[1]/div/div/div[1]/div[2]/p/text()[2]',
            'bedrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[1]/p',
            'bathrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[3]/p',
            'car_spaces': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[4]/p',
            'land_size': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[2]/li/p',
            'offer': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[2]/span',
            'property_highlights': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[4]/div[3]',
            'property_features': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[6]/div/div/div',
            'inspections': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[8]/div[2]',
            'description_title': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[1]/h2',
            'description_body': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[2]/div/div/span/p',
            'agent_picture': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/a',
            'agent_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[1]/a',
            'agent_number': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[2]/a[2]',
            'agency_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/a',
            'agency_address': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/div'
        }

        # Flexible backup selectors
        self.backup_selectors = {
            'full_address': ['//h1[contains(@class, "address")]', '//h1', '//title'],
            'bedrooms': ['//span[contains(text(), "bed")]', '//*[contains(text(), "bedroom")]', '//li[contains(text(), "bed")]'],
            'bathrooms': ['//span[contains(text(), "bath")]', '//*[contains(text(), "bathroom")]', '//li[contains(text(), "bath")]'],
            'car_spaces': ['//span[contains(text(), "car")]', '//*[contains(text(), "garage")]', '//li[contains(text(), "car")]'],
            'land_size': ['//*[contains(text(), "m²")]', '//*[contains(text(), "sqm")]', '//span[contains(text(), "land")]'],
            'offer': ['//span[contains(text(), "$")]', '//*[contains(text(), "Offers")]', '//*[contains(text(), "Price")]'],
            'agent_name': ['//a[contains(@href, "agent")]', '//*[contains(@class, "agent")]//a', '//div[contains(@class, "contact")]//a'],
            'agency_name': ['//*[contains(@class, "agency")]', '//*[contains(text(), "Realty")]', '//*[contains(text(), "Real Estate")]'],
            'property_features': ['//*[contains(@class, "feature")]', '//ul//li', '//div[contains(@class, "listing")]//li'],
            'property_highlights': ['//*[contains(@class, "highlight")]', '//*[contains(@class, "summary")]']
        }

    def extract_property_robust(self, property_url):
        """Extract property using robust approach - try exact XPath first, then flexible selectors"""

        print(f"🎯 ROBUST XPATH EXTRACTION")
        print(f"Property: {property_url}")
        print("="*70)

        params = {
            'render_js': True,
            'block_resources': False,
            'stealth_proxy': True,
            'country_code': 'AU'
        }

        try:
            response = self.client.get(property_url, params=params, timeout=120)

            if response.status_code == 200:
                print(f"✅ HTML fetched successfully")

                # Save HTML for debugging
                property_id = self.extract_property_id_from_url(property_url)
                self.save_html_for_debug(response.text, property_id)

                # Parse with multiple parsers
                tree = lxml_html.fromstring(response.text)
                soup = BeautifulSoup(response.text, 'html.parser')

                property_data = {
                    'id': property_id,
                    'url': property_url,
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'method': 'robust_xpath_extraction'
                }

                print(f"\n📍 TRYING EXACT XPATHS FIRST...")
                # Try exact XPaths first
                exact_successes = 0
                for field_name, xpath in self.target_xpaths.items():
                    success = self.try_exact_xpath(tree, xpath, field_name, property_data)
                    if success:
                        exact_successes += 1
                        print(f"  ✅ {field_name}: SUCCESS (exact XPath)")
                    else:
                        print(f"  ❌ {field_name}: Failed (exact XPath)")

                print(f"\n🔄 TRYING FLEXIBLE SELECTORS...")
                # Try flexible selectors for failed fields
                flexible_successes = 0
                for field_name in self.backup_selectors:
                    if field_name not in property_data:  # Only if exact XPath failed
                        success = self.try_flexible_selectors(tree, soup, field_name, property_data)
                        if success:
                            flexible_successes += 1
                            print(f"  ✅ {field_name}: SUCCESS (flexible)")
                        else:
                            print(f"  ❌ {field_name}: Failed (flexible)")

                # Extract from meta tags as ultimate fallback
                print(f"\n📋 EXTRACTING FROM META TAGS...")
                self.extract_from_meta_tags(soup, property_data)

                # Extract images
                print(f"\n📸 EXTRACTING IMAGES...")
                images = self.extract_property_images(soup)
                if images:
                    property_data['images'] = images
                    print(f"  ✅ {len(images)} images found")

                # Save complete data
                self.save_property_data(property_data, property_id)

                # Print summary
                self.print_extraction_summary(property_data, exact_successes, flexible_successes)

                return True, property_data

        except Exception as e:
            print(f"❌ Extraction failed: {e}")

        return False, None

    def try_exact_xpath(self, tree, xpath, field_name, property_data):
        """Try the exact XPath provided by user"""

        try:
            elements = tree.xpath(xpath)
            if elements:
                # Handle different types of results
                if isinstance(elements[0], str):
                    value = elements[0].strip()
                else:
                    value = elements[0].text_content().strip() if elements[0].text_content() else ''

                if value:
                    self.process_extracted_value(field_name, value, elements[0], property_data)
                    return True

        except Exception as e:
            print(f"    XPath error: {e}")

        return False

    def try_flexible_selectors(self, tree, soup, field_name, property_data):
        """Try flexible backup selectors"""

        if field_name not in self.backup_selectors:
            return False

        for selector in self.backup_selectors[field_name]:
            try:
                elements = tree.xpath(selector)
                if elements:
                    for element in elements:
                        text = element.text_content().strip() if hasattr(element, 'text_content') else str(element).strip()

                        # Validate the text makes sense for this field
                        if self.validate_field_value(field_name, text):
                            self.process_extracted_value(field_name, text, element, property_data)
                            return True

            except Exception as e:
                continue

        return False

    def validate_field_value(self, field_name, text):
        """Validate that extracted text makes sense for the field"""

        if len(text) < 2:
            return False

        if field_name == 'bedrooms':
            return re.search(r'\d+', text) and ('bed' in text.lower() or text.isdigit())
        elif field_name == 'bathrooms':
            return re.search(r'\d+', text) and ('bath' in text.lower() or text.isdigit())
        elif field_name == 'car_spaces':
            return re.search(r'\d+', text) and ('car' in text.lower() or 'garage' in text.lower() or text.isdigit())
        elif field_name == 'land_size':
            return 'm²' in text or 'sqm' in text or 'hectare' in text.lower()
        elif field_name == 'offer':
            return '$' in text or 'offer' in text.lower() or 'price' in text.lower()
        elif field_name == 'agent_name':
            return len(text) > 5 and len(text) < 50 and not text.isdigit()
        elif field_name == 'agency_name':
            return ('realty' in text.lower() or 'real estate' in text.lower() or
                   'property' in text.lower()) and len(text) > 5
        elif field_name == 'full_address':
            return len(text) > 10 and ('street' in text.lower() or 'avenue' in text.lower() or
                                      'road' in text.lower() or 'qld' in text.lower())

        return True  # Default to accepting

    def process_extracted_value(self, field_name, value, element, property_data):
        """Process and clean extracted value"""

        value = value.strip()

        if field_name in ['bedrooms', 'bathrooms', 'car_spaces']:
            # Extract number
            match = re.search(r'\d+', value)
            if match:
                property_data[field_name] = int(match.group(0))
        elif field_name == 'full_address':
            property_data['title'] = value
            property_data['address'] = value
            property_data['full_address'] = value
        elif field_name == 'offer':
            property_data['price'] = value
            property_data['offer'] = value
        elif field_name == 'land_size':
            property_data[field_name] = value.replace('mÂ²', 'm²')
        elif field_name in ['property_features', 'property_highlights']:
            # Extract multiple items from container
            if hasattr(element, 'xpath'):
                items = []
                list_items = element.xpath('.//li | .//p | .//div')
                for item in list_items:
                    item_text = item.text_content().strip() if item.text_content() else ''
                    if item_text and 5 < len(item_text) < 200:
                        items.append(item_text)

                if items:
                    property_data[field_name] = items[:10]
                else:
                    # Fallback to splitting text
                    parts = re.split(r'[•\-\n]', value)
                    items = [part.strip() for part in parts if part.strip() and 5 < len(part.strip()) < 200]
                    property_data[field_name] = items[:10]
            else:
                property_data[field_name] = [value]
        else:
            property_data[field_name] = value

    def extract_from_meta_tags(self, soup, property_data):
        """Extract from meta tags as fallback"""

        # Title from og:title
        if 'title' not in property_data:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                property_data['title'] = og_title.get('content', '')
                property_data['address'] = og_title.get('content', '')
                print(f"  ✅ Title from og:title: {property_data['title']}")

        # Description from og:description
        if 'description' not in property_data:
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                raw_desc = og_desc.get('content', '')
                clean_desc = html.unescape(raw_desc).replace('&lt;br/&gt;', '\n').replace('<br/>', '\n')
                property_data['description'] = clean_desc
                property_data['description_body'] = clean_desc
                print(f"  ✅ Description from og:description: {len(clean_desc)} chars")

                # Extract features from description
                if 'property_features' not in property_data:
                    features = self.extract_features_from_text(clean_desc)
                    if features:
                        property_data['property_features'] = features
                        print(f"  ✅ Features from description: {len(features)} items")

        # Property ID from structured data
        if 'property_id' not in property_data:
            try:
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    data = json.loads(script.text)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Residence':
                                address = item.get('address', {})
                                if address.get('streetAddress'):
                                    print(f"  ✅ Address from JSON-LD: {address.get('streetAddress')}")
                                    if 'address' not in property_data:
                                        property_data['address'] = f"{address.get('streetAddress')}, {address.get('addressLocality')}, {address.get('addressRegion')} {address.get('postalCode')}"
            except:
                pass

    def extract_features_from_text(self, text):
        """Extract features from description text"""

        features = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                feature = line.lstrip('-•').strip()
                if 5 < len(feature) < 200:
                    features.append(feature)

        return features[:15]

    def extract_property_images(self, soup):
        """Extract property images"""

        images = []

        # Look for og:image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            img_url = og_image.get('content')
            if img_url and 'i2.au.reastatic.net' in img_url:
                images.append({
                    'url': img_url,
                    'type': 'main_photo'
                })

        # Find all reastatic URLs
        page_content = str(soup)
        reastatic_urls = re.findall(r'https://i2\.au\.reastatic\.net/[^"\'>\s]+', page_content)

        for url in set(reastatic_urls):
            if 'logo' not in url.lower() and len(url) > 50:
                images.append({
                    'url': url,
                    'type': 'property_photo'
                })

        return images

    def extract_property_id_from_url(self, url):
        """Extract property ID from URL"""
        match = re.search(r'-(\d{8,10})(?:\?|#|$)', url)
        return match.group(1) if match else 'unknown'

    def save_html_for_debug(self, html_content, property_id):
        """Save HTML for debugging"""
        debug_dir = Path("data/html_inspection")
        debug_dir.mkdir(parents=True, exist_ok=True)

        html_file = debug_dir / f"{property_id}_robust_debug.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  💾 Debug HTML saved: {html_file}")

    def save_property_data(self, property_data, property_id):
        """Save property data"""
        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{property_id}_robust_complete.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Property data saved: {filepath}")

    def print_extraction_summary(self, property_data, exact_successes, flexible_successes):
        """Print extraction summary"""

        print(f"\n🎉 ROBUST EXTRACTION SUMMARY")
        print("="*50)
        print(f"  Exact XPath successes: {exact_successes}")
        print(f"  Flexible selector successes: {flexible_successes}")
        print(f"  Total fields extracted: {len(property_data)}")
        print()
        print(f"  Property ID: {property_data.get('id')}")
        print(f"  Title: {property_data.get('title', 'Missing')}")
        print(f"  Price: {property_data.get('price', 'Missing')}")
        print(f"  Bedrooms: {property_data.get('bedrooms', 'Missing')}")
        print(f"  Bathrooms: {property_data.get('bathrooms', 'Missing')}")
        print(f"  Car Spaces: {property_data.get('car_spaces', 'Missing')}")
        print(f"  Land Size: {property_data.get('land_size', 'Missing')}")
        print(f"  Agent: {property_data.get('agent_name', 'Missing')}")
        print(f"  Agent Phone: {property_data.get('agent_number', 'Missing')}")
        print(f"  Agency: {property_data.get('agency_name', 'Missing')}")
        print(f"  Description: {len(property_data.get('description', ''))} chars")
        print(f"  Features: {len(property_data.get('property_features', []))} items")
        print(f"  Images: {len(property_data.get('images', []))} found")


def test_robust_extraction():
    """Test robust extraction approach"""

    print("🚀 TESTING ROBUST XPATH EXTRACTION")
    print("="*70)

    extractor = RobustXPathExtractor()
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    success, data = extractor.extract_property_robust(test_url)

    if success:
        print(f"\n🎯 ROBUST EXTRACTION COMPLETE!")
        print("Now you can see which XPaths work and which need flexible approach")
        return True
    else:
        print(f"\n❌ Robust extraction failed")
        return False


if __name__ == "__main__":
    test_robust_extraction()