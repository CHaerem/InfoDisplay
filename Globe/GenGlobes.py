from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime
import matplotlib.patches as mpatches
import math

from shapely.geometry import Point, Polygon
import pyproj

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from pathlib import Path
  


# Function to initialize the globe
def init_globe():
    m = Basemap(projection='ortho', lat_0=0, lon_0=0, resolution='l')

    

    print("Reading shapefile...")
    m.readshapefile(f'/Users/cher/Documents/Globe/shapefiles/World_Countries/World_Countries', 'countries', drawbounds=True, linewidth=1, color='black')
    print("Shapefile read.")

    return m

def init_globe_2(plt, m):
    # Define color maps for water and land
    ocean_map = (plt.get_cmap('ocean'))(210)
    cmap = plt.get_cmap('gist_earth')

    # Coastlines, map boundary, fill continents/water, fill ocean, draw countries
    m.drawcoastlines()
    m.drawmapboundary(fill_color=ocean_map)
    m.fillcontinents(color=cmap(200), lake_color=ocean_map)
    #m.nightshade(datetime.now(), delta=0.2)
    m.drawcountries()

    # Latitude/longitude line vectors
    m.drawmeridians(range(0, 360, 20))
    m.drawparallels(range(-90, 100, 10))
    
# Function to get country info from restcountries API
def get_country(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url).json()
    if response:
        return response[0]
    else:
        return None

# Function to get all countries from RESTcountries API
def get_all_countries():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url).json()
    return response

# Function to find the best matching country name
def find_best_match(country_name, countries_dict):
    best_match = ""
    max_ratio = 0

    for country in countries_dict:
        ratio = fuzz.ratio(country_name.lower(), country.lower())
        if ratio > max_ratio:
            max_ratio = ratio
            best_match = country

    return best_match, max_ratio

def find_best_match_2(country_name, countries_dict):
    best_match = process.extractOne(country_name, countries_dict.keys(), scorer=fuzz.token_set_ratio)
    return best_match[0]

# Function to add shapes to the map
def add_shapes(m, country, ax):
    # Dictionary to store country names and corresponding shapes and info
    countries_dict = {}

    for info, shape in zip(m.countries_info, m.countries):
        country_name = info['COUNTRY']

        if country_name not in countries_dict:
            countries_dict[country_name] = {
                "info": info,
                "shapes": [shape]
            }
        else:
            countries_dict[country_name]["shapes"].append(shape)

    best_match = find_best_match_2(country['name']['common'], countries_dict)
    print(f"Best match for {country['name']['common']}: {best_match}")
    with open(f"globes/{country['name']['common']}/info.tx", 'w') as f:
        f.write(f"Best match for {country['name']['common']}: {best_match}")

    # Add all the shapes for the best matching country
    for shape in countries_dict[best_match]["shapes"]:
        shape = np.array(shape)
        ax.add_patch(mpatches.Polygon(shape, facecolor='red', edgecolor='k', linewidth=1., zorder=2, closed=True))

# Function to plot the globe
def plot_globe(country, m):
    # Create figure
    fig = plt.figure(figsize=(9,9))
    ax = fig.add_subplot(111)
    init_globe_2(plt, m)

    # Set perspective angle
    lat_viewing_angle = country['latlng'][0]
    lon_viewing_angle = country['latlng'][1]

    # Call the basemap and use orthographic projection at viewing angle
    #m = Basemap(projection='ortho', lat_0=lat_viewing_angle, lon_0=lon_viewing_angle) 
    m.lat_0 = lat_viewing_angle
    m.lon_0 = lon_viewing_angle

    # Add marker if country is small
    if country['area'] < 100000:
        x, y = m(country['latlng'][1], country['latlng'][0])
        m.plot(x, y, 'ro', markersize=5)
    
    Path(f"/Users/cher/Documents/Globe/globes/{country_name}").mkdir(parents=True, exist_ok=True)  

    # Add shapes for the given country
    add_shapes(m, country, ax)
        
    # Save figure
    filename_pdf = f"globes/{country_name}/{country_name}.pdf"
    filename_svg = f"globes/{country_name}/{country_name}.svg"
    plt.savefig(filename_pdf, format='pdf')
    plt.savefig(filename_svg, format='svg')


if __name__ == '__main__':
    #country_name = input("Enter the name of a country: ")

    # Initialize the globe
    m = init_globe()

    countries = get_all_countries()
    for country in countries:
        country_name = country['name']['common']
        print(f"Generating globe for {country_name}...")
        plot_globe(country, m)
        print(f"Globe for {country_name} generated.")
        print()
        print()
        
    