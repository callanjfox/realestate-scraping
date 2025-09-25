#!/usr/bin/env python3
"""
Debug ScrapingBee API calls to understand the 400 error
"""

from scrapingbee import ScrapingBeeClient
import json


def debug_scrapingbee_api():
    """Debug ScrapingBee API response"""

    api_key = "PJD8I9K7SMRHKW86IK6WNZ8LPZ2ALCFRP4MKDXAJ0DNCUQX6VJ1HHIZBJN1K40VKSZERRFRJD8YF6GAX"

    print("🐝 DEBUGGING SCRAPINGBEE API")
    print("="*50)

    client = ScrapingBeeClient(api_key=api_key)

    # Test 1: Simple request without advanced parameters
    print("🧪 Test 1: Simple request")
    try:
        response = client.get(
            'https://httpbin.org/ip',  # Test with simple endpoint first
            params={},
            timeout=30
        )

        print(f"  Status: {response.status_code}")
        print(f"  Content: {response.text}")

        if response.status_code == 200:
            print("✅ ScrapingBee API key working!")

            # Test 2: Simple realestate.com.au request
            print("\n🧪 Test 2: Simple realestate.com.au request")

            simple_response = client.get(
                'https://www.realestate.com.au/',
                params={'render_js': False},  # Start simple
                timeout=30
            )

            print(f"  Status: {simple_response.status_code}")
            print(f"  Content length: {len(simple_response.content)}")

            if simple_response.status_code == 200:
                print("✅ Simple realestate.com.au access successful!")

                # Test 3: Add JavaScript rendering
                print("\n🧪 Test 3: With JavaScript rendering")

                js_response = client.get(
                    'https://www.realestate.com.au/',
                    params={'render_js': True},
                    timeout=60
                )

                print(f"  Status: {js_response.status_code}")
                print(f"  Content length: {len(js_response.content)}")

                if js_response.status_code == 200:
                    print("✅ JavaScript rendering successful!")

                    # Test 4: Full Brisbane property listing
                    print("\n🧪 Test 4: Brisbane property listings")

                    full_response = client.get(
                        'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1',
                        params={
                            'render_js': True,
                            'premium_proxy': True,
                            'country_code': 'AU',
                        },
                        timeout=90
                    )

                    print(f"  Status: {full_response.status_code}")
                    print(f"  Content length: {len(full_response.content)}")

                    if full_response.status_code == 200:
                        print("🚀 FULL BREAKTHROUGH!")

                        # Check content
                        content = full_response.text.lower()
                        property_indicators = ['property', 'bedroom', 'bathroom', 'real estate']
                        found = [ind for ind in property_indicators if ind in content]

                        print(f"  Property indicators: {found}")

                        if len(found) >= 3:
                            print("🎯 PROPERTY CONTENT CONFIRMED!")
                            return True, full_response.text

                    elif full_response.status_code == 429:
                        print("❌ Still rate limited")
                    else:
                        print(f"❌ Failed: {full_response.status_code}")
                        print(f"Response: {full_response.text}")

            else:
                print(f"❌ JS rendering failed: {js_response.status_code}")
                print(f"Response: {js_response.text}")

        else:
            print(f"❌ Simple request failed: {simple_response.status_code}")
            print(f"Response: {simple_response.text}")

    except Exception as e:
        print(f"❌ API test failed: {e}")

    return False, None


if __name__ == "__main__":
    success, content = debug_scrapingbee_api()

    if success:
        print(f"\n🎉 SCRAPINGBEE WORKING!")
        print("Ready to implement production scraping")

        # Quick property extraction test
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Quick count of potential properties
            selectors = ['article', '[class*="card"]', '[class*="property"]', '[class*="listing"]']
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"Found {len(elements)} potential property elements with: {selector}")
                    break

    else:
        print(f"\n⚠️ ScrapingBee API issues - checking error response")