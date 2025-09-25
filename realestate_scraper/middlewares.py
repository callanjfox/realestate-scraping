"""
Custom middlewares for realestate scraper
Handles proxy rotation, headers, and anti-bot evasion
"""

import random
import logging
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.exceptions import NotConfigured


class HeadersMiddleware:
    """Add realistic browser headers to avoid detection"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        """Add realistic headers to request"""

        # Additional headers that make requests look more realistic
        additional_headers = {
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-user': '?1',
        }

        # Add random viewport-related headers
        viewports = [
            '1920,1080',
            '1366,768',
            '1536,864',
            '1440,900',
            '1280,720'
        ]

        additional_headers['X-Viewport'] = random.choice(viewports)

        # Set headers
        for key, value in additional_headers.items():
            request.headers[key] = value

        # Add referrer for non-first requests
        if hasattr(spider, 'referrer_url'):
            request.headers['Referer'] = spider.referrer_url

        return None


class ProxyMiddleware:
    """Handle proxy configuration for ScraperAPI and other proxy services"""

    def __init__(self, settings):
        self.proxy_enabled = settings.getbool('PROXY_ENABLED', False)
        self.proxy_server = settings.get('PROXY_SERVER')
        self.proxy_username = settings.get('PROXY_USERNAME')
        self.proxy_password = settings.get('PROXY_PASSWORD')
        self.scraperapi_key = settings.get('SCRAPERAPI_KEY')

        self.logger = logging.getLogger(__name__)

        if self.proxy_enabled and not (self.proxy_server or self.scraperapi_key):
            raise NotConfigured('Proxy enabled but no proxy server or ScraperAPI key configured')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        """Configure proxy for request"""

        if not self.proxy_enabled:
            return None

        # ScraperAPI direct API approach
        if self.scraperapi_key and not self.proxy_server:
            return self.configure_scraperapi_request(request, spider)

        # Traditional proxy approach
        if self.proxy_server:
            return self.configure_proxy_request(request, spider)

        return None

    def configure_scraperapi_request(self, request, spider):
        """Configure request to use ScraperAPI direct endpoint with advanced options"""

        # Convert original request to ScraperAPI format with enhanced parameters
        original_url = request.url

        # Advanced ScraperAPI parameters for better anti-detection
        params = {
            'api_key': self.scraperapi_key,
            'url': original_url,
            'render': 'true',  # Enable JavaScript rendering
            'country_code': 'au',  # Use Australian IP addresses
            'device_type': 'desktop',  # Desktop user agent
            'premium': 'true',  # Use premium proxies
            'session_number': getattr(spider, 'session_id', 1),  # Session persistence
            'keep_headers': 'true',  # Preserve custom headers
        }

        # Build ScraperAPI URL
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        scraperapi_url = f"http://api.scraperapi.com?{param_string}"

        # Update request URL
        request = request.replace(url=scraperapi_url)

        self.logger.info(f"Using ScraperAPI (render=true, premium, AU) for: {original_url}")
        return None

    def configure_proxy_request(self, request, spider):
        """Configure traditional proxy for request"""

        proxy_url = self.proxy_server

        # Add authentication if provided
        if self.proxy_username and self.proxy_password:
            # Extract protocol and host from proxy_server
            if '://' in proxy_url:
                protocol, rest = proxy_url.split('://', 1)
                proxy_url = f"{protocol}://{self.proxy_username}:{self.proxy_password}@{rest}"

        request.meta['proxy'] = proxy_url
        self.logger.info(f"Using proxy: {self.proxy_server}")

        return None


class RetryMiddleware:
    """Enhanced retry middleware with exponential backoff"""

    def __init__(self, settings):
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = settings.getlist('RETRY_HTTP_CODES', [500, 502, 503, 504, 408, 429])
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST', -1)
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """Process response and determine if retry is needed"""

        if response.status in self.retry_http_codes:
            reason = f'HTTP {response.status}'
            return self._retry(request, reason, spider) or response

        # Check for anti-bot detection patterns
        if self.is_blocked_response(response):
            reason = 'Anti-bot detection'
            return self._retry(request, reason, spider) or response

        return response

    def process_exception(self, request, exception, spider):
        """Handle request exceptions"""

        if isinstance(exception, (ConnectionError, TimeoutError)):
            reason = f'Connection error: {exception}'
            return self._retry(request, reason, spider)

        return None

    def is_blocked_response(self, response):
        """Check if response indicates blocking/anti-bot detection"""

        blocked_indicators = [
            b'blocked',
            b'captcha',
            b'403 forbidden',
            b'access denied',
            b'cloudflare',
            b'rate limit'
        ]

        response_body = response.body.lower()
        return any(indicator in response_body for indicator in blocked_indicators)

    def _retry(self, request, reason, spider):
        """Retry request with exponential backoff"""

        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            self.logger.warning(f"Retrying {request.url} (attempt {retries}/{self.max_retry_times}): {reason}")

            # Exponential backoff
            delay = min(300, (2 ** retries) + random.uniform(0, 1))

            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.priority = request.priority + self.priority_adjust
            retryreq.dont_filter = True

            # Add delay meta for scheduler
            retryreq.meta['download_delay'] = delay

            return retryreq
        else:
            self.logger.error(f"Gave up retrying {request.url} (tried {retries} times): {reason}")
            return None