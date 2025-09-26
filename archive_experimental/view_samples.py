#!/usr/bin/env python3
"""
View Sample Property Data
Shows all sample properties extracted by the XPath-based scraper
"""

import json
from pathlib import Path
import glob

def view_sample_properties():
    """Display all sample property data"""

    print("🏠 SAMPLE PROPERTY DATA OVERVIEW")
    print("="*60)

    sample_files = glob.glob("data/properties/sample_property_*.json")
    sample_files.sort()

    if not sample_files:
        print("❌ No sample properties found")
        return

    for i, filepath in enumerate(sample_files, 1):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"\n📋 PROPERTY {i}: {Path(filepath).name}")
            print("-" * 50)
            print(f"🏠 Title: {data.get('title', 'N/A')}")
            print(f"🏷️ Type: {data.get('property_type', 'N/A')}")
            print(f"💰 Offer: {data.get('offer', 'N/A')}")
            print(f"🛏️ Bedrooms: {data.get('bedrooms', 'N/A')}")
            print(f"🛁 Bathrooms: {data.get('bathrooms', 'N/A')}")
            print(f"🚗 Car Spaces: {data.get('car_spaces', 'N/A')}")
            print(f"📐 Land Size: {data.get('land_size', 'N/A')}")
            print(f"👤 Agent: {data.get('agent_name', 'N/A')}")
            print(f"🏢 Agency: {data.get('agency_name', 'N/A')}")

            features = data.get('property_features', [])
            highlights = data.get('property_highlights', [])
            images = data.get('images', [])

            print(f"📋 Features ({len(features)} items):")
            for feature in features[:5]:  # Show first 5
                print(f"   • {feature}")
            if len(features) > 5:
                print(f"   ... and {len(features) - 5} more")

            print(f"⭐ Highlights ({len(highlights)} items):")
            for highlight in highlights[:3]:  # Show first 3
                print(f"   • {highlight}")
            if len(highlights) > 3:
                print(f"   ... and {len(highlights) - 3} more")

            print(f"📸 Images: {len(images)} collected")

        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")

    print(f"\n🎉 SAMPLE DATA SUMMARY")
    print(f"📁 Total samples: {len(sample_files)}")
    print(f"📋 Property types: house, apartment, townhouse")
    print(f"💰 Price formats: offers, fixed prices, auctions")
    print(f"📊 Data fields: ~20+ per property")
    print(f"📸 Images: Sample URLs provided")

    print(f"\n🔧 USAGE:")
    print(f"cat data/properties/sample_property_1_house.json")
    print(f"ls data/properties/sample_*")

if __name__ == "__main__":
    view_sample_properties()