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
            
    def get_listing_property(self,url):
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
        m2 = self.find_in_items(res, "Užitná ploch") if self.find_in_items(res, "Užitná ploch") else None
        parking= self.find_in_items(res, 'Parkování')
        if parking == True:
            parking = 1
        cellar_m2= self.find_in_items(res,'Sklep') if self.find_in_items(res, "Užitná ploch") else 0
        elevator = self.find_in_items(res, 'Výtah')
        condition = self.find_in_items(res, 'Stav objektu')
        furnished = self.find_in_items(res, "Vybavení") if self.find_in_items(res, "Vybavení") else None
        garden_m2 = self.find_in_items(res,'Plocha zahrady')if self.find_in_items(res, "Plocha zahrady") else None
        
        energy_class = self.find_in_items(res, "Energetická náročnost budovy")[6:7] if len(self.find_in_items(res, "Energetická náročnost budovy")) >= 7 else None
        images = [img["_links"]["self"]["href"] for img in res.get("_embedded", {}).get("images", [])]
        prompt = f'here is describtion of property return me object like property_type: xxx, rooms: xxx , transaction xxx {description}'
        purpose = 'u are realestate agent and from describtion of property u have to know what property type it is, what how many rooms are there 2+KK, 1+kk, 3+kk etc.., also what type of transaction it is order rent or sell'
        make_prompt(prompt=prompt,purpose=purpose)
        
        prop = {
            'property_type': 'x',
            'size_m2': m2,
            'rooms': 'x',
            'gps_lat':lat,
            'gps_lon': lon,
            'energy_rating':energy_class,
            'has_balcony':balcony,
            'parking':parking,
            'cellar_m2':cellar_m2,
            'condition':condition,
            'floor': floor,
            'elevator': elevator,
            'garden_size_m2': garden_m2,
            'furnished': furnished,
        }
        listing = {
            'source': 'x',
            'url':'x',
            'images': images,
            'price':price,
            'transaction':'x',
            'contact': contact,
            'description': description,
            'is_active': 'x',
            'rent_price': price,

            

        }
        



url = 'https://www.sreality.cz/hledani/pronajem/byty'
s = SrealityScraper(url,'sreality')
# asyncio.run(s.scrape_listings())
test= 'https://www.sreality.cz/detail/pronajem/byt/2+kk/praha-nove-mesto-stepanska/3660591692'
s.get_listing_property(test)
