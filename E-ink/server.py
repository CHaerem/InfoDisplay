from flask import Flask, send_file, jsonify
from PIL import Image, ImageEnhance, ImageOps
import requests
from io import BytesIO
import random
import os
import json

app = Flask(__name__)

last_country = None
countries_data = None

def load_countries_data():
    global countries_data
    # Check if the file exists
    if os.path.isfile("countries.json"):
        # Load the data from the file
        with open("countries.json", "r") as file:
            countries_data = json.load(file)
    else:
        # Fetch the data from the API
        response = requests.get("https://restcountries.com/v3.1/all")
        countries_data = response.json()
        # Save the data to the file
        with open("countries.json", "w") as file:
            json.dump(countries_data, file)

def get_flag(flag_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0.1',
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

@app.route('/flag/', defaults={'country_name': None})
@app.route('/flag/<country_name>')
def fetch_flag(country_name):
    global last_country
    global countries_data

    if countries_data is None:
        load_countries_data()

    country = None

    if country_name:
        for item in countries_data:
            if item['name']['common'].lower() == country_name.lower():
                country = item
                break

    # If no country specified, select a random country
    if not country:
        country = random.choice(countries_data)

    last_country = country

    # Get the flag URL
    flag_url = country["flags"]["png"]

    # Download and open the flag image
    flag_image = get_flag(flag_url)

    # Fill the image with black
    flag_image = flag_image.convert("RGBA")
    black_background = Image.new('RGBA', flag_image.size, 'black')
    flag_image = Image.alpha_composite(black_background, flag_image)

    # Optimize the flag image
    flag_image = optimize_image(flag_image)

    # Convert the flag image to a BMP format
    output = BytesIO()
    flag_image.save(output, format="BMP")
    output.seek(0)

    return send_file(output, mimetype='image/bmp')

@app.route('/info/', defaults={'country_name': None})
@app.route('/info/<country_name>')
def get_country_info(country_name):
    global countries_data
    global last_country

    if countries_data is None:
        load_countries_data()

    country = None

    if country_name is not None:
        for item in countries_data:
            if item['name']['common'].lower() == country_name.lower():
                country = item
                break

        # If country is not found in the list, return an error
        if not country:
            return jsonify({"error": f"No country found with name {country_name}."})
    else:
        country = last_country
        if country is None:
            return jsonify({"error": "No country has been fetched yet."})

    # Extract the desired information
    name = country['name']['common']
    capital = country['capital'][0] if country['capital'] else 'No capital found'
    population = country['population']
    currency_code, currency_info = list(country['currencies'].items())[0]
    currency_symbol = currency_info.get('symbol', 'N/A')  # Use get method to provide default value if 'symbol' key does not exist
    currency = f"{currency_info['name']} ({currency_code}, {currency_symbol})"
    languages = ', '.join([v for k, v in country['languages'].items()])
    area = country['area']

    # Return a simplified JSON object
    return jsonify({
        'name': name,
        'capital': capital,
        'population': population,
        'currency': currency,
        'language': languages,
        'area': area
    })

def optimize_image(image):
    # Resize and center image
    image = resize_and_center_image(image, (800, 480))

    # Adjust contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # Increase contrast

    # Reduce colors (quantize)
    image = image.quantize(colors=7)

    # Apply dithering
    image = image.convert('RGB', dither=Image.NONE)

    return image

def resize_and_center_image(image, display_size):
    # Calculate scale factors for width and height
    width_scale = display_size[0] / image.size[0]
    height_scale = display_size[1] / image.size[1]

    # Use the smaller scale factor to maintain aspect ratio
    scale_factor = min(width_scale, height_scale)

    # Resize the image
    new_size = (int(image.size[0] * scale_factor), int(image.size[1] * scale_factor))
    image = image.resize(new_size, Image.LANCZOS)

    # Create a new image with a black background and the display size
    new_image = Image.new('RGB', display_size, 'black')

    # Calculate the position to paste the image onto the new image to center it
    paste_position = ((display_size[0] - new_size[0]) // 2, (display_size[1] - new_size[1]) // 2)

    # Paste the image onto the new image
    new_image.paste(image, paste_position)

    return new_image


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
