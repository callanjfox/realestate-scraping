#!/usr/bin/env python3
"""
Real Estate Scraper for realestate.com.au
Handles property listings and detailed property information with anti-bot measures.
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict

import aiohttp
import aiofiles
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


@dataclass
class PropertyBasic:
    """Basic property information from listing page"""
    id: str
    url: str
    title: str
    price: str
    address: str
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None


@dataclass
class PropertyDetailed:
    """Detailed property information from property page"""
    id: str
    url: str
    scraped_at: str
    last_updated: str
    title: str
    price: str
    address: Dict[str, str]
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None
    land_size: Optional[str] = None
    building_size: Optional[str] = None
    description: str = ""
    features: List[str] = None
    images: List[Dict[str, str]] = None
    agent: Dict[str, str] = None
    listing_date: Optional[str] = None
    status: str = "active"

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.images is None:
            self.images = []
        if self.agent is None:
            self.agent = {}


class RealEstateScraper:
    """Main scraper class with anti-bot protection"""

    def __init__(self, data_dir: str = "data", max_properties: int = 100, proxy_config: Optional[Dict] = None):
        self.data_dir = Path(data_dir)
        self.max_properties = max_properties
        self.proxy_config = proxy_config
        self.scraped_properties: Set[str] = set()
        self.failed_properties: Set[str] = set()

        # Create directories
        self.properties_dir = self.data_dir / "properties"
        self.images_dir = self.data_dir / "images"
        self.logs_dir = self.data_dir / "logs"

        for dir_path in [self.properties_dir, self.images_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load existing state
        self._load_state()

    def _load_state(self):
        """Load existing scraped properties and failed attempts"""
        try:
            scraped_file = self.logs_dir / "scraped_properties.json"
            if scraped_file.exists():
                with open(scraped_file, 'r') as f:
                    self.scraped_properties = set(json.load(f))

            failed_file = self.logs_dir / "failed_properties.json"
            if failed_file.exists():
                with open(failed_file, 'r') as f:
                    self.failed_properties = set(json.load(f))

        except Exception as e:
            self.logger.warning(f"Error loading state: {e}")

    def _save_state(self):
        """Save current state to files"""
        try:
            with open(self.logs_dir / "scraped_properties.json", 'w') as f:
                json.dump(list(self.scraped_properties), f, indent=2)

            with open(self.logs_dir / "failed_properties.json", 'w') as f:
                json.dump(list(self.failed_properties), f, indent=2)

            with open(self.logs_dir / "last_sync.json", 'w') as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "scraped_count": len(self.scraped_properties),
                    "failed_count": len(self.failed_properties)
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    async def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def _setup_browser_page(self, browser: Browser) -> Page:
        """Setup browser page with realistic settings and anti-detection"""
        # Create new context with realistic user agent and settings
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 768},
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'DNT': '1',
            }
        )

        # Add stealth scripts to avoid detection
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined,
            });

            Object.defineProperty(navigator, 'plugins', {
              get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
              get: () => ['en-US', 'en'],
            });

            Object.defineProperty(navigator, 'permissions', {
              get: () => ({
                query: () => Promise.resolve({ state: 'granted' }),
              }),
            });

            // Override the `chrome` property to make it seem like a regular browser
            Object.defineProperty(window, 'chrome', {
              value: {
                runtime: {},
              },
            });

            // Mock the window.outerWidth and window.outerHeight
            Object.defineProperty(window, 'outerWidth', {
              get: () => 1366,
            });
            Object.defineProperty(window, 'outerHeight', {
              get: () => 768,
            });
        """)

        page = await context.new_page()

        # Set additional headers to look more like a real browser
        await page.set_extra_http_headers({
            'DNT': '1',
            'Cache-Control': 'no-cache',
        })

        return page

    async def scrape_property_listings(self, base_url: str) -> List[PropertyBasic]:
        """Scrape property listings from the main page"""
        properties = []

        async with async_playwright() as playwright:
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            }

            # Add proxy if configured
            if self.proxy_config:
                launch_options['proxy'] = {
                    'server': self.proxy_config.get('server'),
                    'username': self.proxy_config.get('username'),
                    'password': self.proxy_config.get('password')
                }
                self.logger.info(f"Using proxy: {self.proxy_config.get('server')}")

            browser = await playwright.chromium.launch(**launch_options)
            page = await self._setup_browser_page(browser)

            try:
                current_page = 1
                total_scraped = 0

                while total_scraped < self.max_properties:
                    url = f"{base_url.replace('list-1', f'list-{current_page}')}"
                    self.logger.info(f"Scraping page {current_page}: {url}")

                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await self._random_delay(1, 2)

                    # Check if page loaded successfully
                    if await page.locator('text="429"').count() > 0 or await page.locator('text="blocked"').count() > 0:
                        self.logger.warning("Rate limited or blocked, waiting longer...")
                        await asyncio.sleep(random.uniform(30, 60))
                        continue

                    # Wait for content to load
                    await page.wait_for_selector('body', timeout=30000)
                    await self._random_delay(2, 4)

                    # Extract property cards - using updated selectors for realestate.com.au
                    property_cards = await page.locator('[data-testid="residential-card"]').all()

                    if not property_cards:
                        # Try alternative selectors
                        property_cards = await page.locator('article[data-testid="residential-card"], [class*="residential-card"]').all()

                    if not property_cards:
                        # Fallback selectors
                        property_cards = await page.locator('.listing-result, [data-testid*="card"], article[class*="card"]').all()

                    if not property_cards:
                        self.logger.warning(f"No property cards found on page {current_page}")
                        break

                    page_properties = 0
                    for card in property_cards:
                        if total_scraped >= self.max_properties:
                            break

                        try:
                            # Extract basic property information
                            prop = await self._extract_property_basic(card)
                            if prop and prop.id not in self.scraped_properties:
                                properties.append(prop)
                                total_scraped += 1
                                page_properties += 1
                                self.logger.info(f"Found property {prop.id}: {prop.title}")

                        except Exception as e:
                            self.logger.error(f"Error extracting property from card: {e}")

                    self.logger.info(f"Page {current_page}: Found {page_properties} new properties")

                    if page_properties == 0:
                        break

                    current_page += 1
                    await self._random_delay(1, 3)

            except Exception as e:
                self.logger.error(f"Error scraping listings: {e}")
            finally:
                await browser.close()

        return properties

    async def _extract_property_basic(self, card) -> Optional[PropertyBasic]:
        """Extract basic property information from a listing card"""
        try:
            # Extract property URL and ID
            link_elem = await card.locator('a[href*="/property-"]').first
            if not link_elem:
                link_elem = await card.locator('a[href*="realestate.com.au/property"]').first

            if not link_elem:
                return None

            url = await link_elem.get_attribute('href')
            if not url.startswith('http'):
                url = f"https://www.realestate.com.au{url}"

            # Extract property ID from URL
            property_id = None
            if '/property-' in url:
                property_id = url.split('/property-')[-1].split('-')[-1]

            if not property_id:
                return None

            # Extract title with updated selectors
            title_elem = await card.locator('[data-testid="address-line1"], h2, .property-title, [data-testid*="title"]').first
            title = await title_elem.inner_text() if title_elem else "No title"

            # Extract price with updated selectors
            price_elem = await card.locator('[data-testid="property-price"], .property-price, [data-testid*="price"], .price').first
            price = await price_elem.inner_text() if price_elem else "Price not available"

            # Extract address with updated selectors
            address_elem = await card.locator('[data-testid="address-line1"], [data-testid="address-line2"], .property-address, [data-testid*="address"], .address').first
            address = await address_elem.inner_text() if address_elem else "Address not available"

            # Extract property type
            type_elem = await card.locator('.property-type, [data-testid*="type"]').first
            property_type = await type_elem.inner_text() if type_elem else "Unknown"

            # Extract bedrooms, bathrooms, parking
            features = await card.locator('.property-features, .features, [data-testid*="features"]').all()
            bedrooms = bathrooms = parking = None

            for feature in features:
                text = await feature.inner_text()
                if 'bed' in text.lower():
                    bedrooms = self._extract_number(text)
                elif 'bath' in text.lower():
                    bathrooms = self._extract_number(text)
                elif 'car' in text.lower() or 'park' in text.lower():
                    parking = self._extract_number(text)

            return PropertyBasic(
                id=property_id,
                url=url,
                title=title.strip(),
                price=price.strip(),
                address=address.strip(),
                property_type=property_type.strip(),
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                parking=parking
            )

        except Exception as e:
            self.logger.error(f"Error extracting property basic info: {e}")
            return None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text like '3 bed' -> 3"""
        import re
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None

    async def scrape_property_details(self, property_basic: PropertyBasic) -> Optional[PropertyDetailed]:
        """Scrape detailed information for a specific property"""
        async with async_playwright() as playwright:
            launch_options = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            }

            # Add proxy if configured
            if self.proxy_config:
                launch_options['proxy'] = {
                    'server': self.proxy_config.get('server'),
                    'username': self.proxy_config.get('username'),
                    'password': self.proxy_config.get('password')
                }
                self.logger.info(f"Using proxy: {self.proxy_config.get('server')}")

            browser = await playwright.chromium.launch(**launch_options)
            page = await self._setup_browser_page(browser)

            try:
                self.logger.info(f"Scraping details for property {property_basic.id}")

                await page.goto(property_basic.url, wait_until='networkidle', timeout=30000)
                await self._random_delay(1, 2)

                # Check if page loaded successfully
                if await page.locator('text="429"').count() > 0:
                    self.logger.warning(f"Rate limited for property {property_basic.id}")
                    return None

                # Extract detailed information
                now = datetime.now(timezone.utc).isoformat()

                # Description
                description_elem = await page.locator('.property-description, [data-testid*="description"], .description').first
                description = await description_elem.inner_text() if description_elem else ""

                # Features
                features = []
                feature_elems = await page.locator('.property-features li, .features li, [data-testid*="feature"]').all()
                for elem in feature_elems:
                    feature_text = await elem.inner_text()
                    if feature_text.strip():
                        features.append(feature_text.strip())

                # Images
                images = []
                image_elems = await page.locator('img[src*="property"], .property-image img, [data-testid*="image"] img').all()
                for i, img in enumerate(image_elems[:20]):  # Limit to 20 images
                    try:
                        src = await img.get_attribute('src')
                        if src and 'property' in src:
                            images.append({
                                'url': src if src.startswith('http') else f"https://www.realestate.com.au{src}",
                                'local_path': f"data/images/{property_basic.id}/image_{i+1:03d}.jpg",
                                'description': f"Property image {i+1}"
                            })
                    except Exception as e:
                        self.logger.warning(f"Error extracting image {i}: {e}")

                # Agent information
                agent = {}
                agent_name_elem = await page.locator('.agent-name, [data-testid*="agent-name"]').first
                if agent_name_elem:
                    agent['name'] = await agent_name_elem.inner_text()

                agent_agency_elem = await page.locator('.agent-agency, [data-testid*="agency"]').first
                if agent_agency_elem:
                    agent['agency'] = await agent_agency_elem.inner_text()

                agent_phone_elem = await page.locator('.agent-phone, [data-testid*="phone"]').first
                if agent_phone_elem:
                    agent['phone'] = await agent_phone_elem.inner_text()

                # Parse address into components
                address_parts = property_basic.address.split(',')
                address = {
                    'full': property_basic.address,
                    'street': address_parts[0].strip() if len(address_parts) > 0 else '',
                    'suburb': address_parts[1].strip() if len(address_parts) > 1 else '',
                    'state': address_parts[2].strip() if len(address_parts) > 2 else '',
                    'postcode': address_parts[3].strip() if len(address_parts) > 3 else ''
                }

                detailed = PropertyDetailed(
                    id=property_basic.id,
                    url=property_basic.url,
                    scraped_at=now,
                    last_updated=now,
                    title=property_basic.title,
                    price=property_basic.price,
                    address=address,
                    property_type=property_basic.property_type,
                    bedrooms=property_basic.bedrooms,
                    bathrooms=property_basic.bathrooms,
                    parking=property_basic.parking,
                    description=description,
                    features=features,
                    images=images,
                    agent=agent
                )

                return detailed

            except Exception as e:
                self.logger.error(f"Error scraping property details for {property_basic.id}: {e}")
                return None
            finally:
                await browser.close()

    async def download_images(self, property_detailed: PropertyDetailed):
        """Download all images for a property"""
        if not property_detailed.images:
            return

        property_image_dir = self.images_dir / property_detailed.id
        property_image_dir.mkdir(exist_ok=True)

        async with aiohttp.ClientSession() as session:
            for image_info in property_detailed.images:
                try:
                    local_path = Path(image_info['local_path'])
                    if local_path.exists():
                        continue

                    async with session.get(image_info['url']) as response:
                        if response.status == 200:
                            local_path.parent.mkdir(parents=True, exist_ok=True)
                            async with aiofiles.open(local_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    await f.write(chunk)
                            self.logger.info(f"Downloaded image: {local_path}")
                        else:
                            self.logger.warning(f"Failed to download image {image_info['url']}: {response.status}")

                    await self._random_delay(0.5, 1.5)

                except Exception as e:
                    self.logger.error(f"Error downloading image {image_info['url']}: {e}")

    async def save_property(self, property_detailed: PropertyDetailed):
        """Save property data to JSON file"""
        try:
            property_file = self.properties_dir / f"{property_detailed.id}.json"

            # Convert to dict and handle datetime serialization
            data = asdict(property_detailed)

            async with aiofiles.open(property_file, 'w') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))

            self.scraped_properties.add(property_detailed.id)
            self.logger.info(f"Saved property {property_detailed.id}")

        except Exception as e:
            self.logger.error(f"Error saving property {property_detailed.id}: {e}")
            self.failed_properties.add(property_detailed.id)

    async def run_full_scrape(self, listing_url: str):
        """Run complete scraping process"""
        self.logger.info("Starting full property scrape...")

        # Step 1: Scrape property listings
        self.logger.info("Step 1: Scraping property listings...")
        properties = await self.scrape_property_listings(listing_url)
        self.logger.info(f"Found {len(properties)} properties to scrape")

        # Step 2: Scrape details for each property
        self.logger.info("Step 2: Scraping property details...")
        scraped_count = 0

        for i, prop in enumerate(properties, 1):
            if prop.id in self.scraped_properties:
                self.logger.info(f"Skipping already scraped property {prop.id}")
                continue

            self.logger.info(f"Processing property {i}/{len(properties)}: {prop.id}")

            try:
                detailed = await self.scrape_property_details(prop)
                if detailed:
                    # Step 3: Download images
                    await self.download_images(detailed)

                    # Step 4: Save property data
                    await self.save_property(detailed)
                    scraped_count += 1
                else:
                    self.failed_properties.add(prop.id)

            except Exception as e:
                self.logger.error(f"Error processing property {prop.id}: {e}")
                self.failed_properties.add(prop.id)

            # Save state periodically
            if scraped_count % 10 == 0:
                self._save_state()

            # Random delay between properties (optimized)
            await self._random_delay(2, 5)

        # Final state save
        self._save_state()

        self.logger.info(f"Scraping completed. Scraped: {scraped_count}, Failed: {len(self.failed_properties)}")


async def main():
    """Main function to run the scraper"""
    scraper = RealEstateScraper(max_properties=100)

    # Brisbane properties for sale
    listing_url = "https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1"

    await scraper.run_full_scrape(listing_url)


if __name__ == "__main__":
    asyncio.run(main())