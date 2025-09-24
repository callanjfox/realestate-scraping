# Data Storage Schema

## Directory Structure
```
data/
├── properties/          # JSON files for each property
├── images/             # Property images organized by property ID
├── logs/              # Scraping logs and state files
└── schema.md          # This file
```

## Property JSON Structure
Each property is stored as a JSON file named `{property_id}.json`:

```json
{
  "id": "149128636",
  "url": "https://www.realestate.com.au/property-apartment-qld-indooroopilly-149128636",
  "scraped_at": "2025-09-24T02:25:22Z",
  "last_updated": "2025-09-24T02:25:22Z",
  "title": "Property Title",
  "price": "$XXX,XXX",
  "address": {
    "street": "123 Example St",
    "suburb": "Indooroopilly",
    "state": "QLD",
    "postcode": "4068"
  },
  "property_type": "Apartment",
  "bedrooms": 2,
  "bathrooms": 1,
  "parking": 1,
  "land_size": null,
  "building_size": "65 m²",
  "description": "Full property description...",
  "features": ["Feature 1", "Feature 2"],
  "images": [
    {
      "url": "https://...",
      "local_path": "data/images/149128636/image_001.jpg",
      "description": "Living room"
    }
  ],
  "agent": {
    "name": "Agent Name",
    "agency": "Agency Name",
    "phone": "+61 X XXXX XXXX"
  },
  "listing_date": "2025-09-20",
  "status": "active"
}
```

## State Files
- `data/logs/last_sync.json` - Tracks last successful sync timestamp
- `data/logs/scraped_properties.json` - List of all scraped property IDs
- `data/logs/failed_properties.json` - List of properties that failed to scrape