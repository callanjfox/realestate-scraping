#!/usr/bin/env python3
"""
Use exact working ScrapingBee configuration that returned 200
"""

from scrapingbee import ScrapingBeeClient
import time
import json
import random
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def test_exact_working_config():
    """Use the exact configuration that worked (returned 200 with 454 properties)"""

    print("🎯 USING EXACT WORKING SCRAPINGBEE CONFIGURATION")
    print("Configuration that returned HTTP 200 with 454 properties")
    print("="*70)

    api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"
    client = ScrapingBeeClient(api_key=api_key)

    # EXACT parameters that worked
    working_params = {
        'render_js': True,
        'block_resources': False,
        'stealth_proxy': True,
        'country_code': 'AU'
    }

    print(f"🐝 Using exact working parameters:")
    for key, value in working_params.items():
        print(f"  {key}: {value}")

    try:
        print(f"\n📍 Testing exact working configuration...")

        start_time = time.time()

        response = client.get(
            'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
            params=working_params,
            timeout=120
        )

        request_time = time.time() - start_time

        print(f"⏱️ Request time: {request_time:.1f} seconds")
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Content length: {len(response.content)}")

        if response.status_code == 200:
            print("🚀 EXACT CONFIGURATION CONFIRMED WORKING!")

            # Extract properties immediately
            properties = extract_properties_from_working_response(response.text)

            if properties:
                print(f"✅ Extracted {len(properties)} properties!")

                # Save properties
                saved = save_working_properties(properties)

                print(f"💾 Saved {saved} properties")

                # Calculate scaling
                print(f"\n📈 SCALING CALCULATIONS:")
                print(f"  Properties per page: {len(properties)}")
                print(f"  Time per page: {request_time:.1f}s")
                print(f"  Pages for 100 properties: {100 // len(properties) + 1}")
                print(f"  Total time for 100: {((100 // len(properties) + 1) * request_time)/60:.1f} minutes")
                print(f"  Credits for 100: ~{(100 // len(properties) + 1) * 75}")

                if saved >= 10:
                    print(f"🎯 READY FOR FULL 100-PROPERTY SCRAPE!")
                    return True, working_params

            else:
                print("⚠️ No properties extracted despite 200 response")

        elif response.status_code == 400:
            print("❌ Configuration now returning 400")
            print(f"Response: {response.text}")
        elif response.status_code == 500:
            print("❌ Server error")
            print(f"Error: {response.text}")
        else:
            print(f"❌ Unexpected status: {response.status_code}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

    return False, {}


def extract_properties_from_working_response(html_content):
    """Extract properties from confirmed working response"""

    print("📝 Extracting properties from working response...")

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Use all possible selectors
        all_selectors = [
            '[data-testid="residential-card"]',
            'article[data-testid="residential-card"]',
            '[class*="residential-card"]',
            '.listing-result',
            'article',
            '[class*="property"]',
            '[class*="card"]',
            '[class*="listing"]'
        ]

        properties = []

        for selector in all_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  Trying selector: {selector} ({len(elements)} elements)")

                for i, element in enumerate(elements[:30]):  # Extract up to 30 per page
                    try:
                        prop_data = {}

                        # Extract text content for analysis
                        element_text = element.get_text(separator=' ', strip=True)

                        # Look for address patterns
                        import re
                        address_patterns = [
                            r'(\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Place|Pl|Court|Ct))',
                            r'([A-Za-z\s]+,\s*[A-Za-z\s]+,?\s*(?:QLD|NSW|VIC|SA|WA|TAS|NT|ACT))',
                        ]

                        for pattern in address_patterns:
                            match = re.search(pattern, element_text, re.IGNORECASE)
                            if match:
                                prop_data['title'] = match.group(1).strip()
                                break

                        # If no address pattern, use longer text segments
                        if not prop_data.get('title'):
                            text_segments = [t.strip() for t in element_text.split() if len(t.strip()) > 15]
                            if text_segments:
                                prop_data['title'] = text_segments[0]

                        # Extract price
                        price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', element_text)
                        if price_match:
                            prop_data['price'] = price_match.group(0)

                        # Extract URL
                        link_elem = element.find('a', href=True)
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('/'):
                                href = urljoin('https://www.realestate.com.au', href)
                            prop_data['url'] = href
                            prop_data['id'] = extract_id_from_url(href, i)

                        # Extract features
                        bed_match = re.search(r'(\d+)\s*(?:bed|br)', element_text, re.IGNORECASE)
                        bath_match = re.search(r'(\d+)\s*(?:bath|ba)', element_text, re.IGNORECASE)
                        car_match = re.search(r'(\d+)\s*(?:car|garage)', element_text, re.IGNORECASE)

                        if bed_match:
                            prop_data['bedrooms'] = int(bed_match.group(1))
                        if bath_match:
                            prop_data['bathrooms'] = int(bath_match.group(1))
                        if car_match:
                            prop_data['parking'] = int(car_match.group(1))

                        if prop_data.get('title') and len(prop_data['title']) > 10:
                            properties.append(prop_data)

                    except Exception as e:
                        continue

                print(f"    ✅ Extracted {len(properties)} properties with {selector}")

                if properties:
                    break  # Use first successful selector

        return properties

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return []


def extract_id_from_url(url, index):
    """Extract ID from URL with fallback"""
    import re
    match = re.search(r'/property/[^/]*?-(\d+)-', url)
    if match:
        return match.group(1)
    return f"working_{index}_{random.randint(10000, 99999)}"


def save_working_properties(properties):
    """Save properties from working configuration"""

    data_dir = Path("data/properties")
    data_dir.mkdir(parents=True, exist_ok=True)

    saved_count = 0
    timestamp = datetime.now(timezone.utc).isoformat()

    for prop in properties:
        try:
            property_id = prop.get('id', f"working_{random.randint(10000, 99999)}")

            detailed_prop = {
                'id': property_id,
                'url': prop.get('url', ''),
                'title': prop.get('title', ''),
                'price': prop.get('price', ''),
                'bedrooms': prop.get('bedrooms'),
                'bathrooms': prop.get('bathrooms'),
                'parking': prop.get('parking'),
                'scraped_at': timestamp,
                'method': 'scrapingbee_exact_working_config',
                'status': 'active',
                'address': {'full': prop.get('title', '')},
                'features': [],
                'images': [],
                'agent': {}
            }

            filename = f"{property_id}_working.json"
            filepath = data_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(detailed_prop, f, indent=2, ensure_ascii=False)

            saved_count += 1

        except Exception as e:
            continue

    return saved_count


def main():
    """Main execution"""

    # Test exact working configuration
    success, working_params = test_exact_working_config()

    if success:
        print(f"\n🚀 SCALING TO FULL PRODUCTION!")

        # Now scale to multiple pages
        print(f"\n🔄 Scaling to multiple pages...")

        api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"
        client = ScrapingBeeClient(api_key=api_key)

        all_properties = []
        credits_used = 1  # Already used 1 in test

        # Scrape 5 pages for 100+ properties
        for page_num in range(2, 7):  # Pages 2-6 (already did page 1)
            if credits_used >= 400:  # Conservative limit
                print(f"⚠️ Approaching credit limit at {credits_used}")
                break

            print(f"\n📄 Page {page_num}...")

            try:
                url = f'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-{page_num}'

                response = client.get(url, params=working_params, timeout=120)
                credits_used += 1

                print(f"  Status: {response.status_code} (Credits: {credits_used}/1000)")

                if response.status_code == 200:
                    page_properties = extract_properties_from_working_response(response.text)
                    if page_properties:
                        all_properties.extend(page_properties)
                        print(f"  ✅ Page {page_num}: {len(page_properties)} properties (Total: {len(all_properties)})")

                        if len(all_properties) >= 100:
                            print(f"🎯 100 PROPERTY TARGET REACHED!")
                            break

                else:
                    print(f"  ❌ Page {page_num} failed: {response.status_code}")

                # Delay between pages
                time.sleep(random.uniform(3, 8))

            except Exception as e:
                print(f"  ❌ Page {page_num} error: {e}")

        # Final results
        if all_properties:
            final_saved = save_working_properties(all_properties)

            print(f"\n🎉 FINAL SCRAPINGBEE RESULTS:")
            print(f"  Total properties: {len(all_properties)}")
            print(f"  Properties saved: {final_saved}")
            print(f"  Credits used: {credits_used}/1000")

            if final_saved >= 100:
                print(f"🏆 100-PROPERTY MISSION ACCOMPLISHED!")
            elif final_saved >= 50:
                print(f"🎯 EXCELLENT RESULTS: {final_saved} properties!")

            return True

    return False


if __name__ == "__main__":
    success = main()

    if success:
        print(f"\n🎉 SCRAPINGBEE KASADA BYPASS SUCCESSFUL!")
    else:
        print(f"\n⚠️ Need to debug ScrapingBee parameter issues")