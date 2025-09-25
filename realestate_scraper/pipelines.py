import json
import os
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
import aiohttp
import aiofiles


class JsonWriterPipeline:
    """Pipeline to save items as individual JSON files (compatible with existing structure)"""

    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.properties_dir = self.data_dir / 'properties'
        self.logs_dir = self.data_dir / 'logs'

        # Create directories
        for dir_path in [self.properties_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        """Process and save item as JSON file"""
        adapter = ItemAdapter(item)

        # Convert item to dict and ensure proper structure
        item_dict = dict(adapter)

        # Fix ItemLoader lists - convert single-item lists to values
        for key, value in item_dict.items():
            if isinstance(value, list) and len(value) == 1 and key not in ['features', 'images']:
                item_dict[key] = value[0]

        # Ensure required fields have defaults
        if not item_dict.get('features'):
            item_dict['features'] = []
        if not item_dict.get('images'):
            item_dict['images'] = []
        if not item_dict.get('agent'):
            item_dict['agent'] = {}
        if not item_dict.get('address') or isinstance(item_dict['address'], str):
            # Convert string address to dict format
            address_str = item_dict.get('address', '')
            item_dict['address'] = {
                'full': address_str,
                'street': '',
                'suburb': '',
                'state': '',
                'postcode': ''
            }
        elif isinstance(item_dict.get('address'), list) and len(item_dict['address']) > 0:
            # If address is a list, take the first item
            item_dict['address'] = item_dict['address'][0]

        # Save to JSON file
        property_id = item_dict['id']
        if isinstance(property_id, list):
            property_id = property_id[0]
        filename = f"{property_id}.json"
        filepath = self.properties_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(item_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved property {property_id} to {filepath}")

            # Update scraped properties log
            self.update_scraped_properties_log(item_dict)

        except Exception as e:
            self.logger.error(f"Error saving property {property_id}: {e}")
            raise

        return item

    def update_scraped_properties_log(self, item_dict):
        """Update the scraped properties log file"""
        scraped_log_file = self.logs_dir / 'scraped_properties.json'

        # Load existing log
        scraped_properties = {}
        if scraped_log_file.exists():
            try:
                with open(scraped_log_file, 'r', encoding='utf-8') as f:
                    scraped_properties = json.load(f)
            except:
                scraped_properties = {}

        # Add/update property
        property_id = item_dict['id']
        if isinstance(property_id, list):
            property_id = property_id[0]
        scraped_properties[property_id] = {
            'scraped_at': item_dict.get('scraped_at', ''),
            'title': item_dict.get('title', ''),
            'url': item_dict.get('url', ''),
            'hash': self.calculate_item_hash(item_dict)
        }

        # Save updated log
        try:
            with open(scraped_log_file, 'w', encoding='utf-8') as f:
                json.dump(scraped_properties, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error updating scraped properties log: {e}")

    def calculate_item_hash(self, item_dict):
        """Calculate MD5 hash of key property fields for change detection"""
        key_fields = ['title', 'price', 'description', 'features']
        hash_data = {}

        for field in key_fields:
            value = item_dict.get(field, '')
            if isinstance(value, list):
                value = '|'.join(sorted([str(v) for v in value]))
            hash_data[field] = str(value)

        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()


class PropertyImagesPipeline(ImagesPipeline):
    """Custom images pipeline to organize images by property ID"""

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.data_dir = Path(settings.get('IMAGES_STORE', 'data/images'))

    def get_media_requests(self, item, info):
        """Generate requests for downloading images"""
        adapter = ItemAdapter(item)
        images = adapter.get('images', [])

        for image_info in images:
            if isinstance(image_info, dict) and 'url' in image_info:
                yield scrapy.Request(
                    url=image_info['url'],
                    meta={
                        'property_id': adapter.get('id'),
                        'image_info': image_info
                    }
                )

    def file_path(self, request, response=None, info=None, *, item=None):
        """Generate file path for image"""
        property_id = request.meta.get('property_id')
        image_url = request.url

        # Extract filename from URL
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)

        # Ensure we have a valid filename with extension
        if not filename or '.' not in filename:
            filename = f"image_{hashlib.md5(image_url.encode()).hexdigest()[:8]}.jpg"

        # Organize by property ID
        return f"{property_id}/{filename}"

    def item_completed(self, results, item, info):
        """Update item with downloaded image information"""
        adapter = ItemAdapter(item)
        property_id = adapter.get('id')

        if results:
            downloaded_images = []
            for ok, result in results:
                if ok:
                    downloaded_images.append({
                        'url': result['url'],
                        'path': result['path'],
                        'checksum': result['checksum']
                    })

            if downloaded_images:
                adapter['images'] = downloaded_images
                info.spider.logger.info(f"Downloaded {len(downloaded_images)} images for property {property_id}")

        return item