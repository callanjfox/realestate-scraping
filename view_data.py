#!/usr/bin/env python3
"""
Data viewer for scraped properties
Usage: python3 view_data.py [count]
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def view_scraped_data(count=10):
    """View scraped property data"""

    data_dir = Path("data/properties")

    if not data_dir.exists():
        print("❌ No data directory found")
        return

    # Get all property files, sorted by newest first
    property_files = sorted(data_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not property_files:
        print("❌ No property files found")
        return

    print(f"📊 SCRAPED PROPERTY DATA")
    print(f"Total properties: {len(property_files)}")
    print(f"Showing latest {min(count, len(property_files))} properties:")
    print("="*80)

    for i, file_path in enumerate(property_files[:count]):
        try:
            with open(file_path, 'r') as f:
                prop = json.load(f)

            print(f"\n{i+1}. Property ID: {prop.get('id')}")
            print(f"   Title: {prop.get('title', 'No title')}")
            print(f"   Price: {prop.get('price', 'No price')}")
            print(f"   Bedrooms: {prop.get('bedrooms', 'N/A')}")
            print(f"   Bathrooms: {prop.get('bathrooms', 'N/A')}")
            print(f"   Parking: {prop.get('parking', 'N/A')}")
            print(f"   URL: {prop.get('url', 'No URL')}")
            print(f"   Scraped: {prop.get('scraped_at', 'Unknown')}")
            print(f"   Method: {prop.get('method', 'Unknown')}")

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    print(f"\n📁 Data location: {data_dir.absolute()}")
    print(f"🔍 View individual files: cat data/properties/[filename].json")


def view_by_method(method_filter=None):
    """View properties by scraping method"""

    data_dir = Path("data/properties")
    property_files = list(data_dir.glob("*.json"))

    methods = {}
    filtered_files = []

    for file_path in property_files:
        try:
            with open(file_path, 'r') as f:
                prop = json.load(f)

            method = prop.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1

            if method_filter and method_filter in method:
                filtered_files.append((file_path, prop))

        except Exception as e:
            continue

    print(f"\n📈 PROPERTIES BY METHOD:")
    for method, count in methods.items():
        print(f"  {method}: {count} properties")

    if method_filter and filtered_files:
        print(f"\n🔍 PROPERTIES WITH METHOD '{method_filter}':")
        for file_path, prop in filtered_files[:10]:
            print(f"  {prop.get('id')}: {prop.get('title', 'No title')[:50]}...")

    return methods


if __name__ == "__main__":
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except:
            count = 10

    view_scraped_data(count)

    # Show methods breakdown
    methods = view_by_method()

    print(f"\n📋 USAGE:")
    print(f"  python3 view_data.py 20    # View 20 latest properties")
    print(f"  python3 view_data.py 100   # View 100 latest properties")
