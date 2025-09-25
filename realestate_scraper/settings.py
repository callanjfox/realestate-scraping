"""
Scrapy settings for realestate_scraper project
Optimized for anti-bot evasion and real estate scraping
"""

import os

# Scrapy settings for realestate_scraper project
BOT_NAME = 'realestate_scraper'

SPIDER_MODULES = ['realestate_scraper.spiders']
NEWSPIDER_MODULE = 'realestate_scraper.spiders'

# Obey robots.txt rules (set to False for realestate.com.au)
ROBOTSTXT_OBEY = False

# Configure pipelines
ITEM_PIPELINES = {
    'realestate_scraper.pipelines.JsonWriterPipeline': 300,
    'realestate_scraper.pipelines.PropertyImagesPipeline': 400,
}

# Images store
IMAGES_STORE = 'data/images'

# Configure delays and concurrency for anti-bot evasion
DOWNLOAD_DELAY = 3  # 3 seconds between requests (increased)
RANDOMIZE_DOWNLOAD_DELAY = True  # 0.5 * to 1.5 * DOWNLOAD_DELAY
DOWNLOAD_TIMEOUT = 60  # Increased timeout for ScraperAPI rendering

# Limit concurrent requests
CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Auto-throttling settings (more conservative)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 15
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.5  # More conservative
AUTOTHROTTLE_DEBUG = True

# Configure user agent rotation
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
]

# Default user agent (will be overridden by middleware)
USER_AGENT = USER_AGENT_LIST[0]

# Configure middlewares for anti-bot evasion
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # Disable default
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,     # Enable random user agents
    'realestate_scraper.middlewares.ProxyMiddleware': 500,               # Custom proxy middleware
    'realestate_scraper.middlewares.HeadersMiddleware': 600,             # Custom headers
}

# Headers to appear more like a real browser
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-AU,en;q=0.9,en-US;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]

# Cache settings (disable for live scraping)
HTTPCACHE_ENABLED = False

# Log level
LOG_LEVEL = 'INFO'

# Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Proxy settings (can be overridden via spider arguments)
PROXY_ENABLED = False
PROXY_SERVER = None
PROXY_USERNAME = None
PROXY_PASSWORD = None

# ScraperAPI settings
SCRAPERAPI_KEY = None

# Custom settings for realestate.com.au
REALESTATE_CUSTOM_SETTINGS = {
    'handle_httpstatus_list': [403, 429],  # Don't treat these as errors
    'cookies_enabled': True,
    'session_persistence': True,
}