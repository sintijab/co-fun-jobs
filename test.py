import scrapy
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

class ComputerFuturesSpider(scrapy.Spider):
    name = "computerfutures"
    start_urls = ["https://dummyjson.com/docs/products/"]

    def __init__(self, *args, **kwargs):
        super(ComputerFuturesSpider, self).__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.headless = True  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def parse(self, response):
        self.driver.get(response.url)
        time.sleep(5)  # Wait for the page to load

        try:
            page_title = self.driver.find_element(By.CLASS_NAME, "docs-title").text.strip()
        except Exception:
            page_title = "N/A"
        
        yield {"page_title": page_title}

    def closed(self, reason):
        self.driver.quit()
