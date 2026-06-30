from flask import Flask, render_template
from requests_oauthlib import OAuth1
import requests
import json
import os
import config

app = Flask(__name__)

# set up OAuth so every request to BrickLink is signed with credentials
auth = OAuth1(
    config.CONSUMER_KEY,
    config.CONSUMER_SECRET,
    config.TOKEN,
    config.TOKEN_SECRET
)

# folder of downloaded images
IMAGE_DIR = os.path.join("static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)


def load_minifigure_ids():
    # reads a list of BrickLink item numbers from manually maintained file
    with open("minifigures.json") as f:
        data = json.load(f)
    return data["minifigures"]

def cache_image(item_no, image_url):
    # if BrickLink doesnt return an image, nothing to cache
    if not image_url:
        return None

    extension = image_url.split(".")[-1]
    local_filename = f"{item_no}.{extension}"
    local_path = os.path.join(IMAGE_DIR, local_filename)

    # only download if there is no local copy
    if not os.path.exists(local_path):
        # BrickLink blocks server to server requests for images
        # mask the request to look like a browser visiting the site
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bricklink.com/"
        }
        response = requests.get(image_url, headers=headers)
        print(f"Download status code: {response.status_code}")
        if response.status_code == 200:
            # if status code 200, save image
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"Saved to {local_path}")
        else:
            # else download failed
            print("Download failed")
            return None
    else:
        # image has already been downloaded
        print("Already cached")

    # return path relative to static folder
    return f"images/{local_filename}"

def get_minifigure_data(item_no):
    # look up basic catalogue info for the minifigure
    catalog_url = f"https://api.bricklink.com/api/store/v1/items/minifig/{item_no}"
    catalog_response = requests.get(catalog_url, auth=auth)

    if catalog_response.status_code != 200:
        # item doesnt exist or request failed, skip
        return None

    catalog_data = catalog_response.json()["data"]
    image_url = catalog_data.get("image_url")

    # BrickLink sometimes returns URL's with prefix '//' instead of 'https://'
    # this isnt valid so fix up
    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url

    local_image_path = cache_image(item_no, image_url)

    # look up average sold price for the minifigure (used condition)
    price_url = f"https://api.bricklink.com/api/store/v1/items/minifig/{item_no}/price"
    price_response = requests.get(price_url, auth=auth, params={"guide_type": "sold", "new_or_used": "U"})

    avg_price = None
    if price_response.status_code == 200:
        price_data = price_response.json()["data"]
        raw_price = price_data.get("avg_price")
        # round price to currency formatting
        if raw_price is not None:
            avg_price = round(float(raw_price), 2)

    return {
        "id": item_no,
        "name": catalog_data.get("name"),
        "price": avg_price,
        "image": local_image_path
    }

@app.route("/")
def index():
    item_ids = load_minifigure_ids()
    minifigures = []

    # build full list of minifigure data to pass to the template
    for item_id in item_ids:
        result = get_minifigure_data(item_id)
        if result:
            minifigures.append(result)

    # calculate total number of minifigures
    total_figures = len(minifigures)

    # calculate total value of minifigures
    total_value = sum(fig["price"] for fig in minifigures if fig["price"] is not None)
    total_value = round(total_value, 2)

    return render_template(
        "index.html", 
        minifigures=minifigures,
        total_figures=total_figures,
        total_value=total_value
    )

if __name__ == "__main__":
    app.run(debug=True)
