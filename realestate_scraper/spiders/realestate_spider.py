import scrapy
import re
import json
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, parse_qs
from itemloaders import ItemLoader
from realestate_scraper.items import PropertyItem


class PropertyItemLoader(ItemLoader):
    default_item_class = PropertyItem


class RealEstateSpider(scrapy.Spider):
    """Spider for scraping realestate.com.au"""

    name = 'realestate'
    allowed_domains = ['realestate.com.au']

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def __init__(self, url=None, max_properties=10, *args, **kwargs):
        super(RealEstateSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else [
            'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'
        ]
        self.max_properties = int(max_properties)
        self.properties_scraped = 0
        self.base_url = self.start_urls[0]

        # Session management for ScraperAPI
        import random
        self.session_id = random.randint(1, 100000)  # Consistent session for this crawl

    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_listing_page,
                meta={'page_num': 1}
            )

    def parse_listing_page(self, response):
        """Parse property listing pages"""
        page_num = response.meta.get('page_num', 1)
        self.logger.info(f"Parsing listing page {page_num}: {response.url}")

        # Multiple selectors for property cards (realestate.com.au uses different layouts)
        property_selectors = [
            '[data-testid="residential-card"]',
            'article[data-testid="residential-card"]',
            '[class*="residential-card"]',
            '.listing-result',
            'article[class*="card"]'
        ]

        properties_found = []
        for selector in property_selectors:
            properties = response.css(selector)
            if properties:
                properties_found = properties
                self.logger.info(f"Found {len(properties)} properties using selector: {selector}")
                break

        if not properties_found:
            # Try to find any article or div that might contain properties
            properties_found = response.css('article, .property-card, [class*="property"], [class*="listing"]')
            self.logger.warning(f"Using fallback selector, found {len(properties_found)} potential properties")

        properties_processed = 0
        for property_card in properties_found:
            if self.properties_scraped >= self.max_properties:
                self.logger.info(f"Reached max properties limit: {self.max_properties}")
                return

            # Extract property URL
            property_url = self.extract_property_url(property_card)
            if not property_url:
                continue

            property_url = urljoin(response.url, property_url)

            # Extract property ID from URL
            property_id = self.extract_property_id(property_url)
            if not property_id:
                continue

            # Extract basic info from listing card
            basic_info = self.extract_basic_info(property_card)

            self.logger.info(f"Found property {property_id}: {basic_info.get('title', 'No title')}")

            yield scrapy.Request(
                url=property_url,
                callback=self.parse_property_detail,
                meta={
                    'property_id': property_id,
                    'basic_info': basic_info,
                    'property_url': property_url
                }
            )

            self.properties_scraped += 1
            properties_processed += 1

        self.logger.info(f"Processed {properties_processed} properties on page {page_num}")

        # Only go to next page if we haven't reached the limit and found properties
        if self.properties_scraped < self.max_properties and properties_processed > 0:
            next_page_url = self.get_next_page_url(response.url, page_num + 1)
            if next_page_url:
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_listing_page,
                    meta={'page_num': page_num + 1}
                )

    def extract_property_url(self, property_card):
        """Extract property URL from card"""
        url_selectors = [
            'a::attr(href)',
            '.property-title a::attr(href)',
            '[data-testid*="title"] a::attr(href)',
            'h2 a::attr(href)',
            '.title a::attr(href)'
        ]

        for selector in url_selectors:
            url = property_card.css(selector).get()
            if url:
                return url.strip()

        return None

    def extract_property_id(self, url):
        """Extract property ID from URL"""
        # realestate.com.au URLs typically have format: /property/{type}-{id}-{suburb}
        match = re.search(r'/property/[^/]*?-(\d+)-', url)
        if match:
            return match.group(1)

        # Alternative: extract from query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'id' in query_params:
            return query_params['id'][0]

        # Fallback: use last part of path as ID
        path_parts = parsed_url.path.strip('/').split('/')
        if path_parts:
            # Try to find a number in the last part
            last_part = path_parts[-1]
            match = re.search(r'(\d+)', last_part)
            if match:
                return match.group(1)

        return None

    def extract_basic_info(self, property_card):
        """Extract basic info from property card"""
        info = {}

        # Title selectors
        title_selectors = [
            '.property-title::text',
            '[data-testid*="title"]::text',
            'h2::text',
            '.title::text',
            'a[title]::attr(title)'
        ]

        for selector in title_selectors:
            title = property_card.css(selector).get()
            if title:
                info['title'] = title.strip()
                break

        # Price selectors
        price_selectors = [
            '.property-price::text',
            '[data-testid*="price"]::text',
            '.price::text',
            '[class*="price"]::text'
        ]

        for selector in price_selectors:
            price = property_card.css(selector).get()
            if price:
                info['price'] = price.strip()
                break

        # Address selectors
        address_selectors = [
            '.property-address::text',
            '[data-testid*="address"]::text',
            '.address::text',
            '[class*="address"]::text'
        ]

        for selector in address_selectors:
            address = property_card.css(selector).get()
            if address:
                info['address'] = address.strip()
                break

        return info

    def parse_property_detail(self, response):
        """Parse individual property detail page"""
        property_id = response.meta['property_id']
        basic_info = response.meta['basic_info']
        property_url = response.meta['property_url']

        self.logger.info(f"Parsing property detail for ID {property_id}")

        loader = PropertyItemLoader(response=response)

        # Basic fields
        loader.add_value('id', property_id)
        loader.add_value('url', property_url)
        loader.add_value('scraped_at', datetime.now(timezone.utc).isoformat())
        loader.add_value('last_updated', datetime.now(timezone.utc).isoformat())
        loader.add_value('status', 'active')

        # Use basic info from listing page as fallback
        if basic_info.get('title'):
            loader.add_value('title', basic_info['title'])
        if basic_info.get('price'):
            loader.add_value('price', basic_info['price'])
        if basic_info.get('address'):
            loader.add_value('address', {'full': basic_info['address']})

        # Extract detailed information
        self.extract_detailed_info(loader, response)

        yield loader.load_item()

    def extract_detailed_info(self, loader, response):
        """Extract detailed property information"""

        # Title (override with detailed page if available)
        title_selectors = [
            'h1::text',
            '.property-title h1::text',
            '[data-testid*="title"] h1::text',
            '.listing-details h1::text'
        ]

        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                loader.add_value('title', title.strip())
                break

        # Price (override with detailed page if available)
        price_selectors = [
            '.property-price::text',
            '[data-testid*="price"]::text',
            '.price-wrapper::text',
            '.listing-details .price::text'
        ]

        for selector in price_selectors:
            price = response.css(selector).get()
            if price:
                loader.add_value('price', price.strip())
                break

        # Property type
        type_selectors = [
            '.property-type::text',
            '[data-testid*="type"]::text',
            '.property-info .type::text'
        ]

        for selector in type_selectors:
            prop_type = response.css(selector).get()
            if prop_type:
                loader.add_value('property_type', prop_type.strip())
                break

        # Bedrooms, bathrooms, parking
        self.extract_property_features(loader, response)

        # Description
        desc_selectors = [
            '.property-description::text',
            '[data-testid*="description"] p::text',
            '.description p::text',
            '.listing-details .description::text'
        ]

        for selector in desc_selectors:
            descriptions = response.css(selector).getall()
            if descriptions:
                loader.add_value('description', ' '.join(descriptions))
                break

        # Features
        feature_selectors = [
            '.property-features li::text',
            '.features li::text',
            '[data-testid*="features"] li::text'
        ]

        features = []
        for selector in feature_selectors:
            feature_list = response.css(selector).getall()
            if feature_list:
                features.extend([f.strip() for f in feature_list if f.strip()])

        if features:
            loader.add_value('features', features)

        # Images
        img_selectors = [
            '.property-images img::attr(src)',
            '.gallery img::attr(src)',
            '[data-testid*="image"] img::attr(src)'
        ]

        images = []
        for selector in img_selectors:
            img_urls = response.css(selector).getall()
            if img_urls:
                for img_url in img_urls:
                    if img_url and not img_url.startswith('data:'):
                        images.append({
                            'url': urljoin(response.url, img_url),
                            'alt': f'Property {loader.get_output_value("id")} image'
                        })

        if images:
            loader.add_value('images', images)

    def extract_property_features(self, loader, response):
        """Extract bedrooms, bathrooms, parking from various selectors"""

        # Common feature patterns
        feature_patterns = {
            'bedrooms': [r'(\d+)\s*bed', r'(\d+)\s*br'],
            'bathrooms': [r'(\d+)\s*bath', r'(\d+)\s*ba'],
            'parking': [r'(\d+)\s*car', r'(\d+)\s*garage', r'(\d+)\s*park']
        }

        # Look in feature elements
        feature_selectors = [
            '.property-features *::text',
            '.features *::text',
            '.property-info *::text',
            '[data-testid*="features"] *::text'
        ]

        all_text = []
        for selector in feature_selectors:
            texts = response.css(selector).getall()
            all_text.extend([t.lower().strip() for t in texts if t.strip()])

        full_text = ' '.join(all_text)

        # Extract features using patterns
        for feature, patterns in feature_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    loader.add_value(feature, int(match.group(1)))
                    break

    def get_next_page_url(self, current_url, next_page):
        """Generate URL for next page"""
        # Replace list-X with list-{next_page}
        next_url = re.sub(r'/list-\d+', f'/list-{next_page}', current_url)
        return next_url if next_url != current_url else None