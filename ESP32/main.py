#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import epd7in3f
import random
import logging
import urllib
import json

import requests
from io import BytesIO
from PIL import Image

import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

import requests
from io import BytesIO
from urllib.request import urlopen
from PIL import Image

def get_flag(flag_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    response = requests.get(flag_url, headers=headers)

    if response.status_code == 200:
        flag_image = Image.open(BytesIO(response.content))
        return flag_image
    else:
        raise Exception(f"Error {response.status_code}: {response.reason}")
    

def display_flag(epd, country_name=None):
    logging.info("Displaying flag...")

    # Get the list of countries
    response = requests.get("https://restcountries.com/v3.1/all")
    data = response.json()

    country = None

    if country_name:
        for item in data:
            if item['name']['common'].lower() == country_name.lower():
                country = item
                break

    # If country not found or not specified, select a random country
    if not country:
        random_index = random.randint(0, len(data) - 1)
        country = data[random_index]

    # Get the flag URL
    flag_url = country["flags"]["png"]

    # Download and open the flag image
    flag_image = get_flag(flag_url)

    # Resize the flag image to the display size
    resized_flag_image = flag_image.resize((epd.width, epd.height), Image.ANTIALIAS)

    # Display the flag image
    epd.display(epd.getbuffer(resized_flag_image))

    logging.info(f"Displayed flag for {country['name']['common']}")



try:
    logging.info("epd7in3f Demo")

    epd = epd7in3f.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    # Add other drawing functions here...

    # Display flag
    display_flag(epd, "portugal")
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in3f.epdconfig.module_exit()
    exit()
