#!/usr/bin/env python3
"""
Incremental Property Scraper - Complete Two-Stage System
Coordinates listings scraping with detailed property extraction
"""

from property_listings_scraper import PropertyListingsScraper
from refined_xpath_extractor import RefinedXPathExtractor
import json
import time
from datetime import datetime, timezone
from pathlib import Path

class IncrementalPropertyScraper:
    """Manages incremental property scraping with two-stage approach"""

    def __init__(self):
        self.listings_scraper = PropertyListingsScraper()
        self.detail_extractor = RefinedXPathExtractor()

        # Tracking files
        self.tracking_dir = Path("data/tracking")
        self.tracking_dir.mkdir(parents=True, exist_ok=True)

        self.scraped_ids_file = self.tracking_dir / "scraped_property_ids.json"
        self.sync_log_file = self.tracking_dir / "sync_log.json"

    def load_existing_property_ids(self):
        """Load already scraped property IDs"""

        if self.scraped_ids_file.exists():
            try:
                with open(self.scraped_ids_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    existing_ids = set(data.get('property_ids', []))
                    print(f"📋 Loaded {len(existing_ids)} existing property IDs")
                    return existing_ids
            except Exception as e:
                print(f"⚠️ Error loading existing IDs: {e}")

        print(f"📋 No existing property IDs found - starting fresh")
        return set()

    def save_scraped_property_ids(self, all_scraped_ids):
        """Save updated list of scraped property IDs"""

        data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_properties': len(all_scraped_ids),
            'property_ids': list(all_scraped_ids)
        }

        with open(self.scraped_ids_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Updated scraped IDs: {len(all_scraped_ids)} total")

    def filter_new_properties(self, found_urls, found_ids, existing_ids):
        """Filter out already-scraped properties"""

        new_urls = []
        new_ids = []

        for url, prop_id in zip(found_urls, found_ids):
            if prop_id and prop_id not in existing_ids:
                new_urls.append(url)
                new_ids.append(prop_id)

        print(f"🔍 FILTERING RESULTS:")
        print(f"  Found properties: {len(found_urls)}")
        print(f"  Already scraped: {len(found_urls) - len(new_urls)}")
        print(f"  New to scrape: {len(new_urls)}")

        return new_urls, new_ids

    def extract_new_properties(self, new_urls, new_ids):
        """Extract detailed data for new properties"""

        print(f"\n🎯 EXTRACTING DETAILED DATA FOR NEW PROPERTIES")
        print("="*60)

        successful_extractions = 0
        failed_extractions = 0
        extracted_ids = []

        for i, (url, prop_id) in enumerate(zip(new_urls, new_ids), 1):
            print(f"\n🏠 PROPERTY {i}/{len(new_urls)}: {prop_id}")
            print(f"URL: {url}")
            print("-" * 50)

            try:
                success, data = self.detail_extractor.extract_property_refined(url)

                if success:
                    successful_extractions += 1
                    extracted_ids.append(prop_id)

                    title = data.get('title', 'Unknown property')
                    features_count = len(data.get('property_features', []))
                    highlights_count = len(data.get('property_highlights', []))
                    images_count = len(data.get('downloaded_images', []))

                    print(f"✅ SUCCESS: {title}")
                    print(f"   Features: {features_count}, Highlights: {highlights_count}")
                    print(f"   Images downloaded: {images_count}")
                else:
                    failed_extractions += 1
                    print(f"❌ FAILED: Could not extract property data")

            except Exception as e:
                failed_extractions += 1
                print(f"❌ ERROR: {e}")

            # Respectful delay between extractions
            if i < len(new_urls):
                print(f"⏳ Waiting 5 seconds before next property...")
                time.sleep(5)

        print(f"\n🎉 DETAILED EXTRACTION COMPLETE!")
        print(f"✅ Successful: {successful_extractions}/{len(new_urls)}")
        print(f"❌ Failed: {failed_extractions}")

        return extracted_ids

    def log_sync_run(self, found_properties, new_properties, successful_extractions):
        """Log sync run details"""

        sync_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'found_properties': found_properties,
            'new_properties': new_properties,
            'successful_extractions': successful_extractions,
            'success_rate': f"{(successful_extractions/new_properties*100):.1f}%" if new_properties > 0 else "0%"
        }

        # Load existing log
        sync_log = []
        if self.sync_log_file.exists():
            try:
                with open(self.sync_log_file, 'r', encoding='utf-8') as f:
                    sync_log = json.load(f)
            except:
                sync_log = []

        # Add new entry
        sync_log.append(sync_entry)

        # Keep only last 20 runs
        sync_log = sync_log[-20:]

        # Save updated log
        with open(self.sync_log_file, 'w', encoding='utf-8') as f:
            json.dump(sync_log, f, indent=2, ensure_ascii=False)

        print(f"📊 Sync run logged")

    def run_incremental_sync(self, start_url, max_pages=2, max_new_properties=10):
        """Run complete incremental sync process"""

        print(f"🔄 STARTING INCREMENTAL PROPERTY SYNC")
        print(f"Source: Brisbane Greater Region Houses")
        print(f"Max pages: {max_pages}")
        print(f"Max new properties: {max_new_properties}")
        print("="*70)

        # Step 1: Load existing property IDs
        existing_ids = self.load_existing_property_ids()

        # Step 2: Scrape listings to find property URLs
        print(f"\n📄 STAGE 1: SCRAPING LISTINGS")
        found_urls, found_ids = self.listings_scraper.scrape_multiple_pages(start_url, max_pages)

        if not found_urls:
            print(f"❌ No properties found in listings")
            return False

        # Step 3: Filter new properties
        print(f"\n🔍 STAGE 2: FILTERING NEW PROPERTIES")
        new_urls, new_ids = self.filter_new_properties(found_urls, found_ids, existing_ids)

        if not new_urls:
            print(f"✅ No new properties to scrape - all up to date!")
            return True

        # Limit new properties if specified
        if len(new_urls) > max_new_properties:
            print(f"📊 Limiting to first {max_new_properties} new properties")
            new_urls = new_urls[:max_new_properties]
            new_ids = new_ids[:max_new_properties]

        # Step 4: Extract detailed data for new properties
        print(f"\n🎯 STAGE 3: EXTRACTING DETAILED DATA")
        extracted_ids = self.extract_new_properties(new_urls, new_ids)

        # Step 5: Update tracking
        print(f"\n💾 STAGE 4: UPDATING TRACKING")
        all_scraped_ids = existing_ids | set(extracted_ids)
        self.save_scraped_property_ids(all_scraped_ids)

        # Step 6: Log sync run
        self.log_sync_run(len(found_urls), len(new_urls), len(extracted_ids))

        print(f"\n🎉 INCREMENTAL SYNC COMPLETE!")
        print(f"📊 FINAL SUMMARY:")
        print(f"  Properties found: {len(found_urls)}")
        print(f"  New properties: {len(new_urls)}")
        print(f"  Successfully extracted: {len(extracted_ids)}")
        print(f"  Total properties tracked: {len(all_scraped_ids)}")

        return len(extracted_ids) > 0


def test_incremental_sync():
    """Test the complete incremental sync process"""

    print("🧪 TESTING COMPLETE INCREMENTAL SYNC SYSTEM")
    print("="*60)

    scraper = IncrementalPropertyScraper()

    # Brisbane search URL
    start_url = "https://www.realestate.com.au/buy/property-house-in-brisbane+-+greater+region,+qld/list-1?activeSort=list-date&source=refinement"

    # Test with 2 pages, max 3 new properties for testing
    success = scraper.run_incremental_sync(
        start_url=start_url,
        max_pages=2,
        max_new_properties=3  # Limit for testing
    )

    if success:
        print(f"\n🎯 INCREMENTAL SYNC TEST SUCCESSFUL!")
        print(f"📁 Check data/properties/ for extracted property data")
        print(f"🖼️ Check data/images/ for downloaded property images")
        print(f"📊 Check data/tracking/ for sync logs and tracking data")
        return True
    else:
        print(f"\n❌ Incremental sync test failed")
        return False


if __name__ == "__main__":
    test_incremental_sync()