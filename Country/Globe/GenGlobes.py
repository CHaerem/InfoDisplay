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
import time


# Function to initialize the globe
def init_globe(country):
    # Create figure
    fig = plt.figure(figsize=(9,9))
    ax = fig.add_subplot(111)

    # Set perspective angle
    lat_viewing_angle = country['latlng'][0]
    lon_viewing_angle = country['latlng'][1]

    # Call the basemap and use orthographic projection at viewing angle
    m = Basemap(projection='ortho', lat_0=lat_viewing_angle, lon_0=lon_viewing_angle) 

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

    #print("Reading shapefile...")
    m.readshapefile(f'shapefiles/World_Countries/World_Countries', 'countries', drawbounds=True, linewidth=1, color='black')
    #print("Shapefile read.")

    return m, ax, fig
    
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

def build_countries_dict(m):
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
    return countries_dict

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

def find_best_match_3(country_name, countries_dict):
    best_match = process.extractOne(country_name, countries_dict.keys(), scorer=fuzz.token_set_ratio)
    if best_match[1] < 85:
        best_match = process.extractOne(country_name, countries_dict.keys(), scorer=fuzz.token_sort_ratio)
    return best_match[0]

def find_best_match_4(country_name, countries_dict):
    specific_matches = {
        "Macau": "Nope",
        "Hong Kong": "Nope",
        "Vatican City": "Nope",
        "Sint Maarten": "Nope",
        "Curaçao": "Nope",
        "Saint Barthélemy": "Nope",
        "Kosovo": "Nope",
        "Eswatini": "Nope",
        "Åland Islands": "Nope",
        "Saint Martin": "Nope",
        "Caribbean Netherlands": "Nope",
        "Republic of the Congo": "Congo",
        "North Macedonia": "macedonia",
        "DR Congo": "democratic republic of the congo",
        "South Georgia": "south georgia and the south sandwich is (uk)",
        "United States Virgin Islands": "american virgin islands (us)",
        "Saint Helena, Ascension and Tristan da Cunha": "st. helena (uk)",
        "Czechia": "czech republic"
    }
    
    if country_name in specific_matches:
        if specific_matches[country_name] == "Nope":
            return None
        else:
            country_name = specific_matches[country_name]
    
    best_match, ratio = find_best_match(country_name, countries_dict)

    if (ratio < 95):
        return find_best_match_3(country_name, countries_dict)

    return best_match

# Function to add shapes to the map
def add_shapes(m, country, ax):
    # Dictionary to store country names and corresponding shapes and info
    countries_dict = build_countries_dict(m)

    best_match = find_best_match_4(country['name']['common'], countries_dict)
    if best_match is None:
        print(f"Could not find a match for {country['name']['common']}.")
        with open(f"globes/{country['name']['common']}/info.txt", 'w') as f:
            f.write(f"Could not find a match for {country['name']['common']}")
        return False

    print(f"Best match for {country['name']['common']}: {best_match}")
    with open(f"globes/{country['name']['common']}/info.txt", 'w') as f:
        f.write(f"Best match for {country['name']['common']}: {best_match}")

    # Add all the shapes for the best matching country
    for shape in countries_dict[best_match]["shapes"]:
        shape = np.array(shape)
        ax.add_patch(mpatches.Polygon(shape, facecolor='red', edgecolor='k', linewidth=1., zorder=2, closed=True))

    return True


# Function to plot the globe
def plot_globe(country):
    m, ax, fig = init_globe(country)
    
    # Add marker if country is small
    if country['area'] < 100000:
        x, y = m(country['latlng'][1], country['latlng'][0])
        m.plot(x, y, 'ro', markersize=5)
    
    Path(f"globes/{country_name}").mkdir(parents=True, exist_ok=True)  

    # Add shapes for the given country
    res = add_shapes(m, country, ax)
    if res is False:
        plt.close(fig)
        return res

    # Save figure
    filename_pdf = f"globes/{country_name}/{country_name}.pdf"
    filename_svg = f"globes/{country_name}/{country_name}.svg"
    plt.savefig(filename_pdf, format='pdf')
    plt.savefig(filename_svg, format='svg')
    plt.close(fig)


if __name__ == '__main__':
    #country_name = input("Enter the name of a country: ")
    start_time = time.time()
    countries = get_all_countries()
    failed = []
    count = 0
    start_time = time.time()
    for country in countries:
        country_name = country['name']['common']
        count += 1
        print()
        elapsed_time = time.time() - start_time
        print("Time elapsed: {:.2f} seconds".format(elapsed_time))
        print("--------------------------------")
        print()
        print(f"Country {count}/{len(countries)}: {country_name}")
        print(f"Generating globe for {country_name}...")
        res = plot_globe(country)
        if res is False:
            failed.append(country_name)
            print()
            print("--------------------------------")
            print()
            continue

        print(f"Globe for {country_name} generated.")
        print()
        print("--------------------------------")
        print()
    
    print("Failed to generate globes for:")
    for country in failed:
        print(country)