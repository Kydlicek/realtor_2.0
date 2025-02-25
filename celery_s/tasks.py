from celery_s.celery_app import celery_app
from celery.schedules import crontab
from scraper_config import SCRAPER_SOURCES
from scrapers import idnes_scraper,sreality_scraper

@celery_app.task
def start_all_scrapers():
    """Spustí scraping pro všechny weby a kategorie."""
    for site, urls in SCRAPER_SOURCES.items():
        for category, path in urls.items():
            if category == "base_url":  
                continue  # Přeskočíme base_url, není potřeba scrapovat
            full_url = urls["base_url"] + path
            print(f"🚀 Spouštím scraper pro {site} - {full_url}")
            scrape_new_listings.delay(full_url, site)

@celery_app.task
def scrape_new_listings(full_url: str, source: str):
    """Task for scraping new listings from different sources."""
    print(f"🔍 Starting scraper for {source} at {full_url}")

    if source == "idnes":
        idnes_scraper(full_url).scrape_listings()
    elif source == "sreality":
        sreality_scraper(full_url).scrape_listings()


@celery_app.task
def scrape_listing_details(url: str, source: str) -> str:
    """Task pro scraping detailní stránky inzerátu."""
    if source == "idnes":
        idnes_scraper().process_detailed_listing(url)
    elif source == "sreality":
        sreality_scraper().process_detailed_listing(url)

# Přidání periodického tasku pro Celery Beat
celery_app.conf.beat_schedule = {
    "start-all-scrapers-every-15min": {
        "task": "tasks.start_all_scrapers",
        "schedule": crontab(minute="*/15"),  # Každých 15 minut
    },
}
