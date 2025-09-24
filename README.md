# Real Estate Scraper

A robust web scraper for realestate.com.au that can reliably extract property listings and detailed information, including images. Designed to handle anti-bot protection and perform incremental synchronization.

## Features

- **Comprehensive Data Extraction**: Scrapes property details, images, and agent information
- **Enhanced Anti-Bot Protection**: Advanced stealth mode with webdriver masking and realistic behavior
- **Proxy Support**: Built-in proxy rotation support for IP distribution and rate limit avoidance
- **Optimized Performance**: 60-80% faster execution with smart delay optimization
- **Incremental Synchronization**: Detects new, changed, and removed properties
- **Periodic Updates**: Can run automatically on a schedule
- **Robust Error Handling**: Continues scraping even when individual properties fail
- **Image Downloads**: Automatically downloads and organizes property images
- **State Persistence**: Tracks scraped properties to avoid duplicates
- **Debug Tools**: Built-in connection testing and debugging utilities

## Installation

1. Clone or download the project
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

The scraper provides a command-line interface with several modes:

### Full Scrape (First Run)
Scrape the first 100 properties from Brisbane listings:
```bash
python main.py full
```

With custom parameters:
```bash
python main.py full --max-properties 50 --url "https://www.realestate.com.au/buy/in-melbourne,+vic/list-1"
```

With proxy support:
```bash
python main.py full --max-properties 100 --proxy-server http://proxy:8080 --proxy-username user --proxy-password pass
```

### Incremental Sync
Check for new/changed properties and update data:
```bash
python main.py sync
```

### Periodic Sync
Run incremental sync every 24 hours (or custom interval):
```bash
python main.py periodic --interval 12
```

### Check Status
View scraping statistics and recent activity:
```bash
python main.py status
```

## Testing & Debugging

### Connection Testing
Test basic connectivity and debug issues:
```bash
# Basic connection test
python test_connection.py

# Test with proxy
python test_connection.py --proxy http://proxy:8080 username password
```

### Small Test Runs
Always test with small batches first:
```bash
# Test with 10 properties
python main.py full --max-properties 10

# System tests
python test_scraper.py
```

## Data Structure

The scraper organizes data as follows:

```
data/
├── properties/          # JSON files for each property
│   ├── 149128636.json
│   └── ...
├── images/             # Property images by ID
│   ├── 149128636/
│   │   ├── image_001.jpg
│   │   └── ...
│   └── ...
└── logs/              # Scraper logs and state
    ├── scraper.log
    ├── last_sync.json
    └── scraped_properties.json
```

Each property JSON contains:
- Basic information (title, price, address)
- Detailed features and description
- Image URLs and local paths
- Agent contact information
- Scraping timestamps

## Anti-Bot Protection

The scraper implements advanced measures to avoid detection:
- **Enhanced Stealth Mode**: JavaScript injection to mask webdriver properties
- **Realistic Browser Profile**: Updated user agent and comprehensive HTTP headers
- **Optimized Delays**: Smart timing (2-5 seconds between properties, 1-3 seconds between pages)
- **Proxy Support**: Built-in proxy rotation for IP distribution
- **Browser Context**: Realistic viewport (1366x768) and browser arguments
- **Error Handling**: Automatic retry with exponential backoff for 429 errors
- **Updated Selectors**: Modern CSS selectors for current website structure

## Performance & Timing

**Optimized Performance (v2.0):**
- **Without proxy**: ~25-45 minutes for 100 properties
- **With proxy**: ~15-25 minutes for 100 properties
- **60-80% faster** than previous version due to optimized delays

**Recommended Testing Approach:**
1. Test connection: `python test_connection.py`
2. Small batch: `python main.py full --max-properties 10`
3. Full run: `python main.py full --max-properties 100`

## Incremental Updates

The sync system can detect:
- **New properties**: Not previously scraped
- **Changed properties**: Price, description, or features updated
- **Removed properties**: No longer in listings (marked as inactive)

## Customization

### Changing Target Location
Modify the URL in the main script or use the `--url` parameter:
```bash
python main.py full --url "https://www.realestate.com.au/buy/in-sydney,+nsw/list-1"
```

### Adjusting Delays
The scraper is now optimized for performance. Edit `_random_delay()` calls in `scraper.py`:
```python
# Between properties (currently optimized: 2-5 seconds)
await self._random_delay(2, 5)

# Between pages (currently optimized: 1-3 seconds)
await self._random_delay(1, 3)

# Increase delays if encountering rate limits
await self._random_delay(5, 15)  # More conservative
```

### Adding New Fields
Extend the `PropertyDetailed` dataclass in `scraper.py` and update the extraction logic in `scrape_property_details()`.

## Troubleshooting

### Rate Limiting (429 Errors)
If you encounter rate limiting:
1. Use proxy services for IP rotation
2. Increase delays between requests in `scraper.py`
3. Run during off-peak hours
4. Reduce `max_properties` value
5. Test connectivity first with `python test_connection.py`

### Missing Data
If properties are missing data:
1. Check the logs in `data/logs/scraper.log`
2. Update CSS selectors in `_extract_property_basic()` and `scrape_property_details()`
3. Test with a single property first

### Browser Issues
If Playwright fails:
```bash
# Reinstall browsers
playwright install --force chromium

# Test connection first
python test_connection.py

# Try headful mode for debugging (modify test_connection.py)
# Set headless=False in the script
```

## Scheduling

For production use, set up a cron job for periodic syncing:
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/scraper && python main.py sync

# Or run continuous periodic mode
python main.py periodic --interval 6
```

## Legal Considerations

- Respect robots.txt and terms of service
- Use reasonable delays to avoid overloading servers
- Consider the website's API if available
- This tool is for educational and research purposes

## Architecture

- `scraper.py`: Core scraping logic with Playwright
- `incremental_sync.py`: Change detection and sync logic
- `main.py`: CLI interface and orchestration
- `data/schema.md`: Documentation of data structure