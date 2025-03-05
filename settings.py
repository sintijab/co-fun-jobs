DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy_proxies.RandomProxy': 100,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

ROTATING_PROXY_LIST = [
    "http://67.43.228.252:29825",
    "http://188.166.197.129:3128",
    "http://13.36.104.85:80"
]

RETRY_TIMES = 5  # Number of times to retry failed requests
RETRY_HTTP_CODES = [403, 429, 500, 502, 503, 504]  # Common error codes to retry
HTTPERROR_ALLOWED_CODES = [403, 429]  # Allow Scrapy to process 403 and 429 errors
