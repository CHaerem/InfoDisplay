from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, render_template, send_from_directory
import requests
import random
import os

app = Flask(__name__)
toolbar = DebugToolbarExtension(app)

@app.route("/country/")
def display_random_country():
    # Make GET request to restcountries API 
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    data = response.json()

    # Choose a random country from the response
    random_index = random.randint(0, len(data) - 1)
    random_country = data[random_index]

    return render_template("country.html", data=random_country)

@app.route("/country/<country_name>")
def display_country(country_name):
    # Make GET request to restcountries API
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url)
    data = response.json()[0]

    return render_template("country.html", data=data)

@app.route("/country/globe/<country_name>")
def get_globe(country_name):
    try:
        return send_from_directory(f"Globe/globes/{country_name}/", f"{country_name}.svg")
    except FileNotFoundError:
        return "Globe not found", 404

@app.route("/country/assets/<asset>")
def get_asset(asset):
    try:
        return send_from_directory("templates/", asset)
    except FileNotFoundError:
        return asset, 404

if __name__ == "__main__":
    app.run()
