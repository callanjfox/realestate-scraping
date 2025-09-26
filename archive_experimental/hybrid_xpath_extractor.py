#!/usr/bin/env python3
"""
HYBRID XPATH EXTRACTOR - Container + Sub-extraction Approach
Treats failed XPaths as containers and extracts their contents properly
"""

from scrapingbee import ScrapingBeeClient
from lxml import html as lxml_html
from bs4 import BeautifulSoup
import json
import re
import html
from datetime import datetime, timezone
from pathlib import Path

class HybridXPathExtractor:
    """Hybrid extractor using container-based XPath approach for complex elements"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)

        # Working XPaths (validated)
        self.working_xpaths = {
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

        # Container XPaths (need sub-extraction)
        self.container_xpaths = {
            'property_highlights': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[4]/div[3]',
            'property_features': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[6]/div/div/div',
            'inspections': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[8]/div[2]',
            'description_title': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[1]/h2',
            'description_body': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[2]/div/div/span/p',
            'agent_number': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[2]/a[2]'
        }

    def extract_property_complete(self, property_url):
        """Extract property using hybrid approach - XPath + container extraction"""

        print(f"🎯 HYBRID XPATH EXTRACTION")
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

                # Parse with lxml for XPath
                tree = lxml_html.fromstring(response.text)
                soup = BeautifulSoup(response.text, 'html.parser')

                property_data = {
                    'id': property_id,
                    'url': property_url,
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'method': 'hybrid_xpath_container_extraction'
                }

                print(f"\n📍 EXTRACTING WITH WORKING XPATHS...")
                # Extract using working XPaths
                for field_name, xpath in self.working_xpaths.items():
                    success = self.extract_single_field(tree, xpath, field_name, property_data)
                    if success:
                        print(f"  ✅ {field_name}: {property_data.get(field_name)}")
                    else:
                        print(f"  ❌ {field_name}: Failed")

                print(f"\n📦 EXTRACTING FROM CONTAINER XPATHS...")
                # Extract using container XPaths with sub-extraction
                for field_name, xpath in self.container_xpaths.items():
                    success = self.extract_container_field(tree, xpath, field_name, property_data)
                    if success:
                        print(f"  ✅ {field_name}: Extracted")
                    else:
                        print(f"  ❌ {field_name}: Not found")

                # Add images
                print(f"\n📸 EXTRACTING IMAGES...")
                images = self.extract_property_images(soup)
                if images:
                    property_data['images'] = images
                    print(f"  ✅ {len(images)} images found")

                # Save complete data
                self.save_property_data(property_data, property_id)

                # Print summary
                self.print_extraction_summary(property_data)

                return True, property_data

        except Exception as e:
            print(f"❌ Extraction failed: {e}")

        return False, None

    def extract_single_field(self, tree, xpath, field_name, property_data):
        """Extract single field using XPath"""

        try:
            elements = tree.xpath(xpath)
            if elements:
                if isinstance(elements[0], str):
                    value = elements[0].strip()
                else:
                    value = elements[0].text_content().strip() if elements[0].text_content() else ''

                # Process field based on type
                if field_name in ['bedrooms', 'bathrooms', 'car_spaces'] and value.isdigit():
                    property_data[field_name] = int(value)
                elif field_name == 'full_address':
                    property_data['title'] = value
                    property_data['address'] = value
                elif field_name == 'offer':
                    property_data['price'] = value
                elif field_name == 'land_size':
                    property_data[field_name] = value.replace('mÂ²', 'm²')
                else:
                    property_data[field_name] = value

                return True

        except Exception as e:
            print(f"    Error extracting {field_name}: {e}")

        return False

    def extract_container_field(self, tree, xpath, field_name, property_data):
        """Extract container field and parse its contents"""

        try:
            print(f"    🔍 Looking for container: {field_name}")
            print(f"    📍 XPath: {xpath}")

            elements = tree.xpath(xpath)

            if elements:
                container = elements[0]
                print(f"    ✅ Container found!")

                # Extract based on field type
                if field_name == 'property_highlights':
                    highlights = self.extract_highlights_from_container(container)
                    property_data['property_highlights'] = highlights
                    print(f"    📝 Extracted {len(highlights)} highlights")
                    return len(highlights) > 0

                elif field_name == 'property_features':
                    features = self.extract_features_from_container(container)
                    property_data['property_features'] = features
                    print(f"    📝 Extracted {len(features)} features")
                    return len(features) > 0

                elif field_name == 'inspections':
                    inspections = self.extract_inspections_from_container(container)
                    property_data['inspections'] = inspections
                    print(f"    📅 Extracted {len(inspections)} inspections")
                    return len(inspections) > 0

                elif field_name == 'description_title':
                    title = container.text_content().strip() if container.text_content() else ''
                    property_data['description_title'] = title
                    print(f"    📝 Description title: {title}")
                    return len(title) > 0

                elif field_name == 'description_body':
                    body = self.extract_description_from_container(container)
                    property_data['description_body'] = body
                    print(f"    📝 Description body: {len(body)} chars")
                    return len(body) > 0

                elif field_name == 'agent_number':
                    phone = self.extract_agent_phone_from_container(container)
                    if phone:
                        property_data['agent_number'] = phone
                        print(f"    📞 Agent phone: {phone}")
                        return True

            else:
                print(f"    ❌ Container not found")

        except Exception as e:
            print(f"    ❌ Container extraction error: {e}")

        return False

    def extract_highlights_from_container(self, container):
        """Extract highlights from container element"""

        highlights = []

        try:
            # Get all list items or bullet points
            list_items = container.xpath('.//li | .//p | .//div')

            for item in list_items:
                text = item.text_content().strip() if item.text_content() else ''
                if text and len(text) > 10:  # Meaningful highlights
                    highlights.append(text)

            # If no list items, get direct text
            if not highlights:
                text = container.text_content().strip() if container.text_content() else ''
                if text:
                    # Split by common separators
                    parts = re.split(r'[•\-\n]', text)
                    for part in parts:
                        part = part.strip()
                        if part and len(part) > 10:
                            highlights.append(part)

        except Exception as e:
            print(f"      Error extracting highlights: {e}")

        return highlights[:10]  # Limit to 10 highlights

    def extract_features_from_container(self, container):
        """Extract features from container element"""

        features = []

        try:
            # Method 1: Look for list items
            list_items = container.xpath('.//li')
            for item in list_items:
                text = item.text_content().strip() if item.text_content() else ''
                if text and 5 < len(text) < 200:  # Reasonable feature length
                    features.append(text)

            # Method 2: Look for paragraph elements
            if not features:
                paragraphs = container.xpath('.//p')
                for p in paragraphs:
                    text = p.text_content().strip() if p.text_content() else ''
                    if text and 5 < len(text) < 200:
                        features.append(text)

            # Method 3: Look for div elements with text
            if not features:
                divs = container.xpath('.//div')
                for div in divs:
                    text = div.text_content().strip() if div.text_content() else ''
                    if text and 5 < len(text) < 200:
                        features.append(text)

            # Method 4: Split container text by common separators
            if not features:
                text = container.text_content().strip() if container.text_content() else ''
                if text:
                    parts = re.split(r'[•\-\n]', text)
                    for part in parts:
                        part = part.strip()
                        if part and 5 < len(part) < 200:
                            features.append(part)

        except Exception as e:
            print(f"      Error extracting features: {e}")

        return features[:15]  # Limit to 15 features

    def extract_inspections_from_container(self, container):
        """Extract inspection times from container element"""

        inspections = []

        try:
            # Look for time-related text patterns
            text = container.text_content().strip() if container.text_content() else ''

            # Common inspection patterns
            patterns = [
                r'(\d{1,2}[:/]\d{2}[ap]?m?\s*-?\s*\d{1,2}[:/]\d{2}[ap]m)',  # Time ranges
                r'(\d{1,2}[ap]m\s*-?\s*\d{1,2}[ap]m)',  # Simple time ranges
                r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)\s+\d+',  # Day + date
                r'(\d{1,2}/\d{1,2}/\d{2,4})',  # Dates
            ]

            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    inspections.append({
                        'time': match,
                        'source': 'container_text'
                    })

            # Also look for structured elements
            time_elements = container.xpath('.//time | .//*[contains(@class, "time")] | .//*[contains(@class, "date")]')
            for elem in time_elements:
                time_text = elem.text_content().strip() if elem.text_content() else ''
                if time_text:
                    inspections.append({
                        'time': time_text,
                        'source': 'structured_element'
                    })

        except Exception as e:
            print(f"      Error extracting inspections: {e}")

        return inspections

    def extract_description_from_container(self, container):
        """Extract description from container element"""

        try:
            # Get all text content from container
            text = container.text_content().strip() if container.text_content() else ''

            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.replace('\n', ' ').strip()

            return text

        except Exception as e:
            print(f"      Error extracting description: {e}")
            return ''

    def extract_agent_phone_from_container(self, container):
        """Extract agent phone from container element"""

        try:
            # Look for tel: links
            tel_links = container.xpath('.//a[contains(@href, "tel:")]')
            for link in tel_links:
                href = link.get('href', '')
                if 'tel:' in href:
                    phone = href.replace('tel:', '').strip()
                    if len(phone) > 8:
                        return phone

            # Look for phone patterns in text
            text = container.text_content().strip() if container.text_content() else ''

            phone_patterns = [
                r'\b0[2-8]\s?\d{4}\s?\d{4}\b',  # Australian landline
                r'\b04\d{2}\s?\d{3}\s?\d{3}\b',  # Australian mobile
                r'\(\d{2}\)\s?\d{4}\s?\d{4}',    # (02) format
            ]

            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0].strip()

        except Exception as e:
            print(f"      Error extracting agent phone: {e}")

        return None

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

        html_file = debug_dir / f"{property_id}_hybrid_debug.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  💾 Debug HTML saved: {html_file}")

    def save_property_data(self, property_data, property_id):
        """Save property data"""
        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{property_id}_hybrid_complete.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Property data saved: {filepath}")

    def print_extraction_summary(self, property_data):
        """Print extraction summary"""

        print(f"\n🎉 HYBRID EXTRACTION SUMMARY")
        print("="*50)
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

        # Container-extracted fields
        print(f"  Description Title: {property_data.get('description_title', 'Missing')}")
        print(f"  Description Body: {len(property_data.get('description_body', ''))} chars")
        print(f"  Property Highlights: {len(property_data.get('property_highlights', []))} items")
        print(f"  Property Features: {len(property_data.get('property_features', []))} items")
        print(f"  Inspections: {len(property_data.get('inspections', []))} scheduled")
        print(f"  Images: {len(property_data.get('images', []))} found")

        # Show samples
        if property_data.get('property_highlights'):
            print(f"  Sample highlights: {property_data['property_highlights'][:2]}")

        if property_data.get('property_features'):
            print(f"  Sample features: {property_data['property_features'][:3]}")


def test_hybrid_extraction():
    """Test hybrid container-based extraction"""

    print("🚀 TESTING HYBRID XPATH CONTAINER EXTRACTION")
    print("="*70)

    extractor = HybridXPathExtractor()
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    success, data = extractor.extract_property_complete(test_url)

    if success:
        print(f"\n🎯 HYBRID EXTRACTION SUCCESSFUL!")
        return True
    else:
        print(f"\n❌ Hybrid extraction failed")
        return False


if __name__ == "__main__":
    test_hybrid_extraction()