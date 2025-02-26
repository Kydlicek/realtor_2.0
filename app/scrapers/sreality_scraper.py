from scrapers.base_scraper import BaseScraper
import asyncio


class SrealityScraper(BaseScraper):
    """Scraper for Sreality.cz listings."""

    def __init__(self, base_url: str, source: str):
        super().__init__(base_url, source)
        self.page_num = 0
        self.last_page_num = self.get_last_page()

    def extract_listings(self, soup):
        ul_element = soup.find("ul")
        a_els = ul_element.find_all("a")
        hrefs = [a["href"] for a in a_els if a.has_attr("href")]

        real_urls = [self.base_url + href for href in hrefs]

        return real_urls

    def get_next_page(self):
        """Finds and returns the next page URL if available."""
        self.page_num += 1
        next_page = self.base_url + f"?strana={self.page_num}"

        if not self.page_num > self.last_page_num:
            return next_page
        else:
            return None

    def get_property(self, url) -> object:
        """Returns proccessed property object."""
        print(f"Fetching property details for {url}... (placeholder)")

        return {}  # Return an empty dictionary instead of None

    def get_listing(self, url) -> object:
        """Returns proccessed listing object."""
        print(f"Fetching listing details for {url}... (placeholder)")

        return {}  # Return an empty dictionary instead of None

    def get_last_page(self):
        return 10


# development purpose
s = SrealityScraper(
    base_url="https://www.sreality.cz/hledani/pronajem/byty", source="sreality"
)
s.get_next_page()
asyncio.run(s.scrape_listings())
