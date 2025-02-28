from scrapers.base_scraper import BaseScraper
from utils.prompt_ai import make_prompt
import json
import re
import requests
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
        detailed_page_prefix = 'https://www.sreality.cz'
        

        real_urls = [detailed_page_prefix + href for href in hrefs]

        return real_urls

    def get_next_page(self):
        """Finds and returns the next page URL if available."""
        self.page_num += 1
        next_page = self.base_url + f"?strana={self.page_num}"

        if not self.page_num > self.last_page_num:
            return next_page
        else:
            return None

    def get_property(self, soup) -> object:
        
        """Returns proccessed property object."""
        
        return 
        
        
    def get_listing(self, soup) -> object:
        """Returns proccessed listing object."""
        print(f"Fetching listing details for {url}... (placeholder)")

        return {}  # Return an empty dictionary instead of None

    def get_last_page(self):
        return 10


url = 'https://www.sreality.cz/hledani/pronajem/byty'
s = SrealityScraper(url,'sreality')
# asyncio.run(s.scrape_listings())
new_url ='https://www.sreality.cz/api/cs/v2/estates/149500492'
soup = s.fetch_page(new_url)
print(soup)



def extract_by_ai(data):
    property_schema = {
  "property_type": "string (e.g., Apartment, House)",
  "size": "float (in square meters)",
  "rooms": "integer",
  "gps_lat": "float (latitude)",
  "gps_lon": "float (longitude)",
  "construction_year": "integer",
  "last_reconstruction_year": "integer",
  "energy_rating": "string (e.g., A, B, C)",
  "has_balcony": "boolean",
  "has_parking": "boolean",
  "condition": "string (e.g., Excellent, Good, Renovated)",
  "floor": "integer",
  "building_floors": "integer",
  "elevator": "boolean",
  "garden_size_m2": "float",
  "garage_count": "integer",
  "created_at": "string (ISO 8601 timestamp)",
  "updated_at": "string (ISO 8601 timestamp)"
}

    listing_schema = {
  "external_id": "string",
  "images_urls": "list of strings (URLs)",
  "price": "float",
  "rent": "boolean",
  "contact": "string (email or phone)",
  "description": "string",
  "hash": "string",
  "date_created": "string (ISO 8601 timestamp)",
  "date_removed": "string (ISO 8601 timestamp or null)",
  "is_active": "boolean",
  "rent_price": "float or null",
  "electricity_utilities": "float",
  "provision_rk": "float",
  "downpayment_1x": "float",
  "downpayment_2x": "float",
  "created_at": "string (ISO 8601 timestamp)",
  "updated_at": "string (ISO 8601 timestamp)"
}

    purpose = f"""
You are a real estate data parser. Your task is to convert unstructured input data into two structured JSON objects: `property` and `listing`.

Rules:
1. Follow the exact structure and key names from the schemas below.
2. Use the correct data types (e.g., boolean, float, string).
3. Return ONLY the JSON objects. No explanations, notes, or extra text.
4. For missing data, use `null` (not "Null" or empty strings).
5. Ignore fields not mentioned in the schemas.

Schemas:
- Property Schema: {property_schema}
- Listing Schema: {listing_schema}
"""

    prompt = f"""Analyze this JSON structure and extract values based on these patterns:
    
    1. Property Type: Look for 'categoryMainCb.name' or text containing 'byt'/'dům'
    2. Size: Find numbers with 'm²' or 'size'/'velikost' in key
    3. Price: Search for 'priceCzk' or numbers with 'Kč'/'CZK'
    4. Coordinates: Look for 'latitude'/'longitude' or 'gps' in keys
    5. Dates: Find ISO dates or Czech date formats (dd. mm. yyyy)
    6. Rooms: Extract from '2+kk' patterns or 'pokojů' in text
    
    Return only JSON matching these schemas with null for missing values."""
    return make_prompt(prompt=prompt,purpose=purpose)



# res = extract_by_ai(text_to_analyze)
# print(res)