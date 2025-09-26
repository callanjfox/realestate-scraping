#!/usr/bin/env python3
"""
Perfect Single Property Extraction using EXACT working configuration
Focus: Use proven ScrapingBee config to get complete property details + images
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


def test_single_property_with_exact_config():
    """Test single property using exact working configuration"""

    print("🎯 PERFECT SINGLE PROPERTY EXTRACTION")
    print("Using EXACT working ScrapingBee configuration")
    print("="*70)

    # New API key with 1000 credits
    api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
    client = ScrapingBeeClient(api_key=api_key)

    # EXACT working configuration (proven to return 200)
    working_params = {
        'render_js': True,
        'block_resources': False,
        'stealth_proxy': True,
        'country_code': 'AU'
    }

    print(f"🐝 Using proven working parameters:")
    for key, value in working_params.items():
        print(f"  {key}: {value}")

    # Test with known working property URL
    property_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"
    print(f"\n🏠 Target property: {property_url}")

    try:
        print(f"\n📡 Making ScrapingBee request...")
        start_time = time.time()

        response = client.get(property_url, params=working_params, timeout=120)

        request_time = time.time() - start_time

        print(f"⏱️ Request time: {request_time:.1f} seconds")
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Content length: {len(response.content)}")

        if response.status_code == 200:
            print("🚀 SUCCESS! Individual property page accessible!")

            # Extract complete details
            property_details = extract_complete_details(response.text, property_url)

            if property_details:
                # Download images
                if property_details.get('images'):
                    downloaded_images = download_images_efficiently(property_details)
                    property_details['downloaded_images'] = downloaded_images

                # Save perfect property
                saved = save_perfect_property_data(property_details)

                if saved:
                    print(f"\n🎉 SINGLE PROPERTY PERFECTION COMPLETE!")
                    print(f"📊 COMPLETE DATA EXTRACTED:")
                    print(f"  Title: {property_details.get('title', 'Missing')}")
                    print(f"  Price: {property_details.get('price', 'Missing')}")
                    print(f"  Bedrooms: {property_details.get('bedrooms', 'Missing')}")
                    print(f"  Bathrooms: {property_details.get('bathrooms', 'Missing')}")
                    print(f"  Parking: {property_details.get('parking', 'Missing')}")
                    print(f"  Description: {len(property_details.get('description', ''))} chars")
                    print(f"  Features: {len(property_details.get('features', []))} items")
                    print(f"  Images found: {len(property_details.get('images', []))}")
                    print(f"  Images downloaded: {len(property_details.get('downloaded_images', []))}")
                    print(f"  Agent: {property_details.get('agent', {}).get('name', 'Missing')}")

                    print(f"\n💳 Credit usage: 1 request with stealth_proxy")
                    print(f"🎯 Credit efficiency: Optimal for individual properties")

                    return True, property_details

        elif response.status_code == 500:
            print("❌ Server error (500)")
            print(f"Error: {response.text}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    return False, None


def extract_complete_details(html_content, property_url):
    """Extract ALL possible details from property page"""

    print("\n📝 EXTRACTING COMPLETE PROPERTY DETAILS")
    print("="*50)

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        property_details = {
            'id': extract_property_id(property_url),
            'url': property_url,
            'scraped_at': datetime.now(timezone.utc).isoformat()
        }

        # 1. TITLE/ADDRESS
        print("  🏠 Title/Address...")
        title_selectors = ['h1', '.property-title', '[data-testid*="address"]']
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 10:
                    property_details['title'] = title
                    print(f"    ✅ {title}")
                    break

        # 2. PRICE
        print("  💰 Price...")
        price_selectors = [
            '.property-price',
            '[data-testid*="price"]',
            '[class*="price"]',
            '.price-wrapper'
        ]
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem:
                price = elem.get_text(strip=True)
                if price and ('$' in price or 'auction' in price.lower()):
                    property_details['price'] = price
                    print(f"    ✅ {price}")
                    break

        # 3. BEDROOMS, BATHROOMS, PARKING
        print("  🛏️ Bedrooms, Bathrooms, Parking...")
        extract_features_comprehensive(soup, property_details)

        # 4. DESCRIPTION
        print("  📄 Description...")
        desc_selectors = [
            '.property-description',
            '[data-testid*="description"]',
            '.description',
            '.property-content'
        ]
        descriptions = []
        for selector in desc_selectors:
            elements = soup.select(f'{selector} p, {selector}')
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:
                        descriptions.append(text)
                if descriptions:
                    break

        if descriptions:
            property_details['description'] = ' '.join(descriptions)
            print(f"    ✅ {len(property_details['description'])} characters")

        # 5. FEATURES
        print("  📋 Features...")
        features = extract_feature_list(soup)
        if features:
            property_details['features'] = features
            print(f"    ✅ {len(features)} features")

        # 6. IMAGES
        print("  📸 Images...")
        images = extract_property_images(soup)
        if images:
            property_details['images'] = images
            print(f"    ✅ {len(images)} images found")

        # 7. AGENT
        print("  👤 Agent...")
        agent = extract_agent_info(soup)
        if agent:
            property_details['agent'] = agent
            print(f"    ✅ Agent: {agent.get('name', 'Unknown')}")

        # 8. PROPERTY TYPE
        property_details['property_type'] = determine_property_type(soup, property_url)
        print(f"  🏘️ Type: {property_details['property_type']}")

        return property_details

    except Exception as e:
        print(f"❌ Detail extraction failed: {e}")
        return None


def extract_features_comprehensive(soup, property_details):
    """Extract bedrooms, bathrooms, parking comprehensively"""

    # Get all page text
    page_text = soup.get_text().lower()

    # Bedrooms
    bed_patterns = [r'(\d+)\s*bed(?:room)?s?', r'(\d+)\s*br\b']
    for pattern in bed_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            valid_beds = [int(m) for m in matches if 1 <= int(m) <= 10]
            if valid_beds:
                property_details['bedrooms'] = valid_beds[0]
                print(f"    ✅ Bedrooms: {valid_beds[0]}")
                break

    # Bathrooms
    bath_patterns = [r'(\d+)\s*bath(?:room)?s?', r'(\d+)\s*ba\b']
    for pattern in bath_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            valid_baths = [int(m) for m in matches if 1 <= int(m) <= 10]
            if valid_baths:
                property_details['bathrooms'] = valid_baths[0]
                print(f"    ✅ Bathrooms: {valid_baths[0]}")
                break

    # Parking
    park_patterns = [r'(\d+)\s*car', r'(\d+)\s*garage', r'(\d+)\s*parking']
    for pattern in park_patterns:
        matches = re.findall(pattern, page_text)
        if matches:
            valid_parking = [int(m) for m in matches if 1 <= int(m) <= 10]
            if valid_parking:
                property_details['parking'] = valid_parking[0]
                print(f"    ✅ Parking: {valid_parking[0]}")
                break


def extract_feature_list(soup):
    """Extract property features list"""
    selectors = ['.property-features li', '.features li', '[data-testid*="features"] li']
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            return [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
    return []


def extract_property_images(soup):
    """Extract all property images"""
    img_selectors = [
        '.property-gallery img',
        '[data-testid*="gallery"] img',
        '.property-images img',
        'img[src*="property"]'
    ]

    images = []
    for selector in img_selectors:
        img_elements = soup.select(selector)
        if img_elements:
            for img in img_elements:
                src = img.get('src') or img.get('data-src')
                if src and not src.startswith('data:'):
                    if src.startswith('/'):
                        src = urljoin('https://www.realestate.com.au', src)
                    images.append({
                        'url': src,
                        'alt': img.get('alt', 'Property image')
                    })
            break

    return images[:15]  # Limit to 15 images


def extract_agent_info(soup):
    """Extract agent information"""
    agent_selectors = ['.agent-info', '.listing-agent', '[data-testid*="agent"]']
    for selector in agent_selectors:
        agent_elem = soup.select_one(selector)
        if agent_elem:
            name_elem = agent_elem.find(['h3', 'h4'])
            if name_elem:
                return {'name': name_elem.get_text(strip=True)}
    return {}


def determine_property_type(soup, url):
    """Determine property type"""
    url_lower = url.lower()
    if 'house' in url_lower:
        return 'house'
    elif 'apartment' in url_lower or 'unit' in url_lower:
        return 'apartment'
    elif 'townhouse' in url_lower:
        return 'townhouse'
    return 'unknown'


def extract_property_id(url):
    """Extract property ID"""
    patterns = [r'-(\d+)(?:\?|#|$)', r'property-[^-]+-[^-]+-[^-]+-(\d+)']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return f"perfect_{random.randint(10000, 99999)}"


def download_images_efficiently(property_details):
    """Download images efficiently"""
    property_id = property_details['id']
    images = property_details.get('images', [])

    if not images:
        return []

    images_dir = Path(f"data/images/{property_id}")
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"    📸 Downloading {len(images)} images...")

    downloaded = []
    for i, img_info in enumerate(images[:10]):  # Limit to 10
        try:
            img_response = requests.get(img_info['url'], timeout=30, verify=False)
            if img_response.status_code == 200:
                filename = f"image_{i+1:03d}.jpg"
                filepath = images_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

                downloaded.append({
                    'url': img_info['url'],
                    'local_path': str(filepath),
                    'filename': filename,
                    'size': len(img_response.content)
                })

                print(f"      ✅ {filename} ({len(img_response.content)} bytes)")

        except Exception as e:
            print(f"      ❌ Image {i+1} failed: {e}")

    return downloaded


def save_perfect_property_data(property_details):
    """Save perfect property data"""

    data_dir = Path("data/properties")
    data_dir.mkdir(parents=True, exist_ok=True)

    property_id = property_details['id']
    filename = f"{property_id}_perfect_single.json"
    filepath = data_dir / filename

    # Create complete record
    complete_record = {
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
        'method': 'perfect_single_property_scrapingbee',
        'status': 'active',
        'address': {'full': property_details.get('title', '')},
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(complete_record, f, indent=2, ensure_ascii=False)

    print(f"💾 Saved perfect property: {filepath}")
    return True


def test_second_property():
    """Test second property to validate approach"""

    print(f"\n🔄 TESTING SECOND PROPERTY")
    print("="*50)

    api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
    client = ScrapingBeeClient(api_key=api_key)

    working_params = {
        'render_js': True,
        'block_resources': False,
        'stealth_proxy': True,
        'country_code': 'AU'
    }

    # Second property URL
    second_url = "https://www.realestate.com.au/property-apartment-qld-south+bank-148928524"
    print(f"🏠 Second property: {second_url}")

    try:
        response = client.get(second_url, params=working_params, timeout=120)

        print(f"📊 Status: {response.status_code}")
        print(f"📊 Content: {len(response.content)} bytes")

        if response.status_code == 200:
            print("✅ Second property accessible!")

            # Extract details
            details = extract_complete_details(response.text, second_url)

            if details:
                # Download images
                if details.get('images'):
                    downloaded = download_images_efficiently(details)
                    details['downloaded_images'] = downloaded

                # Save
                saved = save_perfect_property_data(details)

                if saved:
                    print(f"\n✅ SECOND PROPERTY COMPLETE!")
                    return True

        else:
            print(f"❌ Second property failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Second property error: {e}")

    return False


def main():
    """Main execution"""

    print("🚀 SINGLE PROPERTY PERFECTION WITH NEW API KEY")
    print("Focus: Complete details + images with credit efficiency")
    print("="*70)

    # Test first property
    success1, details1 = test_single_property_with_exact_config()

    if success1:
        print(f"\n🎯 FIRST PROPERTY PERFECTED!")

        # Test second property
        success2 = test_second_property()

        if success2:
            print(f"\n🏆 TWO PROPERTIES PERFECTED!")
            print("Approach validated and ready for scaling")

            print(f"\n📋 INSPECT YOUR PERFECT DATA:")
            print(f"  python3 view_data.py 5")
            print(f"  ls data/images/")
            print(f"  cat data/properties/*_perfect_single.json")

            return True

    return False


if __name__ == "__main__":
    success = main()

    if success:
        print(f"\n🎉 PROPERTY PERFECTION ACHIEVED!")
        print("Ready to scale to more properties with complete details")
    else:
        print(f"\n⚠️ Need to debug property perfection approach")