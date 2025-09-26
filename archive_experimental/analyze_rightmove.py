#!/usr/bin/env python3
"""
Analyze RightMove UK site structure for property listings
"""
import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()


def analyze_rightmove():
    """Analyze RightMove site structure"""

    url = 'https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E87490'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    print("Analyzing RightMove UK structure...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")

        if response.status_code != 200:
            print("Failed to get content")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find property listings
        print("\n" + "="*60)
        print("LOOKING FOR PROPERTY LISTINGS")
        print("="*60)

        # Try various selectors for property cards
        selectors_to_try = [
            '.propertyCard',
            '.property-card',
            '[data-test*="property"]',
            '.searchResult',
            '.property-result',
            'article',
            '.listing',
            '.result'
        ]

        for selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"\nSelector '{selector}': Found {len(elements)} elements")

            if elements and len(elements) > 0:
                print("Sample element classes:", [el.get('class', []) for el in elements[:3]])

                # Analyze first element
                first = elements[0]
                print(f"\nFirst element structure:")
                print(f"Tag: {first.name}")
                print(f"Classes: {first.get('class', [])}")
                print(f"ID: {first.get('id', 'None')}")

                # Look for key property info in first element
                print(f"\nLooking for property details in first element:")

                # Price
                price_selectors = ['.price', '[data-test*="price"]', '.propertyCardPrice', 'span']
                for ps in price_selectors:
                    price_elem = first.select_one(ps)
                    if price_elem and '£' in price_elem.get_text():
                        print(f"Price found with '{ps}': {price_elem.get_text().strip()}")
                        break

                # Title/Address
                title_selectors = ['.propertyTitle', 'h2', '.address', '[data-test*="address"]']
                for ts in title_selectors:
                    title_elem = first.select_one(ts)
                    if title_elem:
                        text = title_elem.get_text().strip()
                        if text:
                            print(f"Title/Address found with '{ts}': {text[:100]}...")
                            break

                # Property details (bedrooms, etc)
                detail_selectors = ['.propertyDetails', '.bedroom', '.bathroom', 'span']
                for ds in detail_selectors:
                    detail_elems = first.select(ds)
                    for elem in detail_elems:
                        text = elem.get_text().strip().lower()
                        if any(word in text for word in ['bed', 'bath', 'bedroom', 'bathroom']):
                            print(f"Property details found with '{ds}': {text}")

                # URLs
                link_elem = first.select_one('a')
                if link_elem and link_elem.get('href'):
                    href = link_elem.get('href')
                    if href.startswith('/'):
                        href = 'https://www.rightmove.co.uk' + href
                    print(f"Property URL: {href}")

                break

        print(f"\n" + "="*60)
        print("PAGINATION CHECK")
        print("="*60)

        # Look for pagination
        pagination_selectors = ['.pagination', '.paging', '.page', '.next']
        for ps in pagination_selectors:
            pag_elements = soup.select(ps)
            if pag_elements:
                print(f"Pagination found with '{ps}': {len(pag_elements)} elements")

    except Exception as e:
        print(f"Error analyzing site: {e}")


if __name__ == "__main__":
    analyze_rightmove()