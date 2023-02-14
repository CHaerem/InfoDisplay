from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import requests
import geopandas as gpd
from gadm import GADMDownloader

downloader = GADMDownloader(version="4.0")

url = "https://restcountries.com/v3.1/all"
response = requests.get(url)
data = response.json()

# create the map object
m = Basemap(projection='mill', lat_0=50, lon_0=-100, resolution='l', area_thresh=10000)

# print("Reading shapefile...")
# test = m.readshapefile(f'/Users/cher/Documents/Globe/shapefiles/gadm36_shp/gadm36', 'countries')
# print("Shapefile read.")
for country in data:
    country_found = False
    for info, shape in zip(m.countries_info, m.countries):
        if info['GID_0'].lower() == country["cca3"].lower():
            country_found = True
            break
    if not country_found:
        print(str(info["NAME_0"].lower()) + "        -       " + str(info["GID_0"].lower()))

