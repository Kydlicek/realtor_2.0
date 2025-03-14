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

    
    def get_last_page(self):

        return 10
    

    def find_in_items(self, data, name):
        items = data["items"]
        for dic in items:
            if dic["name"] == name:
                return dic["value"]
            

    def get_listing_data(self,url):
        # input_url= https://www.sreality.cz/detail/pronajem/byt/2+kk/praha-nove-mesto-stepanska/3660591692
        h_id = url.split('/')[-1]
        api_url = f'https://www.sreality.cz/api/cs/v2/estates/{h_id}'
        res = self.fetch_json(api_url)
        description = res['text']['value']
        contact = res["_embedded"]["seller"]
        lat= res.get("map", {}).get("lat", None)
        lon= res.get("map", {}).get("lon", None)
        price = res["price_czk"]["value_raw"]
        rec_data = res.get("recommendations_data", {})
        # Extract values for each key in additional_info
        floor = self.find_in_items(res, "Podlaží")[0] if self.find_in_items(res, "Podlaží") else None
        balcony = rec_data.get("balcony", None)
        m2 = self.find_in_items(res, "Užitná ploch") if self.find_in_items(res, "Užitná ploch") else 0
        parking= self.find_in_items(res, 'Parkování')
        if parking == True:
            parking = 1
        cellar_m2= self.find_in_items(res,'Sklep') if self.find_in_items(res, "Užitná ploch") else 0
        elevator = self.find_in_items(res, 'Výtah')
        condition = self.find_in_items(res, 'Stav objektu')
        furnished = self.find_in_items(res, "Vybavení") if self.find_in_items(res, "Vybavení") else None
        garden_m2 = self.find_in_items(res,'Plocha zahrady')if self.find_in_items(res, "Plocha zahrady") else 0
        
        energy_class = self.find_in_items(res, "Energetická náročnost budovy")[6:7] if len(self.find_in_items(res, "Energetická náročnost budovy")) >= 7 else None
        images = [img["_links"]["self"]["href"] for img in res.get("_embedded", {}).get("images", [])]
        
        property_data = {
    "property_type": self.get_transaction_type_and_prop_type()[1],           # e.g., "apartment", "house"
    "size_m2": m2,                # e.g., 85.5
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
    "garden_size_m2": garden_m2,
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
    "energy_rating": energy_class              # e.g., "B" (from ENUM)
}
        
        

        


url = 'https://www.sreality.cz/hledani/pronajem/byty'
s = SrealityScraper(url,'sreality')
# asyncio.run(s.scrape_listings())
test= 'https://www.sreality.cz/detail/pronajem/byt/2+kk/praha-nove-mesto-stepanska/3660591692'
s.get_listing_data(test)
