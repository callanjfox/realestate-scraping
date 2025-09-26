#!/usr/bin/env python3
"""
XPath Validation Test - Verify all provided XPath selectors work correctly
Tests the specific property: https://www.realestate.com.au/property-house-qld-wilston-149008036
"""

from scrapingbee import ScrapingBeeClient
from lxml import html, etree
import json
from pathlib import Path
import re

class XPathValidationTest:
    """Test class to validate all provided XPath selectors"""

    def __init__(self):
        self.api_key = "NPI86EDJ0YRYGC3L4ZRSOI7I2TEBFT6HWHOZF0YOJDHE9G49YA2SEUELJ0P5WFRPFN4SDF4POKYQWSZC"
        self.client = ScrapingBeeClient(api_key=self.api_key)

        # XPath selectors provided by user
        self.xpath_selectors = {
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

    def fetch_property_html(self, property_url):
        """Fetch property HTML using ScrapingBee"""

        print(f"🌐 Fetching property: {property_url}")

        params = {
            'render_js': True,
            'block_resources': False,
            'stealth_proxy': True,
            'country_code': 'AU'
        }

        try:
            response = self.client.get(property_url, params=params, timeout=120)

            if response.status_code == 200:
                print(f"✅ Successfully fetched HTML ({len(response.text):,} chars)")

                # Save HTML for inspection
                property_id = self.extract_property_id_from_url(property_url)
                html_file = Path(f"data/html_inspection/{property_id}_xpath_test.html")
                html_file.parent.mkdir(parents=True, exist_ok=True)

                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 HTML saved to: {html_file}")

                return response.text
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    def validate_xpath_selectors(self, html_content):
        """Validate all XPath selectors against the HTML"""

        print(f"\n🔍 VALIDATING XPATH SELECTORS")
        print("="*60)

        # Parse HTML with lxml
        try:
            tree = html.fromstring(html_content)
        except Exception as e:
            print(f"❌ Failed to parse HTML: {e}")
            return {}

        results = {}

        for field_name, xpath in self.xpath_selectors.items():
            try:
                print(f"\n🎯 Testing: {field_name}")
                print(f"   XPath: {xpath}")

                # Execute XPath
                elements = tree.xpath(xpath)

                if elements:
                    if isinstance(elements[0], str):
                        # Text node result
                        value = elements[0].strip()
                        results[field_name] = {
                            'success': True,
                            'value': value,
                            'type': 'text',
                            'count': len(elements)
                        }
                        print(f"   ✅ Found text: '{value}'")

                    elif hasattr(elements[0], 'text'):
                        # Element result
                        value = elements[0].text_content().strip() if elements[0].text_content() else ''

                        # For container elements that might have multiple children
                        if field_name in ['property_highlights', 'property_features', 'inspections']:
                            # Get all child text content
                            child_texts = []
                            for child in elements[0].xpath('.//text()'):
                                child_text = child.strip()
                                if child_text:
                                    child_texts.append(child_text)

                            results[field_name] = {
                                'success': True,
                                'value': value,
                                'children': child_texts,
                                'type': 'container',
                                'count': len(elements)
                            }
                            print(f"   ✅ Found container with {len(child_texts)} children")
                            print(f"   📝 First few: {child_texts[:3]}")

                        else:
                            results[field_name] = {
                                'success': True,
                                'value': value,
                                'type': 'element',
                                'count': len(elements)
                            }
                            print(f"   ✅ Found element: '{value}'")

                    # Handle special cases
                    if field_name == 'agent_picture' and elements:
                        # Extract image URL from href or src
                        href = elements[0].get('href', '')
                        src = elements[0].get('src', '')
                        results[field_name]['href'] = href
                        results[field_name]['src'] = src
                        print(f"   🖼️ Image href: {href}")
                        print(f"   🖼️ Image src: {src}")

                else:
                    results[field_name] = {
                        'success': False,
                        'value': None,
                        'type': 'missing',
                        'count': 0
                    }
                    print(f"   ❌ Not found")

            except Exception as e:
                results[field_name] = {
                    'success': False,
                    'error': str(e),
                    'type': 'error'
                }
                print(f"   ❌ XPath error: {e}")

        return results

    def extract_images_from_html(self, html_content):
        """Extract all property images from HTML"""

        print(f"\n📸 EXTRACTING PROPERTY IMAGES")
        print("="*40)

        # Use existing image extraction method
        images = []

        # Look for og:image meta tag
        og_image_pattern = r'<meta property="og:image" content="([^"]+)"'
        og_match = re.search(og_image_pattern, html_content)
        if og_match:
            images.append({
                'url': og_match.group(1),
                'type': 'og_image',
                'source': 'meta_tag'
            })
            print(f"✅ Found og:image: {og_match.group(1)}")

        # Look for all i2.au.reastatic.net URLs
        reastatic_pattern = r'https://i2\.au\.reastatic\.net/[^"\'>\s]+'
        reastatic_urls = re.findall(reastatic_pattern, html_content)

        for url in set(reastatic_urls):  # Remove duplicates
            if 'logo' not in url.lower() and len(url) > 50:
                images.append({
                    'url': url,
                    'type': 'property_photo',
                    'source': 'reastatic_cdn'
                })

        print(f"✅ Found {len(images)} total images")
        return images

    def extract_property_id_from_url(self, url):
        """Extract property ID from URL"""
        match = re.search(r'-(\d{8,10})(?:\?|#|$)', url)
        if match:
            return match.group(1)
        return 'unknown'

    def save_validation_results(self, results, images, property_url):
        """Save validation results to JSON"""

        property_id = self.extract_property_id_from_url(property_url)

        output_data = {
            'property_url': property_url,
            'property_id': property_id,
            'validation_results': results,
            'extracted_images': images,
            'summary': {
                'total_fields': len(results),
                'successful_fields': len([r for r in results.values() if r.get('success')]),
                'failed_fields': len([r for r in results.values() if not r.get('success')]),
                'total_images': len(images)
            }
        }

        # Save results
        results_dir = Path("data/xpath_validation")
        results_dir.mkdir(parents=True, exist_ok=True)

        results_file = results_dir / f"{property_id}_xpath_validation.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Validation results saved to: {results_file}")
        return output_data

    def print_validation_summary(self, results, images):
        """Print comprehensive validation summary"""

        print(f"\n🎉 XPATH VALIDATION SUMMARY")
        print("="*50)

        successful = [field for field, result in results.items() if result.get('success')]
        failed = [field for field, result in results.items() if not result.get('success')]

        print(f"✅ Successful fields: {len(successful)}/{len(results)}")
        print(f"❌ Failed fields: {len(failed)}")
        print(f"📸 Images found: {len(images)}")

        if successful:
            print(f"\n✅ WORKING XPATHS:")
            for field in successful:
                value = results[field]['value']
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"  • {field}: {value}")

        if failed:
            print(f"\n❌ FAILED XPATHS:")
            for field in failed:
                error = results[field].get('error', 'Not found')
                print(f"  • {field}: {error}")

        print(f"\n📸 SAMPLE IMAGES:")
        for i, img in enumerate(images[:5]):
            print(f"  {i+1}. {img['type']}: {img['url']}")


def run_xpath_validation():
    """Run complete XPath validation test"""

    print("🧪 XPATH VALIDATION TEST")
    print("Testing all provided XPath selectors")
    print("="*70)

    validator = XPathValidationTest()

    # Test the specific property
    test_url = "https://www.realestate.com.au/property-house-qld-wilston-149008036"

    # Fetch HTML
    html_content = validator.fetch_property_html(test_url)

    if html_content:
        # Validate XPath selectors
        results = validator.validate_xpath_selectors(html_content)

        # Extract images
        images = validator.extract_images_from_html(html_content)

        # Save results
        output_data = validator.save_validation_results(results, images, test_url)

        # Print summary
        validator.print_validation_summary(results, images)

        return True, output_data

    return False, None


if __name__ == "__main__":
    success, data = run_xpath_validation()

    if success:
        print(f"\n🎯 VALIDATION COMPLETE!")
        print("Check data/xpath_validation/ for detailed results")
        print("Check data/html_inspection/ for raw HTML")
    else:
        print(f"\n⚠️ Validation failed")