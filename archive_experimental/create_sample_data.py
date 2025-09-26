#!/usr/bin/env python3
"""
Create sample property data for demonstration purposes
Uses existing successful extractions as templates
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

def create_sample_properties():
    """Create 5 sample properties based on successful extractions"""

    print("🏗️ CREATING SAMPLE PROPERTY DATA")
    print("="*50)

    # Sample property variations
    samples = [
        {
            "id": "149008036",
            "title": "13 Noble Street, Wilston, Qld 4051",
            "property_type": "house",
            "bedrooms": 3,
            "bathrooms": 2,
            "car_spaces": 3,
            "land_size": "607m²",
            "offer": "Offers over $1.25M",
            "agent_name": "Ben Jackson",
            "agency_name": "Metrocity Realty",
            "features": ["Air conditioning", "Shed", "Deck", "Study", "Garage"],
            "highlights": ["Renovated kitchen", "Prime location", "Family home"]
        },
        {
            "id": "148928524",
            "title": "1909/289 Grey Street, South Bank, Qld 4101",
            "property_type": "apartment",
            "bedrooms": 3,
            "bathrooms": 2,
            "car_spaces": 2,
            "land_size": "142m²",
            "offer": "$850,000",
            "agent_name": "Elisa Wellington",
            "agency_name": "Property Services - South Brisbane",
            "features": ["Pool", "Gym", "Balcony", "River views", "Security"],
            "highlights": ["CBD location", "River views", "Luxury finishes"]
        },
        {
            "id": "149007892",
            "title": "45 Paddington Terrace, Paddington, Qld 4064",
            "property_type": "townhouse",
            "bedrooms": 4,
            "bathrooms": 3,
            "car_spaces": 2,
            "land_size": "320m²",
            "offer": "Auction Saturday",
            "agent_name": "Sarah Mitchell",
            "agency_name": "Ray White Paddington",
            "features": ["Courtyard", "Wine cellar", "Home office", "Solar panels"],
            "highlights": ["Character home", "Walk to cafes", "Private courtyard"]
        },
        {
            "id": "149009145",
            "title": "12/88 Bowen Street, Spring Hill, Qld 4000",
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "car_spaces": 1,
            "land_size": "95m²",
            "offer": "$595,000",
            "agent_name": "Michael Chen",
            "agency_name": "Place Estate Agents",
            "features": ["City views", "Concierge", "Rooftop garden", "Storage cage"],
            "highlights": ["CBD apartment", "Great investment", "City views"]
        },
        {
            "id": "149010456",
            "title": "78 Ashgrove Avenue, Ashgrove, Qld 4060",
            "property_type": "house",
            "bedrooms": 5,
            "bathrooms": 3,
            "car_spaces": 4,
            "land_size": "821m²",
            "offer": "$1.8M - $1.95M",
            "agent_name": "David Thompson",
            "agency_name": "Harcourts Ashgrove",
            "features": ["Pool", "Tennis court", "Workshop", "Garden shed", "Solar"],
            "highlights": ["Family estate", "Premium location", "Entertainer's paradise"]
        }
    ]

    data_dir = Path("data/properties")
    data_dir.mkdir(parents=True, exist_ok=True)

    for i, sample in enumerate(samples, 1):
        property_data = {
            "id": sample["id"],
            "url": f"https://www.realestate.com.au/property-{sample['property_type']}-qld-sample-{sample['id']}",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "method": "refined_xpath_container_extraction",
            "title": sample["title"],
            "address": sample["title"],
            "full_address": sample["title"],
            "bedrooms": sample["bedrooms"],
            "bathrooms": sample["bathrooms"],
            "car_spaces": sample["car_spaces"],
            "land_size": sample["land_size"],
            "offer": sample["offer"],
            "agent_name": sample["agent_name"],
            "agency_name": sample["agency_name"],
            "agency_address": f"{random.randint(100, 999)} Sample Street, BRISBANE, QLD 4000",
            "property_type": sample["property_type"],
            "property_features": sample["features"] + [
                f"Land size: {sample['land_size']}",
                f"Bedrooms: {sample['bedrooms']}",
                f"Bathrooms: {sample['bathrooms']}",
                "Modern fixtures",
                "Quality finishes"
            ],
            "property_highlights": sample["highlights"] + [
                "Excellent location",
                "Quality construction",
                "Great value"
            ],
            "description_title": f"PERFECT {sample['property_type'].upper()} IN PRIME LOCATION!",
            "description_body": f"This {sample['bedrooms']} bedroom {sample['property_type']} offers exceptional value in a prime location. Features include {', '.join(sample['features'][:3])} and much more. Perfect for families or investors looking for quality and location.",
            "property_id": sample["id"],
            "inspections": [
                {
                    "time": "Saturday 12:00-12:30pm",
                    "source": "sample_data"
                }
            ],
            "images": [
                {
                    "url": f"https://i2.au.reastatic.net/800x600/sample_{sample['id']}/main.jpg",
                    "type": "main_photo"
                },
                {
                    "url": f"https://i2.au.reastatic.net/360x270/sample_{sample['id']}/image1.jpg",
                    "type": "property_photo"
                },
                {
                    "url": f"https://i2.au.reastatic.net/360x270/sample_{sample['id']}/image2.jpg",
                    "type": "property_photo"
                }
            ]
        }

        # Save sample property
        filename = f"sample_property_{i}_{sample['property_type']}.json"
        filepath = data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(property_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Created sample {i}: {sample['title']}")
        print(f"   Type: {sample['property_type']}")
        print(f"   Bedrooms: {sample['bedrooms']}, Bathrooms: {sample['bathrooms']}")
        print(f"   Features: {len(property_data['property_features'])} items")
        print(f"   File: {filename}")

    print(f"\n🎉 SAMPLE DATA CREATION COMPLETE!")
    print(f"📁 Created 5 sample properties in data/properties/")
    print(f"📋 Each property demonstrates different:")
    print(f"   - Property types (house, apartment, townhouse)")
    print(f"   - Pricing formats (offers, fixed price, auction)")
    print(f"   - Feature variations (pools, sheds, views, etc.)")
    print(f"   - Agent and agency details")

if __name__ == "__main__":
    create_sample_properties()