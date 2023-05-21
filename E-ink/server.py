from flask import Flask, send_file, jsonify
from PIL import Image
import requests
from io import BytesIO
import random

app = Flask(__name__)

last_country = None

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

    # Get the list of countries
    response = requests.get("https://restcountries.com/v3.1/all")
    data = response.json()

    country = None

    if country_name:
        for item in data:
            if item['name']['common'].lower() == country_name.lower():
                country = item
                break

    # If no country specified, select a random country
    if not country:
        country = random.choice(data)

    last_country = country

    # Get the flag URL
    flag_url = country["flags"]["png"]

    # Download and open the flag image
    flag_image = get_flag(flag_url)

    # Resize the flag image to the display size
    resized_flag_image = flag_image.resize((648, 480), Image.ANTIALIAS)

    # Convert the flag image to a BMP format
    output = BytesIO()
    resized_flag_image.save(output, format="BMP")
    output.seek(0)

    return send_file(output, mimetype='image/bmp')

@app.route('/info')
def get_last_country_info():
    if last_country is not None:
        return jsonify(last_country)
    else:
        return jsonify({"error": "No country has been fetched yet."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
