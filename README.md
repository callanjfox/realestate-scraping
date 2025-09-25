# Real Estate Scraper v3.0 - Kasada Bypass Solution

A robust web scraper for realestate.com.au that successfully bypasses Kasada enterprise protection using ScrapingBee service. This project demonstrates how to overcome sophisticated anti-bot protection to extract property listings and detailed information.

**🎯 BREAKTHROUGH ACHIEVED:** Successfully scraped 130+ properties from realestate.com.au by bypassing Kasada enterprise protection using ScrapingBee stealth proxy service.

## ✅ What Works

**SUCCESSFUL APPROACH: ScrapingBee Integration**
- **Service**: ScrapingBee with stealth proxy
- **Success Rate**: 75%+ against Kasada protection
- **Performance**: ~3-4 seconds per property
- **Cost**: ~7.3 credits per property
- **Capacity**: ~137 properties per 1000 credits

## Core Architecture

The system now includes both legacy approaches and the proven ScrapingBee solution:

1. **ScrapingBee Integration** - ✅ WORKING SOLUTION
   - Bypasses Kasada enterprise protection
   - Uses stealth residential proxies
   - Handles JavaScript challenges automatically

2. **Legacy Scrapy System** - Production-ready framework
   - Complete spider architecture with items, pipelines, middlewares
   - Works perfectly on non-Kasada protected sites (e.g., RightMove UK)

3. **Legacy Playwright System** - Original approach
   - Browser automation with anti-bot measures
   - Blocked by Kasada protection on realestate.com.au

## Installation

1. Clone or download the project
2. Install Python dependencies:
```bash
pip install -r requirements.txt
pip install scrapingbee
```

3. Get ScrapingBee API key:
   - Visit: https://www.scrapingbee.com/
   - Sign up for trial (1000 credits) or paid plan
   - Get API key from dashboard

## Usage

### ScrapingBee Approach (RECOMMENDED)

**For realestate.com.au (Kasada protected):**

```bash
# Test ScrapingBee with your API key
python3 scrapingbee_optimized.py

# Production scrape (edit API key in script first)
python3 final_working_scrape.py
```

**Proven Working Configuration:**
```python
params = {
    'render_js': True,
    'block_resources': False,
    'stealth_proxy': True,
    'country_code': 'AU'
}
```

### Legacy Scrapy Approach

**For non-Kasada sites (e.g., RightMove UK):**

```bash
# Works perfectly without ScrapingBee
python3 main.py full --engine scrapy --max-properties 100

# With Oxylabs proxy
python3 main.py full --engine scrapy --max-properties 100 --proxy-server "http://username:password@pr.oxylabs.io:7777"
```

### Data Viewing

**View scraped properties:**
```bash
# View latest 10 properties
python3 view_data.py

# View latest 50 properties
python3 view_data.py 50

# Check scraper status
python3 main.py status
```

## Data Structure

```
data/
├── properties/          # Individual property JSON files
│   ├── scrapingbee_*.json    # ScrapingBee scraped properties
│   ├── final_*.json          # Production scraped properties
│   └── *.json               # Legacy scraped properties
├── images/             # Property images (if image download enabled)
└── logs/              # Scraper logs and state files
    ├── scraper.log
    ├── approach_results/     # Testing results from different approaches
    └── scraped_properties.json
```

## ScrapingBee Economics

**Real Cost Analysis (Based on Trial Results):**
- **Cost per property**: ~7.3 credits
- **Trial (1000 credits)**: ~137 properties
- **Hobby ($49/month, 10k credits)**: ~1,368 properties
- **Freelance ($199/month, 100k credits)**: ~13,684 properties

**Performance:**
- **Time per property**: ~3-4 seconds
- **Properties per hour**: ~900-1,200
- **100 properties**: ~6-8 minutes

## Technical Breakthrough Details

### Why Previous Approaches Failed

**Kasada Enterprise Protection Detected:**
- ✅ Premium Australian residential proxies (Oxylabs)
- ✅ Browser automation (Playwright, Selenium)
- ✅ Comprehensive stealth techniques
- ✅ Human behavior simulation
- ✅ Session building and referrer chains

**Protection Characteristics:**
- **JavaScript challenges**: Client-side cryptographic puzzles
- **Behavioral analysis**: Mouse movements, timing patterns
- **Hardware fingerprinting**: Canvas, WebGL, audio context
- **Request pattern detection**: Headers, timing, sequences

### ScrapingBee Success Factors

**Why ScrapingBee Works:**
- **Specialized Kasada handling**: Designed specifically for enterprise protection
- **Real browser execution**: Full JavaScript context with challenge resolution
- **Advanced fingerprinting**: Hardware-level browser simulation
- **Residential proxy network**: High-quality IPs with realistic usage patterns

## Production Commands

### Setup ScrapingBee Integration

1. **Get API Key**: Sign up at https://www.scrapingbee.com/
2. **Edit scripts**: Replace API key in `scrapingbee_optimized.py` or `final_working_scrape.py`
3. **Run production scrape**

### Quick Start

```bash
# 1. Test ScrapingBee connection
python3 scrapingbee_debug.py

# 2. Run optimized scraping
python3 scrapingbee_optimized.py

# 3. View results
python3 view_data.py 20
```

## Alternative Approaches Tested

**❌ Approaches That Failed Against Kasada:**
1. **Direct access**: HTTP 429 rate limiting
2. **Scrapy + residential proxies**: HTTP 429 even with premium Australian IPs
3. **Browser automation**: Playwright/Selenium blocked by JavaScript challenges
4. **Session building**: Multi-stage approach still detected
5. **Google referrer simulation**: Still rate limited
6. **Mobile interface targeting**: Same protection applied
7. **API endpoint discovery**: Endpoints protected or non-existent
8. **Undetected Chrome**: Browser connection issues in server environment

**✅ Working Alternative:**
- **RightMove UK**: 125+ properties per page, no protection (great for testing architecture)

## Cost Comparison

**ScrapingBee vs Alternatives:**
- **ScrapingBee**: $199/month for 100k credits (~13k properties)
- **Bright Data**: $500+ per month for residential proxies
- **Custom development**: Weeks/months of work with uncertain success
- **Manual collection**: Extremely time-consuming

**ROI Analysis:**
ScrapingBee provides the best value for overcoming enterprise-level protection with minimal development time.

## Files in This Project

**Production Files:**
- `scrapingbee_optimized.py` - Main ScrapingBee scraper
- `final_working_scrape.py` - Production scraper with proven config
- `view_data.py` - Data viewer for scraped properties
- `main.py` - Legacy CLI interface

**Analysis Files:**
- `analyze_scraping_results.py` - Results and cost analysis
- `data/logs/approach_results/` - Testing results from all approaches

**Test Files (Can be removed):**
- `test_*.py` - Various testing approaches
- `approach*.py` - Failed approach implementations
- `breakthrough_*.py` - Experimental scripts

## Troubleshooting

### ScrapingBee Issues

**401 Errors**: API key or account issue
**400 Errors**: Parameter formatting (avoid custom session_id)
**503 Errors**: Temporary server issues
**429 Errors**: Rate limiting (use stealth_proxy=True)

### Data Quality Issues

**Missing prices**: Extraction pattern needs refinement
**Duplicate properties**: Normal - same property on multiple pages
**Empty fields**: Some properties have limited public data

## Legal and Ethical Use

- **Public Data**: Only scrapes publicly available property listings
- **Respectful Delays**: Uses appropriate delays between requests
- **Terms Compliance**: Designed for research and legitimate business use
- **Anti-Bot Bypass**: Uses legitimate commercial services

## Next Steps

1. **Scale Up**: Use remaining ScrapingBee credits for more properties
2. **Property Details**: Enhance extraction for individual property pages
3. **Image Downloads**: Implement image collection for properties
4. **Incremental Updates**: Set up periodic scraping for data freshness
5. **Alternative Sites**: Apply same techniques to Domain.com.au, etc.

---

**🏆 SUCCESS:** This project successfully demonstrates how to overcome enterprise-level anti-bot protection (Kasada) using legitimate commercial services while maintaining ethical scraping practices.