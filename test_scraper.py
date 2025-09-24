#!/usr/bin/env python3
"""
Test script for the real estate scraper
Tests the system components without requiring full browser installation
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone

# Test the data structures and basic functionality
from scraper import PropertyBasic, PropertyDetailed, RealEstateScraper
from incremental_sync import IncrementalSyncer


def test_data_structures():
    """Test the data structure classes"""
    print("Testing data structures...")

    # Test PropertyBasic
    basic = PropertyBasic(
        id="149128636",
        url="https://www.realestate.com.au/property-apartment-qld-indooroopilly-149128636",
        title="Modern 2BR Apartment in Indooroopilly",
        price="$450,000",
        address="123 Main St, Indooroopilly QLD 4068",
        property_type="Apartment",
        bedrooms=2,
        bathrooms=1,
        parking=1
    )
    print(f"✓ PropertyBasic: {basic.id} - {basic.title}")

    # Test PropertyDetailed
    detailed = PropertyDetailed(
        id="149128636",
        url="https://www.realestate.com.au/property-apartment-qld-indooroopilly-149128636",
        scraped_at=datetime.now(timezone.utc).isoformat(),
        last_updated=datetime.now(timezone.utc).isoformat(),
        title="Modern 2BR Apartment in Indooroopilly",
        price="$450,000",
        address={
            "full": "123 Main St, Indooroopilly QLD 4068",
            "street": "123 Main St",
            "suburb": "Indooroopilly",
            "state": "QLD",
            "postcode": "4068"
        },
        property_type="Apartment",
        bedrooms=2,
        bathrooms=1,
        parking=1,
        description="Beautiful apartment with modern amenities...",
        features=["Air Conditioning", "Built-in Wardrobes", "Balcony"],
        images=[
            {
                "url": "https://example.com/image1.jpg",
                "local_path": "data/images/149128636/image_001.jpg",
                "description": "Living room"
            }
        ],
        agent={
            "name": "John Smith",
            "agency": "ABC Real Estate",
            "phone": "0412 345 678"
        }
    )
    print(f"✓ PropertyDetailed: {detailed.id} - {len(detailed.features)} features, {len(detailed.images)} images")

    return basic, detailed


def test_file_operations(detailed_property):
    """Test file operations"""
    print("\nTesting file operations...")

    # Create test data directory
    data_dir = Path("test_data")
    properties_dir = data_dir / "properties"
    properties_dir.mkdir(parents=True, exist_ok=True)

    # Save property to JSON
    property_file = properties_dir / f"{detailed_property.id}.json"

    # Convert to dict for JSON serialization
    from dataclasses import asdict
    property_data = asdict(detailed_property)

    with open(property_file, 'w') as f:
        json.dump(property_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved property to: {property_file}")

    # Read it back
    with open(property_file, 'r') as f:
        loaded_data = json.load(f)

    print(f"✓ Loaded property: {loaded_data['id']} - {loaded_data['title']}")

    return property_file


def test_incremental_sync():
    """Test incremental sync logic"""
    print("\nTesting incremental sync logic...")

    # Create logs directory first
    logs_dir = Path("test_data/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    syncer = IncrementalSyncer("test_data")

    # Create some test property data
    test_properties = [
        {
            'id': '123456',
            'title': 'Test Property 1',
            'price': '$500,000',
            'address': 'Test Address 1',
            'property_type': 'House',
            'bedrooms': 3,
            'bathrooms': 2,
            'parking': 2,
            'status': 'active'
        },
        {
            'id': '789012',
            'title': 'Test Property 2',
            'price': '$750,000',
            'address': 'Test Address 2',
            'property_type': 'Apartment',
            'bedrooms': 2,
            'bathrooms': 1,
            'parking': 1,
            'status': 'active'
        }
    ]

    # Test hash calculation
    hash1 = syncer._calculate_property_hash(test_properties[0])
    hash2 = syncer._calculate_property_hash(test_properties[1])

    print(f"✓ Property hashes calculated: {hash1[:8]}..., {hash2[:8]}...")

    # Test that identical properties produce same hash
    hash1_duplicate = syncer._calculate_property_hash(test_properties[0])
    assert hash1 == hash1_duplicate, "Identical properties should have same hash"
    print("✓ Hash consistency verified")

    # Test that different properties produce different hashes
    assert hash1 != hash2, "Different properties should have different hashes"
    print("✓ Hash uniqueness verified")


def test_scraper_initialization():
    """Test scraper initialization"""
    print("\nTesting scraper initialization...")

    scraper = RealEstateScraper(data_dir="test_data", max_properties=10)

    print(f"✓ Scraper initialized with data_dir: {scraper.data_dir}")
    print(f"✓ Max properties: {scraper.max_properties}")
    print(f"✓ Properties directory: {scraper.properties_dir}")
    print(f"✓ Images directory: {scraper.images_dir}")
    print(f"✓ Logs directory: {scraper.logs_dir}")

    # Test directories were created
    assert scraper.properties_dir.exists(), "Properties directory should exist"
    assert scraper.images_dir.exists(), "Images directory should exist"
    assert scraper.logs_dir.exists(), "Logs directory should exist"

    print("✓ All directories created successfully")

    # Test state loading/saving
    scraper.scraped_properties.add("test_property_1")
    scraper.scraped_properties.add("test_property_2")
    scraper.failed_properties.add("failed_property_1")

    scraper._save_state()
    print("✓ State saved")

    # Create new scraper and test state loading
    new_scraper = RealEstateScraper(data_dir="test_data", max_properties=10)

    assert "test_property_1" in new_scraper.scraped_properties, "Scraped properties should be loaded"
    assert "test_property_2" in new_scraper.scraped_properties, "Scraped properties should be loaded"
    assert "failed_property_1" in new_scraper.failed_properties, "Failed properties should be loaded"

    print("✓ State loaded successfully")


def test_utility_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")

    scraper = RealEstateScraper(data_dir="test_data", max_properties=10)

    # Test number extraction
    test_cases = [
        ("3 bed", 3),
        ("2 bath", 2),
        ("1 car", 1),
        ("10 parking", 10),
        ("No beds", None),
        ("", None)
    ]

    for text, expected in test_cases:
        result = scraper._extract_number(text)
        assert result == expected, f"Expected {expected} for '{text}', got {result}"
        print(f"✓ Number extraction: '{text}' -> {result}")


async def test_async_functions():
    """Test async functions that don't require browser"""
    print("\nTesting async functions...")

    scraper = RealEstateScraper(data_dir="test_data", max_properties=10)

    # Test random delay function
    import time
    start_time = time.time()
    await scraper._random_delay(0.1, 0.2)
    end_time = time.time()

    delay_time = end_time - start_time
    assert 0.1 <= delay_time <= 0.3, f"Delay should be between 0.1-0.2s, was {delay_time:.3f}s"
    print(f"✓ Random delay function works: {delay_time:.3f}s")


def cleanup_test_data():
    """Clean up test data"""
    print("\nCleaning up test data...")

    import shutil
    test_dir = Path("test_data")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✓ Test data cleaned up")


async def main():
    """Main test function"""
    print("="*60)
    print("REAL ESTATE SCRAPER - SYSTEM TESTS")
    print("="*60)

    try:
        # Test 1: Data structures
        basic_prop, detailed_prop = test_data_structures()

        # Test 2: File operations
        property_file = test_file_operations(detailed_prop)

        # Test 3: Incremental sync logic
        test_incremental_sync()

        # Test 4: Scraper initialization
        test_scraper_initialization()

        # Test 5: Utility functions
        test_utility_functions()

        # Test 6: Async functions
        await test_async_functions()

        print("\n" + "="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        print("\nThe scraper system is ready to use.")
        print("Note: Browser-dependent tests skipped due to disk space constraints.")
        print("\nTo run the actual scraper:")
        print("1. Free up disk space")
        print("2. Run: playwright install chromium")
        print("3. Run: python main.py full --max-properties 5")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Always clean up
        cleanup_test_data()


if __name__ == "__main__":
    asyncio.run(main())