from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from utils.database import check_link_exists, save_new_listing,save_new_property



class BaseScraper(ABC):
    def __init__(self, base_url: str, source: str):
        """
        Initializes the scraper with the base URL and source name.

        :param base_url: The starting URL for scraping.
        :param source: The name of the website being scraped.
        """
        self.base_url = base_url
        self.source = source

    def check_property_exists(self,property)-> bool:
        pass
    def check_listings_exists(self,listing)-> bool:
        pass
    def check_link_exists(self,url:str) -> bool:
        check_link_exists(url)

    
    def save_new_listing(self,listing:object):
        save_new_listing(listing)
    
    def save_new_property(self,property:object):
        save_new_property(property)


    def fetch_page(self, url: str):
        """Fetches a webpage and returns BeautifulSoup object."""
        print(f"📥 Fetching {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url} (status {response.status_code})")
            return None
        return BeautifulSoup(response.text, "html.parser")
    

    def scrape_listings(self, start_url: str):
        """Scrapes listings from multiple pages."""
        url = start_url
        while url:
            soup = self.fetch_page(url)
            if not soup:
                break
            listings_urls = self.extract_listings(soup)
            self.process_listings(listings_urls)
            url = self.get_next_page(soup)

    def process_listings(self, listings_urls):
        """Processes extracted listings."""
        from celery_s.tasks import scrape_listing_details
        for url in listings_urls:
            if not self.check_link_exists(url):
                scrape_listing_details(url,self.source)

    
    
    
    
    def process_detailed_listing(self,url):
        prop = self.get_property(url)
        if not self.check_property_exists(prop):
            self. save_new_property(prop)
        
        listing = self.get_listing(url)
        if not self.check_listings_exists(listing):
            save_new_listing(self.get_listing(url))

   

    @abstractmethod
    def get_property(self,url) -> object:
        """Returns proccessed property object."""
        pass
    @abstractmethod
    def get_listing(self,url) -> object:
        """Returns proccessed listing object."""
        pass

    @abstractmethod
    def extract_listings(self, soup) -> list:
        """Extracts listing URLs from the page."""
        pass

    @abstractmethod
    def get_next_page(self, soup):
        """Finds and returns the next page URL."""
        pass
