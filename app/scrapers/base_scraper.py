from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from utils.database import check_link_exists, save_property, save_listing
import asyncio


class BaseScraper(ABC):
    def __init__(self, base_url: str, source: str):
        """
        Initializes the scraper with the base URL and source name.

        :param base_url: The starting URL for scraping.
        :param source: The name of the website being scraped.
        """
        self.base_url = base_url
        self.source = source

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
        prop = self.get_property(url)
        if not self.check_property_exists(prop):
            save_property(prop)

        listing = self.get_listing(url)
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
