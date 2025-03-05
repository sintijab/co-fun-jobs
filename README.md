
# Web scraper and lookup for career discovery bot

## Install virtualenv and deps
```python
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

## Run the application
```python
    python app.py
```

## Troubleshooting
First, print the extracted links in parse():

```python
 def parse(self, response):
    job_links = response.css("a.link--cover::attr(href)").getall()

    for link in job_links:
        full_url = response.urljoin(link)
        print(f"Found job link: {full_url}")  # Debugging output
        yield scrapy.Request(url=full_url, callback=self.parse_job_details)
```
Run Scrapy:

```python
 scrapy runspider scraper/job_spider.py -o scraped_jobs.json
```
