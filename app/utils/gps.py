# This script help to converts GPS to address and vice versa

import requests
import json
import time


api_interval = 1
def get_address(lat, lon):
    time.sleep(api_interval)
    url = f'https://geocode.maps.co/reverse?lat={lat}&lon={lon}&api_key=67c588c70a112779804541kjs92d24d'
    response = requests.get(url)
            
    # Handle rate limiting (429) and other errors
    if response.status_code == 429:
        print("Rate limited - consider increasing api_interval")
        return None
    if response.status_code != 200:
        return None
        
    data = response.json()
    address = data.get('address', {})
    
    return {
        'country': address.get('country', 'N/A'),
        'country_code': str(address.get('country_code', 'N/A')).upper(),
        'city': address.get('city') or address.get('town', 'N/A'),
        'postcode': address.get('postcode', 'N/A'),
        'street': address.get('road', 'N/A'),
        'house_num': address.get('house_number', 'N/A'),
        'city_district': address.get('city_district', 'N/A'),
        'full_address': data.get('display_name', 'N/A'),
        'lat': lat,
        'lon': lon
    }




 
    


