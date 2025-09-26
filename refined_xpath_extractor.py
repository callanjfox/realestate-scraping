#!/usr/bin/env python3
"""
REFINED XPATH EXTRACTOR - Container + Sub-extraction Approach
Uses your exact XPaths as container locators, then intelligently extracts content
"""

from scrapingbee import ScrapingBeeClient
from lxml import html as lxml_html
from bs4 import BeautifulSoup
import json
import re
import html
from datetime import datetime, timezone
from pathlib import Path

class RefinedXPathExtractor:
    """Refined extractor using exact XPaths as containers with intelligent sub-extraction"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)

        # Working XPaths (validated to work)
        self.working_xpaths = {
            'full_address': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[1]/h1',
            'bedrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[1]/p',
            'bathrooms': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[3]/p',
            'car_spaces': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[1]/li[4]/p',
            'land_size': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[1]/div[2]/ul/div[2]/li/p',
            'offer': '/html/body/div[1]/div[4]/div[3]/div[1]/div/div/div[1]/div/div[2]/span',
            'agent_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[1]/a',
            'agency_name': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/a',
            'agency_address': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/div[2]/div'
        }

        # Priority Container XPaths - User specified these exact paths
        self.priority_container_xpaths = {
            'property_highlights': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[4]/div[3]',
            'property_features': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[6]/div/div/div'
        }

        # Other Container XPaths (for additional fields)
        self.other_container_xpaths = {
            'inspections': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[8]/div[2]',
            'description_title': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[1]/h2',
            'description_body': '/html/body/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[5]/div[2]/div/div/span/p',
            'agent_number': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/div/div[2]/a[2]',
            'property_id': '/html/body/div[1]/div[4]/div[4]/div[1]/div/div/div[1]/div[2]/p/text()[2]',
            'agent_picture': '/html/body/div[1]/div[4]/div[3]/div[2]/div[2]/div[1]/div/ul/li/a'
        }

    def extract_property_refined(self, property_url):
        """Extract property using refined container approach"""

        print(f"🎯 REFINED XPATH EXTRACTION")
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
                    'method': 'refined_xpath_container_extraction'
                }

                print(f"\n📍 EXTRACTING WITH WORKING XPATHS...")
                working_count = 0
                for field_name, xpath in self.working_xpaths.items():
                    success = self.extract_working_field(tree, xpath, field_name, property_data)
                    if success:
                        working_count += 1
                        print(f"  ✅ {field_name}: {property_data.get(field_name)}")
                    else:
                        print(f"  ❌ {field_name}: Failed")

                print(f"\n📦 EXTRACTING PRIORITY CONTAINER FIELDS...")
                priority_count = 0
                for field_name, xpath in self.priority_container_xpaths.items():
                    print(f"\n  🎯 PRIORITY FIELD: {field_name}")
                    success = self.extract_container_field(tree, xpath, field_name, property_data)
                    if success:
                        priority_count += 1
                        value = property_data.get(field_name)
                        if isinstance(value, list):
                            print(f"  ✅ {field_name}: {len(value)} items extracted")
                            if len(value) > 0:
                                print(f"      Sample: {value[0][:100]}...")
                        else:
                            print(f"  ✅ {field_name}: {value}")
                    else:
                        print(f"  ❌ {field_name}: Failed to extract")

                print(f"\n📦 EXTRACTING OTHER CONTAINER FIELDS...")
                other_count = 0
                for field_name, xpath in self.other_container_xpaths.items():
                    success = self.extract_container_field(tree, xpath, field_name, property_data)
                    if success:
                        other_count += 1
                        value = property_data.get(field_name)
                        if isinstance(value, list):
                            print(f"  ✅ {field_name}: {len(value)} items extracted")
                        elif isinstance(value, str) and len(value) > 50:
                            print(f"  ✅ {field_name}: {len(value)} characters")
                        else:
                            print(f"  ✅ {field_name}: {value}")
                    else:
                        print(f"  ❌ {field_name}: Container not found")

                container_count = priority_count + other_count

                # Add meta tag fallbacks
                print(f"\n📋 ADDING META TAG FALLBACKS...")
                self.add_meta_fallbacks(soup, property_data)

                # Extract images
                print(f"\n📸 EXTRACTING IMAGES...")
                images = self.extract_property_images(soup)
                if images:
                    property_data['images'] = images
                    print(f"  ✅ {len(images)} images found")

                # Save complete data
                self.save_property_data(property_data, property_id)

                # Print summary
                self.print_extraction_summary(property_data, working_count, priority_count, other_count)

                return True, property_data

        except Exception as e:
            print(f"❌ Extraction failed: {e}")

        return False, None

    def extract_working_field(self, tree, xpath, field_name, property_data):
        """Extract single field using working XPath"""

        try:
            elements = tree.xpath(xpath)
            if elements:
                if isinstance(elements[0], str):
                    value = elements[0].strip()
                else:
                    value = elements[0].text_content().strip() if elements[0].text_content() else ''

                if value:
                    self.process_field_value(field_name, value, property_data)
                    return True

        except Exception as e:
            print(f"    Error: {e}")

        return False

    def extract_container_field(self, tree, xpath, field_name, property_data):
        """Extract from container using intelligent sub-extraction"""

        try:
            print(f"    🔍 Searching container: {field_name}")
            print(f"    📍 XPath: {xpath}")
            elements = tree.xpath(xpath)

            if elements:
                container = elements[0]
                print(f"    ✅ Container found! Element: {container.tag if hasattr(container, 'tag') else type(container)}")

                # Apply specialized extraction based on field type
                if field_name == 'property_highlights':
                    return self.extract_highlights_smart(container, property_data, field_name)

                elif field_name == 'property_features':
                    return self.extract_features_smart(container, property_data, field_name)

                elif field_name == 'inspections':
                    return self.extract_inspections_smart(container, property_data)

                elif field_name == 'description_title':
                    return self.extract_description_title_smart(container, property_data)

                elif field_name == 'description_body':
                    return self.extract_description_body_smart(container, property_data)

                elif field_name == 'agent_number':
                    return self.extract_agent_number_smart(container, property_data)

                elif field_name == 'property_id':
                    return self.extract_property_id_smart(container, property_data)

                elif field_name == 'agent_picture':
                    return self.extract_agent_picture_smart(container, property_data)

            else:
                print(f"    ❌ Container not found with exact XPath")
                # Try fallback approaches for these critical fields
                if field_name == 'property_highlights':
                    return self.extract_highlights_fallback(tree, property_data)
                elif field_name == 'property_features':
                    return self.extract_features_fallback(tree, property_data)

        except Exception as e:
            print(f"    ❌ Container error: {e}")

        return False

    def extract_highlights_smart(self, container, property_data, field_name):
        """Smart extraction of property highlights"""

        highlights = []

        try:
            # Method 1: Look for structured lists
            list_items = container.xpath('.//li | .//div[@class] | .//p')
            for item in list_items:
                text = item.text_content().strip() if item.text_content() else ''
                if text and 10 < len(text) < 300 and self.is_valid_highlight(text):
                    highlights.append(text)

            # Method 2: Look for bullet points in text
            if not highlights:
                full_text = container.text_content().strip() if container.text_content() else ''
                if full_text:
                    # Split by common separators
                    parts = re.split(r'[•\-\n]', full_text)
                    for part in parts:
                        part = part.strip()
                        if part and 10 < len(part) < 300 and self.is_valid_highlight(part):
                            highlights.append(part)

            # Method 3: Get child elements with meaningful text
            if not highlights:
                children = container.xpath('.//*')
                for child in children:
                    text = child.text_content().strip() if child.text_content() else ''
                    if text and 10 < len(text) < 300 and self.is_valid_highlight(text):
                        highlights.append(text)

            if highlights:
                property_data['property_highlights'] = highlights[:8]  # Limit to 8
                print(f"      📝 Extracted {len(highlights)} highlights")
                return True

        except Exception as e:
            print(f"      Error extracting highlights: {e}")

        return False

    def extract_features_smart(self, container, property_data, field_name):
        """Smart extraction of property features"""

        features = []

        try:
            # Method 1: Look for list items (most common for features)
            list_items = container.xpath('.//li')
            for item in list_items:
                text = item.text_content().strip() if item.text_content() else ''
                if text and 3 < len(text) < 200 and self.is_valid_feature(text):
                    features.append(text)

            # Method 2: Look for span elements with features
            span_items = container.xpath('.//span')
            for span in span_items:
                text = span.text_content().strip() if span.text_content() else ''
                if text and 3 < len(text) < 200 and self.is_valid_feature(text):
                    features.append(text)

            # Method 3: Look for divs with meaningful content
            divs = container.xpath('.//div')
            for div in divs:
                text = div.text_content().strip() if div.text_content() else ''
                if text and 3 < len(text) < 200 and self.is_valid_feature(text):
                    features.append(text)

            # Method 4: Look for paragraphs
            paragraphs = container.xpath('.//p')
            for p in paragraphs:
                text = p.text_content().strip() if p.text_content() else ''
                if text and 3 < len(text) < 200 and self.is_valid_feature(text):
                    features.append(text)

            # Method 5: Split container text by separators to catch additional features
            full_text = container.text_content().strip() if container.text_content() else ''
            if full_text:
                # Look for features in description-like text
                description_features = self.extract_features_from_description_text(full_text)
                features.extend(description_features)

            # Remove duplicates while preserving order
            unique_features = []
            seen = set()
            for feature in features:
                feature_clean = feature.lower().strip()
                if feature_clean not in seen and len(feature_clean) > 2:
                    seen.add(feature_clean)
                    unique_features.append(feature)

            if unique_features:
                property_data['property_features'] = unique_features[:20]  # Increased limit
                print(f"      📝 Extracted {len(unique_features)} unique features")
                return True

        except Exception as e:
            print(f"      Error extracting features: {e}")

        return False

    def extract_features_from_description_text(self, text):
        """Extract features from description text that might mention sheds, pools, etc."""

        features = []
        text_lower = text.lower()

        # Common property features to look for
        feature_keywords = [
            'shed', 'workshop', 'garage', 'carport', 'pool', 'spa', 'deck', 'balcony',
            'air conditioning', 'heating', 'fireplace', 'dishwasher', 'alarm', 'intercom',
            'ensuite', 'walk-in robe', 'built-in robes', 'study', 'office', 'rumpus',
            'family room', 'living room', 'dining room', 'kitchen', 'laundry',
            'storage', 'courtyard', 'garden', 'lawn', 'timber floors', 'tiles',
            'carpet', 'stone benchtops', 'gas cooking', 'electric cooking',
            'solar panels', 'water tank', 'bore', 'irrigation'
        ]

        for keyword in feature_keywords:
            if keyword in text_lower:
                # Find sentences containing this keyword
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        # Extract relevant part around the keyword
                        words = sentence.split()
                        keyword_words = keyword.split()

                        for i, word in enumerate(words):
                            if keyword_words[0].lower() in word.lower():
                                # Get context around the keyword (up to 6 words)
                                start = max(0, i - 2)
                                end = min(len(words), i + len(keyword_words) + 3)
                                feature_text = ' '.join(words[start:end]).strip()

                                if 5 < len(feature_text) < 100:
                                    features.append(feature_text)
                                break
                        break

        return features

    def extract_highlights_fallback(self, tree, property_data):
        """Fallback method to extract highlights using broader selectors"""

        print(f"      🔄 Trying fallback approach for highlights...")

        # Try broader XPath patterns
        fallback_xpaths = [
            '//div[contains(@class, "highlight")]',
            '//div[contains(@class, "summary")]',
            '//div[contains(@class, "features")]//li',
            '//ul//li[contains(text(), "bed") or contains(text(), "bath") or contains(text(), "garage")]',
            '//*[contains(@class, "property")]//li'
        ]

        for xpath in fallback_xpaths:
            try:
                elements = tree.xpath(xpath)
                if elements:
                    highlights = []
                    for elem in elements[:10]:  # Limit to 10
                        text = elem.text_content().strip() if elem.text_content() else ''
                        if text and 10 < len(text) < 200:
                            highlights.append(text)

                    if highlights:
                        property_data['property_highlights'] = highlights
                        print(f"      ✅ Fallback found {len(highlights)} highlights")
                        return True
            except:
                continue

        return False

    def extract_features_fallback(self, tree, property_data):
        """Fallback method to extract features using broader selectors"""

        print(f"      🔄 Trying fallback approach for features...")

        # Try broader XPath patterns
        fallback_xpaths = [
            '//div[contains(@class, "feature")]//li',
            '//div[contains(@class, "property")]//li',
            '//ul//li',
            '//div[contains(@class, "listing")]//li',
            '//*[contains(text(), "garage") or contains(text(), "pool") or contains(text(), "air")]'
        ]

        for xpath in fallback_xpaths:
            try:
                elements = tree.xpath(xpath)
                if elements:
                    features = []
                    for elem in elements[:20]:  # Limit to 20
                        text = elem.text_content().strip() if elem.text_content() else ''
                        if text and 5 < len(text) < 150:
                            # Filter out navigation/UI text
                            if not any(word in text.lower() for word in ['click', 'view', 'contact', 'email', 'phone']):
                                features.append(text)

                    if features:
                        property_data['property_features'] = features
                        print(f"      ✅ Fallback found {len(features)} features")
                        return True
            except:
                continue

        return False

    def extract_inspections_smart(self, container, property_data):
        """Smart extraction of inspection times"""

        inspections = []

        try:
            # Get all text from container
            full_text = container.text_content().strip() if container.text_content() else ''

            if full_text:
                # Look for time patterns
                time_patterns = [
                    r'(\d{1,2}:\d{2}[ap]?m?\s*-?\s*\d{1,2}:\d{2}[ap]m)',  # Time ranges
                    r'(\d{1,2}[ap]m\s*-?\s*\d{1,2}[ap]m)',  # Simple times
                    r'(Saturday|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday)\s+\d+',  # Day + date
                    r'(\d{1,2}/\d{1,2}/\d{2,4})',  # Dates
                    r'(\d{1,2}\s+[A-Za-z]+\s+\d{4})',  # Day Month Year
                ]

                for pattern in time_patterns:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        inspections.append({
                            'time': match,
                            'source': 'container_text',
                            'full_text': full_text
                        })

            # Look for structured time elements
            time_elements = container.xpath('.//*[contains(@class, "time") or contains(@class, "date") or contains(@class, "inspection")]')
            for elem in time_elements:
                time_text = elem.text_content().strip() if elem.text_content() else ''
                if time_text:
                    inspections.append({
                        'time': time_text,
                        'source': 'structured_element'
                    })

            if inspections:
                property_data['inspections'] = inspections[:5]  # Limit to 5
                print(f"      📅 Extracted {len(inspections)} inspection times")
                return True

        except Exception as e:
            print(f"      Error extracting inspections: {e}")

        return False

    def extract_description_title_smart(self, container, property_data):
        """Smart extraction of description title"""

        try:
            # Get direct text content
            title = container.text_content().strip() if container.text_content() else ''

            if title and len(title) > 3:
                property_data['description_title'] = title
                print(f"      📝 Description title: {title}")
                return True

        except Exception as e:
            print(f"      Error extracting description title: {e}")

        return False

    def extract_description_body_smart(self, container, property_data):
        """Smart extraction of description body"""

        try:
            # Method 1: Get all paragraph text
            paragraphs = container.xpath('.//p')
            if paragraphs:
                texts = []
                for p in paragraphs:
                    text = p.text_content().strip() if p.text_content() else ''
                    if text:
                        texts.append(text)

                if texts:
                    body = '\n\n'.join(texts)
                    property_data['description_body'] = body
                    print(f"      📝 Description body: {len(body)} characters")
                    return True

            # Method 2: Get direct container text
            body = container.text_content().strip() if container.text_content() else ''
            if body and len(body) > 50:
                property_data['description_body'] = body
                print(f"      📝 Description body: {len(body)} characters")
                return True

        except Exception as e:
            print(f"      Error extracting description body: {e}")

        return False

    def extract_agent_number_smart(self, container, property_data):
        """Smart extraction of agent phone number"""

        try:
            # Method 1: Look for tel: links
            tel_links = container.xpath('.//a[contains(@href, "tel:")]')
            for link in tel_links:
                href = link.get('href', '')
                if 'tel:' in href:
                    phone = href.replace('tel:', '').strip()
                    if len(phone) > 8:
                        property_data['agent_number'] = phone
                        print(f"      📞 Agent phone: {phone}")
                        return True

            # Method 2: Look for phone patterns in text
            text = container.text_content().strip() if container.text_content() else ''
            phone_patterns = [
                r'\b0[2-8]\s?\d{4}\s?\d{4}\b',  # Australian landline
                r'\b04\d{2}\s?\d{3}\s?\d{3}\b',  # Australian mobile
                r'\(\d{2}\)\s?\d{4}\s?\d{4}',    # (02) format
            ]

            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    phone = matches[0].strip()
                    property_data['agent_number'] = phone
                    print(f"      📞 Agent phone: {phone}")
                    return True

        except Exception as e:
            print(f"      Error extracting agent phone: {e}")

        return False

    def extract_property_id_smart(self, container, property_data):
        """Smart extraction of property ID"""

        try:
            # For text() nodes, container might be the text itself
            if isinstance(container, str):
                text = container.strip()
            else:
                text = container.text_content().strip() if container.text_content() else ''

            # Look for property ID pattern
            if text and text.isdigit() and len(text) >= 8:
                property_data['property_id'] = text
                print(f"      🆔 Property ID: {text}")
                return True

        except Exception as e:
            print(f"      Error extracting property ID: {e}")

        return False

    def extract_agent_picture_smart(self, container, property_data):
        """Smart extraction of agent picture"""

        try:
            # Look for image src
            img = container.xpath('.//img')[0] if container.xpath('.//img') else None
            if img is not None:
                src = img.get('src', '')
                if src:
                    property_data['agent_picture'] = src
                    print(f"      🖼️ Agent picture: {src}")
                    return True

            # Look for href (profile link)
            href = container.get('href', '')
            if href and 'agent' in href:
                property_data['agent_picture'] = href
                print(f"      🖼️ Agent picture link: {href}")
                return True

        except Exception as e:
            print(f"      Error extracting agent picture: {e}")

        return False

    def is_valid_highlight(self, text):
        """Check if text is a valid property highlight"""
        text_lower = text.lower()
        invalid_phrases = ['click', 'view', 'contact', 'phone', 'email', 'website']
        return not any(phrase in text_lower for phrase in invalid_phrases)

    def is_valid_feature(self, text):
        """Check if text is a valid property feature"""
        text_lower = text.lower()
        invalid_phrases = ['click', 'view', 'contact', 'phone', 'email', 'website', 'javascript']
        return not any(phrase in text_lower for phrase in invalid_phrases)

    def process_field_value(self, field_name, value, property_data):
        """Process and clean extracted value"""

        value = value.strip()

        if field_name in ['bedrooms', 'bathrooms', 'car_spaces']:
            if value.isdigit():
                property_data[field_name] = int(value)
        elif field_name == 'full_address':
            property_data['title'] = value
            property_data['address'] = value
            property_data['full_address'] = value
        elif field_name == 'offer':
            property_data['offer'] = value
        elif field_name == 'land_size':
            property_data[field_name] = value.replace('mÂ²', 'm²')
        else:
            property_data[field_name] = value

    def add_meta_fallbacks(self, soup, property_data):
        """Add meta tag fallbacks for missing data"""

        # Description from og:description if not found in containers
        if 'description_body' not in property_data or not property_data['description_body']:
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                raw_desc = og_desc.get('content', '')
                clean_desc = html.unescape(raw_desc).replace('&lt;br/&gt;', '\n').replace('<br/>', '\n')
                property_data['description'] = clean_desc
                property_data['description_body'] = clean_desc
                print(f"  ✅ Description from og:description: {len(clean_desc)} chars")

        # Title from og:title if not found
        if 'title' not in property_data:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                property_data['title'] = og_title.get('content', '')
                property_data['address'] = og_title.get('content', '')
                print(f"  ✅ Title from og:title: {property_data['title']}")

    def extract_property_images(self, soup):
        """Extract property images"""

        images = []

        # og:image
        og_image = soup.find('meta', property='og:image')
        if og_image:
            img_url = og_image.get('content')
            if img_url and 'i2.au.reastatic.net' in img_url:
                images.append({'url': img_url, 'type': 'main_photo'})

        # All reastatic URLs
        page_content = str(soup)
        reastatic_urls = re.findall(r'https://i2\.au\.reastatic\.net/[^"\'>\s]+', page_content)

        for url in set(reastatic_urls):
            if 'logo' not in url.lower() and len(url) > 50:
                images.append({'url': url, 'type': 'property_photo'})

        return images

    def extract_property_id_from_url(self, url):
        """Extract property ID from URL"""
        match = re.search(r'-(\d{8,10})(?:\?|#|$)', url)
        return match.group(1) if match else 'unknown'

    def save_html_for_debug(self, html_content, property_id):
        """Save HTML for debugging"""
        debug_dir = Path("data/html_inspection")
        debug_dir.mkdir(parents=True, exist_ok=True)

        html_file = debug_dir / f"{property_id}_refined_debug.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"  💾 Debug HTML saved: {html_file}")

    def save_property_data(self, property_data, property_id):
        """Save property data"""
        data_dir = Path("data/properties")
        data_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{property_id}_refined_complete.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Property data saved: {filepath}")

    def print_extraction_summary(self, property_data, working_count, priority_count, other_count):
        """Print comprehensive extraction summary"""

        print(f"\n🎉 REFINED EXTRACTION SUMMARY")
        print("="*50)
        print(f"  Working XPath successes: {working_count}/9")
        print(f"  Priority container successes: {priority_count}/2 (property_highlights, property_features)")
        print(f"  Other container successes: {other_count}/6")
        print(f"  Total fields extracted: {len(property_data)}")

        print(f"\n📊 EXTRACTED DATA:")
        print(f"  Property ID: {property_data.get('id')}")
        print(f"  Title: {property_data.get('title', 'Missing')}")
        print(f"  Offer: {property_data.get('offer', 'Missing')}")
        print(f"  Bedrooms: {property_data.get('bedrooms', 'Missing')}")
        print(f"  Bathrooms: {property_data.get('bathrooms', 'Missing')}")
        print(f"  Car Spaces: {property_data.get('car_spaces', 'Missing')}")
        print(f"  Land Size: {property_data.get('land_size', 'Missing')}")
        print(f"  Agent: {property_data.get('agent_name', 'Missing')}")
        print(f"  Agent Phone: {property_data.get('agent_number', 'Missing')}")
        print(f"  Agency: {property_data.get('agency_name', 'Missing')}")
        print(f"  Agency Address: {property_data.get('agency_address', 'Missing')}")

        print(f"\n📝 CONTAINER EXTRACTIONS:")
        print(f"  Description Title: {property_data.get('description_title', 'Missing')}")
        print(f"  Description Body: {len(property_data.get('description_body', ''))} chars")
        print(f"  Property ID: {property_data.get('property_id', 'Missing')}")
        print(f"  Property Features: {len(property_data.get('property_features', []))} items")
        print(f"  Property Highlights: {len(property_data.get('property_highlights', []))} items")
        print(f"  Inspections: {len(property_data.get('inspections', []))} scheduled")
        print(f"  Agent Picture: {'Found' if property_data.get('agent_picture') else 'Missing'}")
        print(f"  Images: {len(property_data.get('images', []))} found")

        # Show samples
        if property_data.get('property_features'):
            print(f"\n  Sample features: {property_data['property_features'][:3]}")

        if property_data.get('property_highlights'):
            print(f"  Sample highlights: {property_data['property_highlights'][:2]}")

        if property_data.get('inspections'):
            for i, insp in enumerate(property_data['inspections'][:2]):
                print(f"  Inspection {i+1}: {insp.get('time', 'TBD')}")


def test_refined_extraction():
    """Test refined container-based extraction"""

    print("🚀 TESTING REFINED XPATH CONTAINER EXTRACTION")
    print("="*70)

    extractor = RefinedXPathExtractor()
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    success, data = extractor.extract_property_refined(test_url)

    if success:
        print(f"\n🎯 REFINED EXTRACTION COMPLETE!")
        print("All your XPaths have been tested with intelligent container extraction")
        return True
    else:
        print(f"\n❌ Refined extraction failed")
        return False


if __name__ == "__main__":
    test_refined_extraction()