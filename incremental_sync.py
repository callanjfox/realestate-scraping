#!/usr/bin/env python3
"""
Incremental sync script for real estate scraper.
Handles periodic updates and change detection.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Set, Dict, List
import hashlib

from scraper import RealEstateScraper, PropertyDetailed


class IncrementalSyncer:
    """Handles incremental synchronization of property data"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.logs_dir = self.data_dir / "logs"
        self.properties_dir = self.data_dir / "properties"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / 'incremental_sync.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _calculate_property_hash(self, property_data: Dict) -> str:
        """Calculate hash of property data to detect changes"""
        # Create a hash of key fields that might change
        key_fields = {
            'title': property_data.get('title', ''),
            'price': property_data.get('price', ''),
            'description': property_data.get('description', ''),
            'features': sorted(property_data.get('features', [])),
            'status': property_data.get('status', 'active')
        }

        hash_string = json.dumps(key_fields, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()

    async def detect_changes(self, new_properties: List[Dict]) -> Dict[str, List[str]]:
        """Detect which properties are new, changed, or removed"""
        changes = {
            'new': [],
            'changed': [],
            'removed': [],
            'unchanged': []
        }

        # Get existing properties
        existing_properties = {}
        property_hashes = {}

        for property_file in self.properties_dir.glob("*.json"):
            try:
                with open(property_file, 'r') as f:
                    data = json.load(f)
                    prop_id = data['id']
                    existing_properties[prop_id] = data
                    property_hashes[prop_id] = self._calculate_property_hash(data)
            except Exception as e:
                self.logger.error(f"Error reading {property_file}: {e}")

        # Build new properties dict for comparison
        new_properties_dict = {prop['id']: prop for prop in new_properties}
        new_property_ids = set(new_properties_dict.keys())
        existing_property_ids = set(existing_properties.keys())

        # Detect new properties
        for prop_id in new_property_ids - existing_property_ids:
            changes['new'].append(prop_id)
            self.logger.info(f"New property detected: {prop_id}")

        # Detect removed properties (no longer in listings)
        for prop_id in existing_property_ids - new_property_ids:
            changes['removed'].append(prop_id)
            self.logger.info(f"Removed property detected: {prop_id}")

        # Detect changed properties
        for prop_id in new_property_ids & existing_property_ids:
            new_hash = self._calculate_property_hash(new_properties_dict[prop_id])
            old_hash = property_hashes.get(prop_id, '')

            if new_hash != old_hash:
                changes['changed'].append(prop_id)
                self.logger.info(f"Changed property detected: {prop_id}")
            else:
                changes['unchanged'].append(prop_id)

        return changes

    async def update_removed_properties(self, removed_property_ids: List[str]):
        """Update status of removed properties"""
        for prop_id in removed_property_ids:
            try:
                property_file = self.properties_dir / f"{prop_id}.json"
                if property_file.exists():
                    with open(property_file, 'r') as f:
                        data = json.load(f)

                    data['status'] = 'removed'
                    data['last_updated'] = datetime.now(timezone.utc).isoformat()

                    with open(property_file, 'w') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    self.logger.info(f"Updated status to 'removed' for property {prop_id}")

            except Exception as e:
                self.logger.error(f"Error updating removed property {prop_id}: {e}")

    async def run_incremental_sync(self, listing_url: str, max_properties: int = 100):
        """Run incremental synchronization"""
        self.logger.info("Starting incremental sync...")

        # Initialize scraper
        scraper = RealEstateScraper(max_properties=max_properties)

        try:
            # Step 1: Get current listings
            self.logger.info("Fetching current property listings...")
            current_properties = await scraper.scrape_property_listings(listing_url)

            if not current_properties:
                self.logger.warning("No properties found in current listings")
                return

            # Convert to dict format for comparison
            current_properties_dict = [
                {
                    'id': prop.id,
                    'title': prop.title,
                    'price': prop.price,
                    'address': prop.address,
                    'property_type': prop.property_type,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'parking': prop.parking,
                    'status': 'active'
                }
                for prop in current_properties
            ]

            # Step 2: Detect changes
            self.logger.info("Detecting changes...")
            changes = await self.detect_changes(current_properties_dict)

            self.logger.info(f"Changes detected - New: {len(changes['new'])}, "
                           f"Changed: {len(changes['changed'])}, "
                           f"Removed: {len(changes['removed'])}, "
                           f"Unchanged: {len(changes['unchanged'])}")

            # Step 3: Update removed properties
            if changes['removed']:
                await self.update_removed_properties(changes['removed'])

            # Step 4: Scrape new and changed properties
            properties_to_scrape = []
            for prop in current_properties:
                if prop.id in changes['new'] or prop.id in changes['changed']:
                    properties_to_scrape.append(prop)

            if properties_to_scrape:
                self.logger.info(f"Scraping {len(properties_to_scrape)} new/changed properties...")

                for i, prop in enumerate(properties_to_scrape, 1):
                    self.logger.info(f"Processing property {i}/{len(properties_to_scrape)}: {prop.id}")

                    try:
                        # Scrape detailed information
                        detailed = await scraper.scrape_property_details(prop)
                        if detailed:
                            # Download images
                            await scraper.download_images(detailed)

                            # Save property data
                            await scraper.save_property(detailed)
                        else:
                            scraper.failed_properties.add(prop.id)

                    except Exception as e:
                        self.logger.error(f"Error processing property {prop.id}: {e}")
                        scraper.failed_properties.add(prop.id)

                    # Random delay between properties
                    await scraper._random_delay(5, 15)

            # Step 5: Save sync state
            scraper._save_state()

            # Save sync summary
            sync_summary = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'changes': changes,
                'total_current_properties': len(current_properties),
                'properties_scraped': len(properties_to_scrape),
                'failed_properties': len(scraper.failed_properties)
            }

            with open(self.logs_dir / "last_incremental_sync.json", 'w') as f:
                json.dump(sync_summary, f, indent=2)

            self.logger.info("Incremental sync completed successfully")

        except Exception as e:
            self.logger.error(f"Error during incremental sync: {e}")
            raise


class PeriodicSyncer:
    """Handles periodic execution of incremental sync"""

    def __init__(self, sync_interval_hours: int = 24):
        self.sync_interval_hours = sync_interval_hours
        self.syncer = IncrementalSyncer()

    async def run_periodic_sync(self, listing_url: str, max_properties: int = 100):
        """Run periodic synchronization"""
        while True:
            try:
                await self.syncer.run_incremental_sync(listing_url, max_properties)

                # Wait for next sync
                wait_seconds = self.sync_interval_hours * 3600
                self.syncer.logger.info(f"Next sync in {self.sync_interval_hours} hours")
                await asyncio.sleep(wait_seconds)

            except KeyboardInterrupt:
                self.syncer.logger.info("Periodic sync stopped by user")
                break
            except Exception as e:
                self.syncer.logger.error(f"Error in periodic sync: {e}")
                # Wait 1 hour before retrying
                await asyncio.sleep(3600)


async def main():
    """Main function"""
    import sys

    listing_url = "https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1"

    if len(sys.argv) > 1 and sys.argv[1] == "periodic":
        # Run periodic sync (default 24 hours)
        sync_hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        periodic_syncer = PeriodicSyncer(sync_interval_hours=sync_hours)
        await periodic_syncer.run_periodic_sync(listing_url, max_properties=100)
    else:
        # Run single incremental sync
        syncer = IncrementalSyncer()
        await syncer.run_incremental_sync(listing_url, max_properties=100)


if __name__ == "__main__":
    asyncio.run(main())