#!/usr/bin/env python3
"""
Test feature extraction from description to demonstrate shed detection
"""

import re

def extract_features_from_description_text(text):
    """Extract features from description text that might mention sheds, pools, etc."""

    features = []
    text_lower = text.lower()

    # Common property features to look for
    feature_keywords = [
        'shed', 'workshop', 'garage', 'carport', 'pool', 'spa', 'deck', 'balcony',
        'air conditioning', 'heating', 'fireplace', 'dishwasher', 'alarm', 'intercom',
        'ensuite', 'walk-in robe', 'built-in robes', 'study', 'office', 'rumpus',
        'family room', 'living room', 'dining room', 'kitchen', 'laundry',
        'storage', 'courtyard', 'garden', 'lawn', 'timber floors', 'tiles',
        'carpet', 'stone benchtops', 'gas cooking', 'electric cooking',
        'solar panels', 'water tank', 'bore', 'irrigation'
    ]

    # Process all lines first, then check for keywords
    lines = re.split(r'[\n]', text)

    for keyword in feature_keywords:
        if keyword in text_lower:
            for line in lines:
                if keyword in line.lower():
                    # Clean up the line
                    clean_line = line.strip().lstrip('-\t•').strip()

                    if 5 < len(clean_line) < 100 and clean_line:
                        features.append(clean_line)

    # Remove duplicates while preserving order
    unique_features = []
    seen = set()
    for feature in features:
        if feature.lower() not in seen:
            seen.add(feature.lower())
            unique_features.append(feature)

    return unique_features

# Test with the actual description
description = """Be quick to see this refurbished two-level home on a generous 607sqm block of land, located in the popular growth suburb of Wilston.

Upstairs you will find:
-	3 generous sized bedrooms with ceiling fans
-	Spacious living/dining area with polished timber floors and air conditioning
-	Renovated kitchen with stone benchtops and new 2pac cupboards
-	Huge covered rear deck overlooking a leafy backyard
-	Modern bathroom with large shower
-	Extra study room or home office
-	Front staircase and landing

Downstairs comes with:
-	2 multiple purpose rooms (just under legal height at 2.35m) with scope to lower flooring or remove ceiling to create the extra few cmâs.
-	Spacious rumpus area or games room
-	Stylish near new bathroom
-	Kitchen space with cabinetry being replaced
-	Long garage plus storage
-	Concrete patio area under the upstairs deck
-	The downstairs has had some water damage from Cyclone Alfred and in the process of being fully refurbished back to original condition through insurance.
-	Huge back shed or work space
-	Landscaped yard with plenty of off-street parking

The property is located in a convenient Wilston position within the Wilson State School and Kelvin Grove State College. It is walking distance to bus/train, popular Downey Park and a short bike ride to the CBD.

A safe first/second home or smart investment in a blue chip location!"""

print("🔍 TESTING FEATURE EXTRACTION FROM DESCRIPTION")
print("="*60)

features = extract_features_from_description_text(description)

print(f"✅ Extracted {len(features)} features:")
for i, feature in enumerate(features, 1):
    print(f"  {i}. {feature}")

print(f"\n🎯 SHED DETECTION:")
shed_features = [f for f in features if 'shed' in f.lower()]
if shed_features:
    for shed in shed_features:
        print(f"✅ Found shed: {shed}")
else:
    print("❌ Shed not detected")