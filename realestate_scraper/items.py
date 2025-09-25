import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
import re


def clean_text(text):
    """Clean text by removing extra whitespace"""
    if text:
        return re.sub(r'\s+', ' ', text.strip())
    return text


def extract_number(text):
    """Extract number from text like '3 bed' -> 3"""
    if text:
        match = re.search(r'(\d+)', str(text))
        return int(match.group(1)) if match else None
    return None


def clean_price(text):
    """Clean price text"""
    if text:
        # Remove extra whitespace and normalize
        return re.sub(r'\s+', ' ', text.strip())
    return text


class PropertyItem(scrapy.Item):
    """Scrapy item for property data - matches PropertyDetailed dataclass"""

    # Core fields
    id = scrapy.Field()
    url = scrapy.Field()
    scraped_at = scrapy.Field()
    last_updated = scrapy.Field()

    # Basic info
    title = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clean_price), output_processor=TakeFirst())
    property_type = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())

    # Address - will be dict
    address = scrapy.Field()

    # Numeric fields
    bedrooms = scrapy.Field(input_processor=MapCompose(extract_number), output_processor=TakeFirst())
    bathrooms = scrapy.Field(input_processor=MapCompose(extract_number), output_processor=TakeFirst())
    parking = scrapy.Field(input_processor=MapCompose(extract_number), output_processor=TakeFirst())

    # Size fields
    land_size = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    building_size = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())

    # Description and features
    description = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join(' '))
    features = scrapy.Field()  # List of features

    # Images and agent - will be lists/dicts
    images = scrapy.Field()
    agent = scrapy.Field()

    # Additional fields
    listing_date = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    status = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())