from scrapers.base_scraper import BaseScraper

class BezrealitkyScraper(BaseScraper):
    """Scraper for Bezrealitky.cz listings."""

    def extract_listings(self, soup):
        """Extracts listing URLs from the page."""
        return [a["href"] for a in soup.select(".property a.title")]

    def get_next_page(self, soup):
        """Finds and returns the next page URL if available."""
        next_page = soup.select_one("a.next-page")
        return next_page["href"] if next_page else None
    

    def get_property(url) -> object:
        """Returns proccessed property object."""
        pass

    def get_listing(url) -> object:
        """Returns proccessed listing object."""
        pass