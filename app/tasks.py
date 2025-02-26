from celery_app import app
from scraper_config import SCRAPER_SOURCES
from scrapers import idnes_scraper, sreality_scraper


@app.task
def start_all_scrapers():
    """Spustí scraping pro všechny weby a kategorie."""
    for site, urls in SCRAPER_SOURCES.items():
        for category, path in urls.items():
            if category == "base_url":
                continue  # Přeskočíme base_url, není potřeba scrapovat
            full_url = urls["base_url"] + path
            print(f"🚀 Spouštím scraper pro {site} - {full_url}")
            scrape_new_listings.delay(full_url, site)


@app.task
def scrape_new_listings(full_url: str, source: str):
    """Task for scraping new listings from different sources."""
    print(f"🔍 Starting scraper for {source} at {full_url}")

    if source == "idnes":
        idnes_scraper(full_url).scrape_listings()
    elif source == "sreality":
        sreality_scraper(full_url).scrape_listings()
