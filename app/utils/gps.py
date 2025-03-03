# This script help to converts GPS to address and vice versa

import requests
import os

def get_address(lat, lon):
    url = f'https://geocode.maps.co/reverse?lat={lat}&lon={lon}&api_key=67c588c70a112779804541kjs92d24d'
    res = requests.get(url=url)
    return res.json()


def get_gps(address):
    url = f'https://geocode.maps.co/search?q={address}&api_key=67c588c70a112779804541kjs92d24d'
    res = requests.get(url=url)
    return res.json()