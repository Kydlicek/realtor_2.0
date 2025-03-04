from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from utils.db_functions import check_link_exists, save_property, save_listing
from utils.gps import get_address, get_gps
import asyncio
import pytest


class BaseScraper(ABC):
    def __init__(self, base_url: str, source: str,country: str,currency:str,search_key:str):
        """
        Initializes the scraper with the base URL and source name.

        :param base_url: The starting URL for scraping.
        :param source: The name of the website being scraped.
        :param country: Country of Listing
        :param currency: currency of Listing
        :serach_key: ex. rent_flat - param to know transaction_type and property_type
        """
        self.base_url = base_url
        self.source = source
        self.currency = currency
        self.country = country
        self.search_key = search_key
    def get_transaction_type_and_prop_type(self):
        transaction_type, property_type = self.search_key.split('_', 1)
        return [transaction_type,property_type]
    

    def check_property_exists(self, property) -> bool:
        return False

    def check_listings_exists(self, listing) -> bool:
        return False

    def fetch_page(self, url: str):
        """Fetches a webpage and returns BeautifulSoup object."""
        print(f"📥 Fetching {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url} (status {response.status_code})")
            return None
        return BeautifulSoup(response.text, "html.parser")

    async def scrape_listings(self):
        """Scrapes listings from multiple pages."""
        tasks = []
        url = self.base_url

        while url:
            soup = self.fetch_page(url)
            if not soup:
                break
            listings_urls = self.extract_listings(soup)

            task = asyncio.create_task(self.process_listings(listings_urls))
            tasks.append(task)

            url = self.get_next_page()

        await asyncio.gather(*tasks)

    async def process_listings(self, listings_urls):
        """Processes extracted listings."""
        for url in listings_urls:
            if not check_link_exists(url):
                await asyncio.to_thread(self.process_detailed_listing, url)

    def process_detailed_listing(self, url):
        soup = self.fetch_page(url)
        prop = self.get_property(soup)
        if not self.check_property_exists(prop):
            save_property(prop)

        listing = self.get_listing(soup)
        if not self.check_listings_exists(listing):
            save_listing(self.get_listing(url))

        return True

    @abstractmethod
    def get_property(self, url) -> object:
        """Returns proccessed property object."""
        pass

    @abstractmethod
    def get_listing(self, url) -> object:
        """Returns proccessed listing object."""
        pass

    @abstractmethod
    def extract_listings(self, soup) -> list:
        """Extracts listing URLs from the page. and returns a list of URLs."""
        pass

    @abstractmethod
    def get_next_page(self) -> str:
        """returns next page url"""
        pass

    @abstractmethod
    def get_last_page(self, soup) -> int:
        """returns max pages"""
        pass
    def fetch_prop(self):
        property_data = {
    "property_type": self.get_transaction_type_and_prop_type()[1],           # e.g., "apartment", "house"
    "size_m2": 0.0,                # e.g., 85.5
    "rooms": 0,                     # e.g., 3
    "has_separate_kitchen": False,  # True/False
    "gps_lat": 0.0,                 # e.g., 48.8566
    "gps_lon": 0.0,                 # e.g., 2.3522
    "country": "",                   # e.g., "Germany"
    "city": "",                      # e.g., "Berlin"
    "city_district": "",             # e.g., "Mitte"
    "address": "",                   # e.g., "123 Main St"
    "year_built": None,              # e.g., 1990 (optional)
    "last_reconstruction_year": None, # e.g., 2010 (optional)
    "condition": "",                 # e.g., "good" (from ENUM)
    "has_balcony": False,
    "balcony_size_m2": 0.0,
    "has_terrace": False,
    "terrace_size_m2": 0,
    "has_garden": False,
    "garden_size_m2": 0,
    "has_parking": False,
    "parking": 0,
    "has_garage": False,
    "garage": 0,
    "has_cellar": False,
    "cellar_size_m2": 0,
    "is_furnished": False,
    "has_lift": False,
    "building_floors": None,         # e.g., 5 (optional)
    "flat_floor": None,              # e.g., 2 (optional)
    "energy_rating": ""              # e.g., "B" (from ENUM)
}
        return property_data
    def fetch_listing(self):
        listing_data = {
    "source": self.source,                    # e.g., "portal123.cz"
    "listing_url": "",              # e.g., "https://example.com/listings/123" (required)
    "api_url": "",                  # e.g., "https://api.example.com/listings/123" (optional)
    "description": "",              # Long text description (optional)
    'transaction_type': self.get_transaction_type_and_prop_type()[0],
    "price": 0.0,                   # Sale price (required)
    "rent_price": None,             # Rent price (optional, e.g., 1200.0)
    "building_fees": 0.0,           # Monthly fees (default 0)
    "electricity_utilities": 0.0,   # Utilities cost (default 0)
    "provision_rk": 0.0,            # Agency commission (default 0)
    "currency": self.currency,              # Currency (default "CZK", from ENUM)
    "contact": None,                # JSON contact info (e.g., {"name": "John", "phone": "..."})
    "listing_status": "active"      # Status (default "active", from ENUM)
}
        return listing_data