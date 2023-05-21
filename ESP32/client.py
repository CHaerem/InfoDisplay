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

def get_country_info(server_url):
    response = requests.get(f"{server_url}/info")
    data = response.json()

    return data

def display_flag(epd, server_url, country_name=None):
    logging.info("Displaying flag...")

    # Get the flag from server
    if country_name:
        flag_url = f"{server_url}/flag/{country_name}"
    else:
        flag_url = f"{server_url}/flag"

    # Download and open the flag image
    flag_image = get_flag(flag_url)

    # Get the country info from the server
    country = get_country_info(server_url)

    # Rotate the flag image 180 degrees
    rotated_flag_image = flag_image.rotate(180)

    # Resize the flag image to the display size
    resized_flag_image = rotated_flag_image.resize((epd.width, epd.height), Image.ANTIALIAS)

    # Display the flag image
    epd.display(epd.getbuffer(resized_flag_image))

    logging.info(f"Displayed flag for {country['name']['common']}")

def main():
    logging.info("epd7in3f Demo")

    epd = epd7in3f.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    # Add other drawing functions here...

    # Get command line arguments
    args = sys.argv
    country_name = None

    # If a country name argument is provided, use it
    if len(args) > 1:
        country_name = args[1]

    server_url = "http://serverpi.local:5000"

    # Display flag
    display_flag(epd, server_url, country_name)

    logging.info("Goto Sleep...")
    epd.sleep()

if __name__ == '__main__':
    main()
