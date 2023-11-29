ITEM_PIPELINES = {
            '__main__.CustomPipeline': 200,
            '__main__.HtmlPipeline': 500,
#            '__main__.CSVPipeline': 800
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

CONCURRENT_REQUESTS = 16 
DOWNLOAD_DELAY = 0
COOKIES_ENABLED = False
PLAYWRIGHT_BROWSER_TYPE = 'chromium'

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

HTTPCACHE_ENABLED = False

LOG_FILE = 'app.log'
LOG_FILE_APPEND = False
LOG_LEVEL = 'INFO'
#LOG_STDOUT = True