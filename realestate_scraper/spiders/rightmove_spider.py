import scrapy
import re
import json
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from itemloaders import ItemLoader
from realestate_scraper.items import PropertyItem


class PropertyItemLoader(ItemLoader):
    default_item_class = PropertyItem


class RightMoveSpider(scrapy.Spider):
    """Spider for scraping RightMove UK"""

    name = 'rightmove'
    allowed_domains = ['rightmove.co.uk']

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def __init__(self, url=None, max_properties=10, *args, **kwargs):
        super(RightMoveSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else [
            'https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E87490'
        ]
        self.max_properties = int(max_properties)
        self.properties_scraped = 0
        self.base_url = 'https://www.rightmove.co.uk'

        # Session management
        import random
        self.session_id = random.randint(1, 100000)

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
        self.logger.info(f"Parsing RightMove listing page {page_num}: {response.url}")

        # RightMove specific selectors
        property_links = response.css('[data-test*="property"] a.propertyCard-link::attr(href)').getall()

        if not property_links:
            # Try alternative selectors
            property_links = response.css('a[href*="/properties/"]::attr(href)').getall()

        self.logger.info(f"Found {len(property_links)} property links on page {page_num}")

        properties_processed = 0
        for link in property_links:
            if self.properties_scraped >= self.max_properties:
                self.logger.info(f"Reached max properties limit: {self.max_properties}")
                return

            # Make URL absolute
            property_url = urljoin(self.base_url, link)

            # Extract property ID from URL
            property_id = self.extract_property_id_from_url(property_url)
            if not property_id:
                continue

            self.logger.info(f"Found property {property_id}: {property_url}")

            yield scrapy.Request(
                url=property_url,
                callback=self.parse_property_detail,
                meta={
                    'property_id': property_id,
                    'property_url': property_url
                }
            )

            self.properties_scraped += 1
            properties_processed += 1

        self.logger.info(f"Processed {properties_processed} properties on page {page_num}")

        # Go to next page if we haven't reached the limit and found properties
        if self.properties_scraped < self.max_properties and properties_processed > 0:
            next_page_url = self.get_next_page_url(response, page_num + 1)
            if next_page_url:
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_listing_page,
                    meta={'page_num': page_num + 1}
                )

    def extract_property_id_from_url(self, url):
        """Extract property ID from RightMove URL"""
        # RightMove URLs typically have format: /properties/123456789#/
        match = re.search(r'/properties/(\d+)', url)
        if match:
            return match.group(1)

        # Fallback: use last numeric part
        path_parts = urlparse(url).path.split('/')
        for part in reversed(path_parts):
            if part.isdigit():
                return part

        return None

    def parse_property_detail(self, response):
        """Parse individual property detail page"""
        property_id = response.meta['property_id']
        property_url = response.meta['property_url']

        self.logger.info(f"Parsing RightMove property detail for ID {property_id}")

        loader = PropertyItemLoader(response=response)

        # Basic fields
        loader.add_value('id', property_id)
        loader.add_value('url', property_url)
        loader.add_value('scraped_at', datetime.now(timezone.utc).isoformat())
        loader.add_value('last_updated', datetime.now(timezone.utc).isoformat())
        loader.add_value('status', 'active')

        # Extract property information using RightMove selectors
        self.extract_rightmove_details(loader, response)

        yield loader.load_item()

    def extract_rightmove_details(self, loader, response):
        """Extract detailed property information from RightMove"""

        # Title - RightMove specific
        title_selectors = [
            'h1._2uQQ3SV0eMHL1P6t5ZDo2q::text',
            'h1[data-testid="property-title"]::text',
            'h1::text',
            '.property-header h1::text'
        ]

        for selector in title_selectors:
            title = response.css(selector).get()
            if title:
                loader.add_value('title', title.strip())
                break

        # Price - RightMove specific
        price_selectors = [
            '._1gfnqJ3Vtd1z40MlC0MzXu span::text',
            '[data-testid="property-price"] span::text',
            '.propertyHeaderPrice span::text',
            '._1gfnqJ3Vtd1z40MlC0MzXu::text'
        ]

        for selector in price_selectors:
            price = response.css(selector).get()
            if price and '£' in price:
                loader.add_value('price', price.strip())
                break

        # Address
        address_text = response.css('meta[property="og:description"]::attr(content)').get()
        if address_text:
            loader.add_value('address', {'full': address_text})

        # Property type
        type_selectors = [
            '.propertySubHeading::text',
            '[data-testid="property-type"]::text',
            '.property-type::text'
        ]

        for selector in type_selectors:
            prop_type = response.css(selector).get()
            if prop_type:
                loader.add_value('property_type', prop_type.strip())
                break

        # Key features (bedrooms, bathrooms, etc.)
        self.extract_rightmove_features(loader, response)

        # Description
        desc_selectors = [
            '.propertyDescription div p::text',
            '[data-testid="property-description"] p::text',
            '.property-description p::text'
        ]

        descriptions = []
        for selector in desc_selectors:
            desc_parts = response.css(selector).getall()
            if desc_parts:
                descriptions.extend([d.strip() for d in desc_parts if d.strip()])

        if descriptions:
            loader.add_value('description', ' '.join(descriptions))

        # Images
        img_selectors = [
            '.propertyGallery img::attr(src)',
            '[data-testid="gallery"] img::attr(src)',
            '.property-images img::attr(src)'
        ]

        images = []
        for selector in img_selectors:
            img_urls = response.css(selector).getall()
            if img_urls:
                for img_url in img_urls:
                    if img_url and not img_url.startswith('data:'):
                        full_url = urljoin(response.url, img_url)
                        images.append({
                            'url': full_url,
                            'alt': f'Property {property_id} image'
                        })

        if images:
            loader.add_value('images', images[:10])  # Limit to 10 images

    def extract_rightmove_features(self, loader, response):
        """Extract bedrooms, bathrooms, etc. from RightMove"""

        # Look for key facts section
        key_facts_selectors = [
            '.propertyKeyFeatures li::text',
            '.key-features li::text',
            '._1u12RxIWt4ozBTvHw7Bg7z div::text'  # RightMove key features
        ]

        all_features = []
        for selector in key_facts_selectors:
            features = response.css(selector).getall()
            if features:
                all_features.extend([f.strip() for f in features if f.strip()])

        # Extract numeric features using regex
        features_text = ' '.join(all_features).lower()

        # Bedrooms
        bed_match = re.search(r'(\d+)\s*bed', features_text)
        if bed_match:
            loader.add_value('bedrooms', int(bed_match.group(1)))

        # Bathrooms
        bath_match = re.search(r'(\d+)\s*bath', features_text)
        if bath_match:
            loader.add_value('bathrooms', int(bath_match.group(1)))

        # Reception rooms (like living rooms)
        reception_match = re.search(r'(\d+)\s*reception', features_text)
        if reception_match:
            # Store as additional info
            pass

        # Store all features
        if all_features:
            loader.add_value('features', all_features)

    def get_next_page_url(self, response, next_page):
        """Generate URL for next page"""
        current_url = response.url

        # RightMove pagination pattern
        if 'index=' in current_url:
            # Replace existing index
            next_url = re.sub(r'index=\d+', f'index={next_page * 24}', current_url)
        else:
            # Add index parameter
            separator = '&' if '?' in current_url else '?'
            next_url = f"{current_url}{separator}index={next_page * 24}"

        return next_url if next_url != current_url else None