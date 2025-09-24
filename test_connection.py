#!/usr/bin/env python3
"""
Simple test script to verify web connection and basic scraper functionality
"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def test_basic_connection():
    """Test basic web connection"""
    print("Testing basic connection to realestate.com.au...")

    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(
                headless=False,  # Run in visible mode for debugging
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security'
                ]
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768}
            )

            page = await context.new_page()

            print("Navigating to homepage...")
            await page.goto('https://www.realestate.com.au', timeout=30000)

            # Take screenshot
            await page.screenshot(path='debug_homepage.png')
            print("Screenshot saved as debug_homepage.png")

            title = await page.title()
            print(f"Page title: {title}")

            # Test search page
            print("\nTesting search page...")
            search_url = 'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'
            await page.goto(search_url, timeout=30000)

            await page.screenshot(path='debug_search.png')
            print("Search page screenshot saved as debug_search.png")

            # Look for property cards with various selectors
            selectors_to_try = [
                '[data-testid="residential-card"]',
                'article[data-testid="residential-card"]',
                '[class*="residential-card"]',
                '.listing-result',
                '[data-testid*="card"]',
                'article[class*="card"]',
                'article',
                '[class*="property"]',
                '[class*="listing"]'
            ]

            for selector in selectors_to_try:
                count = await page.locator(selector).count()
                print(f"Selector '{selector}': {count} elements found")
                if count > 0:
                    break

            # Get page content for analysis
            content = await page.content()
            with open('debug_page_content.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("Page content saved as debug_page_content.html")

            print("\n✅ Basic connection test completed successfully!")

            await browser.close()
            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

async def test_with_proxy(proxy_server, proxy_user=None, proxy_pass=None):
    """Test connection with proxy"""
    print(f"Testing connection with proxy: {proxy_server}")

    async with async_playwright() as playwright:
        try:
            proxy_config = {'server': proxy_server}
            if proxy_user and proxy_pass:
                proxy_config.update({'username': proxy_user, 'password': proxy_pass})

            browser = await playwright.chromium.launch(
                headless=False,
                proxy=proxy_config
            )

            page = await browser.new_page()

            # Test IP location
            await page.goto('https://httpbin.org/ip', timeout=30000)
            content = await page.content()
            print("Your IP through proxy:")
            print(content)

            await browser.close()
            return True

        except Exception as e:
            print(f"❌ Proxy test failed: {e}")
            return False

def main():
    """Main test function"""
    print("Real Estate Scraper - Connection Test")
    print("="*50)

    if len(sys.argv) > 1 and sys.argv[1] == '--proxy':
        if len(sys.argv) < 3:
            print("Usage: python test_connection.py --proxy <proxy_server> [username] [password]")
            sys.exit(1)

        proxy_server = sys.argv[2]
        proxy_user = sys.argv[3] if len(sys.argv) > 3 else None
        proxy_pass = sys.argv[4] if len(sys.argv) > 4 else None

        success = asyncio.run(test_with_proxy(proxy_server, proxy_user, proxy_pass))
    else:
        success = asyncio.run(test_basic_connection())

    if success:
        print("\n🎉 All tests passed! The scraper should work.")
    else:
        print("\n⚠️  Tests failed. Check the debug files and error messages.")

    print("\nNext steps:")
    print("1. Review debug screenshots and HTML content")
    print("2. If tests pass, run: python main.py full --max-properties 10")
    print("3. For proxy usage: python main.py full --max-properties 10 --proxy-server <proxy_url>")

if __name__ == "__main__":
    main()