from scrapers.sreality_scraper import SrealityScraper
import pytest

base_url = "https://www.sreality.cz/hledani/prodej/byty"


@pytest.fixture
def scraper():
    return SrealityScraper(base_url, "sreality")


def test_class(scraper):
    assert isinstance(scraper, SrealityScraper)
    assert scraper.base_url == base_url
    assert scraper.source == "sreality"
    assert scraper.page_num == 1
