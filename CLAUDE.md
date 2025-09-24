# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based web scraper for realestate.com.au that extracts property listings and detailed information using Playwright for browser automation. The project implements anti-bot protection measures and supports incremental synchronization for ongoing data collection.

## Core Architecture

The system consists of three main components:

1. **scraper.py** - Core scraping engine using Playwright
   - `RealEstateScraper` class handles browser automation and data extraction
   - `PropertyBasic` and `PropertyDetailed` dataclasses define data structures
   - Implements anti-bot measures with random delays and realistic browser behavior

2. **incremental_sync.py** - Change detection and synchronization
   - `IncrementalSyncer` detects new, changed, and removed properties
   - `PeriodicSyncer` runs continuous sync operations
   - Uses MD5 hashing to detect property changes

3. **main.py** - CLI interface and orchestration
   - Provides `full`, `sync`, `periodic`, and `status` commands
   - Coordinates between scraper and sync components

## Data Storage Structure

```
data/
├── properties/          # Individual property JSON files (by ID)
├── images/             # Property images organized by property ID
├── logs/              # State files and logs
    ├── scraper.log
    ├── last_sync.json
    ├── scraped_properties.json
    └── failed_properties.json
```

## Development Commands

### Setup and Installation
```bash
# Initial setup (installs dependencies and Playwright browsers)
./setup.sh

# Manual dependency installation
pip install -r requirements.txt
playwright install chromium
```

### Running the Scraper
```bash
# Full scrape (first run)
python main.py full --max-properties 100

# With proxy support
python main.py full --max-properties 100 --proxy-server http://proxy:8080 --proxy-username user --proxy-password pass

# Incremental sync
python main.py sync

# Periodic sync (every 24 hours)
python main.py periodic --interval 24

# Check status
python main.py status
```

### Testing
```bash
# Test connection and debug issues
python test_connection.py

# Test with proxy
python test_connection.py --proxy http://proxy:8080 username password

# Run system tests
python test_scraper.py

# Test with small batch first
python main.py full --max-properties 10
```

## Key Implementation Details

### Anti-Bot Protection
- Optimized random delays (1-5 seconds between properties, 1-3 seconds between pages)
- Enhanced stealth mode with webdriver property masking
- Realistic user agent and comprehensive HTTP headers
- Browser context with realistic viewport (1366x768)
- JavaScript injection to mask automation signatures
- Proxy support for IP rotation and geographic distribution
- Automatic retry with exponential backoff for 429 errors

### Data Extraction Flow
1. **Listing Page Scraping**: Extract basic property info from search results
2. **Detail Page Scraping**: Navigate to individual properties for complete data
3. **Image Download**: Save property images locally with organized file structure
4. **State Persistence**: Track scraped properties to enable incremental updates

### Change Detection
- Compares MD5 hashes of key property fields (title, price, description, features)
- Detects new properties not in existing dataset
- Identifies removed properties no longer in listings
- Updates changed properties with new data

### Error Handling
- Individual property failures don't stop the entire scrape
- Comprehensive logging of errors and retry attempts
- Failed properties tracked in separate log files
- Graceful handling of rate limiting and timeouts

## Configuration

### Customizing Target Location
Modify the default URL in main.py or use the `--url` parameter:
```python
# Default Brisbane URL in main.py
'https://www.realestate.com.au/buy/in-brisbane+-+greater+region,+qld/list-1'
```

### Adjusting Delays
Edit `_random_delay()` calls in scraper.py (currently optimized for speed):
```python
# Between properties (currently 2-5 seconds)
await self._random_delay(2, 5)

# Between pages (currently 1-3 seconds)
await self._random_delay(1, 3)
```

### Adding New Data Fields
1. Extend the `PropertyDetailed` dataclass in scraper.py
2. Update extraction logic in `scrape_property_details()`
3. Modify the data schema documentation in data/schema.md