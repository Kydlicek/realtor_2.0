from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from utils.db_functions import check_link_exists, save_property, save_listing
from utils.gps import get_address
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

    def fetch_soup(self, url: str):
        """Fetches a webpage and returns BeautifulSoup object."""
        print(f"📥 Fetching {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url} (status {response.status_code})")
            return None
        return BeautifulSoup(response.text, "html.parser")
    
    def fetch_json(self, url:str):
        """Fetches a webpage and returns BeautifulSoup object."""
        print(f"📥 Fetching {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url} (status {response.status_code})")
            return None
        return response.json()
    

    async def scrape_listings(self):
        """Scrapes listings from multiple pages."""
        tasks = []
        url = self.base_url

        while url:
            soup = self.fetch_soup(url)
            if not soup:
                break
            listings_urls = self.extract_listings(soup)

            task = asyncio.create_task(self.process_listings(listings_urls))
            tasks.append(task)

            url = self.get_next_page()

    def process_listings(self, listings_urls):
        """Processes extracted listings and query it for later work."""
        for url in listings_urls:
            if not check_link_exists(url):
                self.process_detailed_listing(url)

    def process_detailed_listing(self, listing_url):
        """Processes data from listing input listing URL."""

       
        scraped_data = self.get_listing_data(listing_url)
        address_data = get_address(lat='lat',lon='lon')


        prop_data = ''
        listing_data = ''


        base_prop_data = {
            "property_type": self.get_transaction_type_and_prop_type()[1],
            'gps_lat': address_data.get('lat'),
            'gps_lon': address_data.get('lon'),
            'country': address_data.get('country'),
            'country_code': address_data.get('country_code'),
            'city' :address_data.get('city'),
            'city_district': address_data.get('city_district'),
            'street':address_data.get('street'),
            'full_address': address_data.get('full_address'),
        }
        base_listing_data = {
            'transaction_type': self.get_transaction_type_and_prop_type()[0],
            "currency": self.currency,
            'source' : self.source,
            'listing_url': listing_url
        }


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

       