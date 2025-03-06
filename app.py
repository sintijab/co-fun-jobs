from flask import Flask, jsonify, request
import requests
import random
import urllib.parse
from parsel import Selector

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.94 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.94 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.94 Safari/537.36"
]

COUNTRY_PATHS = {
    "united kingdom": "/en-gb/find-a-job/all-jobs/",
    "netherlands": "/nl-nl/werk-zoeken/alle-banen/",
    "germany": "/de-de/stellensuche/alle-jobs/",
    "france": "/fr-fr/trouver-un-job/tous-les-emplois/",
    "belgium": "/en-be/find-a-job/all-jobs/",
    "japan": "/ja-jp/job-search/すべてのジョブ/",
    "switzerland": "/de-de/stellensuche/?searchRadius=500km&country=Schweiz",
    "austria": "/de-de/stellensuche/?searchRadius=500km&country=Österreich",
    "czech republic": "/de-de/stellensuche/?searchRadius=500km&country=Tschechien"
}

BASE_URL = "https://www.computerfutures.com"

def get_random_headers():
    """ Generate randomized headers for each request """
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

def fetch_page(url):
    """ Fetches the page content of the given URL """
    response = requests.get(url, headers=get_random_headers())
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}, Status Code: {response.status_code}")
        return None

def extract_job_links(html):
    """ Extracts job listing links from the search page """
    sel = Selector(text=html)
    all_links = sel.css("a[href*='/job/']::attr(href)").getall()
    return all_links

def extract_job_apply_link(html):
    """ Extracts job listing links from the search page """
    sel = Selector(text=html)
    link = sel.css("a[href*='/apply']::attr(href)").get()
    print(link)
    return link

def extract_job_details(html):
    """ Extracts job details from a job page """
    sel = Selector(text=html)
    section_texts = sel.css(".job__container *::text, .job-detail *::text").getall()
    section_texts = [text.strip() for text in section_texts if text.strip()]
    return "\n".join(section_texts)

def extract_job_title(html):
    """ Extracts job title from a job page """
    sel = Selector(text=html)
    section_texts = sel.css(".banner__title *::text, .job-detail *::text").getall()
    section_texts = [text.strip() for text in section_texts if text.strip()]
    return "\n".join(section_texts)

def chunk_list(lst, chunk_size):
    """ Splits a list into smaller chunks """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

@app.route('/health')
def hello_world():
    return 'OK'

@app.route('/scrape-jobs', methods=['GET'])
def scrape_jobs():
    country = request.args.get("country", "").strip()

    # Normalize country names
    country = urllib.parse.unquote(country).lower()

    # Validate country and set job listing URL
    if country not in COUNTRY_PATHS:
        return jsonify({"error": "Invalid country. Supported countries: " + ", ".join(COUNTRY_PATHS.keys())}), 400

    job_listings_url = BASE_URL + COUNTRY_PATHS[country]

    # Fetch job listing page
    html = fetch_page(job_listings_url)
    if not html:
        return jsonify({"error": "Failed to fetch job listing page"}), 500

    # Extract job links
    job_links = extract_job_links(html)

    if not job_links:
        return jsonify({"error": "No job links found"}), 404

    # Check if country uses "searchRadius" (skip job detail extraction)
    skip_details = "searchRadius" in COUNTRY_PATHS[country]

    # Limit chunk size if too many jobs
    chunks = chunk_list(job_links, 100) if len(job_links) > 100 else [job_links]

    all_jobs = []
    for chunk in chunks:
        for link in chunk:
            full_url = f"{BASE_URL}{link}" if link.startswith("/") else link
            if skip_details:
                all_jobs.append({"url": full_url, "content": None})
            else:
                job_html = fetch_page(full_url)
                if job_html:
                    job_content = extract_job_details(job_html)
                    job_title = extract_job_title(job_html)
                    job_apply_button = extract_job_apply_link(job_html)
                    all_jobs.append({"url": full_url, "content": job_content, "title": job_title, "apply": job_apply_button })

    return jsonify({
        "job_listings_url": job_listings_url,
        "jobs": all_jobs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
