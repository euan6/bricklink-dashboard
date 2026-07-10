from flask import Flask, render_template
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import json
import os
import config
import time
import datetime
# import other python files
import bricklink
import cache as cache_module

app = Flask(__name__)

_cache_lock = Lock()

# folder of downloaded images
IMAGE_DIR = os.path.join("static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# prefixes of minifigure themes
THEME_PREFIXES = {
    "sw": "Star Wars",
    "sc": "Speed Champions",
    "poc": "Pirates of the Caribbean",
    "toy": "Toy Story",
    "atl": "Atlantis",
    "iaj": "Indiana Jones",
    "pm": "Power Miners",
    "ac": "Space",
    "pi": "Pirates",
    "hp": "Harry Potter",
    "pha": "Pharaoh's Quest",
    "col": "Collectible Minifigures",
    "cty": "City"
}

def get_theme_from_id(item_no):
    # return the theme based on the minifigures prefix 
    for prefix, theme_name in THEME_PREFIXES.items():
        if item_no.startswith(prefix):
            return theme_name
    print(f"Unrecognised theme prefix for item: {item_no}")
    return "Other"

def load_minifigure_ids():
    if not os.path.exists("minifigures.json"):
        # handle if JSON file is not found
        print("minifigures.json not found, starting with an empty collection")
        return []
    try:
        # reads a list of BrickLink item numbers from manually maintained file
        with open("minifigures.json") as f:
            data = json.load(f)
        return data.get("minifigures", [])
    except json.JSONDecodeError:
        # JSON exception thrown if file is malformed
        print("minifigures.json is malformed, starting with empty collection")
        return []

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
        response = bricklink.fetch_image(image_url)
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

def get_minifigure_data(item_no, cache):
    # return cached data if its still fresh
    if cache_module.is_cache_valid(cache, item_no):
        return cache[item_no]["data"]

    catalog_response = bricklink.fetch_catalog(item_no)

    if catalog_response.status_code != 200:
        # item does not exist or request failed, skip
        return None

    response_json = catalog_response.json()
    if "data" not in response_json:
        description = response_json.get("meta", {}).get("description", "")
        message = response_json.get("meta", {}).get("message", "")
        if "TOKEN_IP_MISMATCHED" in description:
            # if IP does not match BrickLink submitted IP
            raise ConnectionError("TOKEN_IP_MISMATCHED")
        if "SIGNATURE_INVALID" in description or "BAD_OAUTH_REQUEST" in message:
            # if credentials have not been authenticated
            raise ConnectionError("BrickLink authentication failed")
        print(f"No data returned for {item_no}: {response_json}")
        return None

    catalog_data = response_json["data"]
    image_url = catalog_data.get("image_url")

    # BrickLink sometimes returns URL's with prefix '//' instead of 'https://'
    if image_url and image_url.startswith("//"):
        image_url = "https:" + image_url

    local_image_path = cache_image(item_no, image_url)

    # look up average sold price for the minifigure (used condition)
    price_response = bricklink.fetch_price(item_no)

    avg_price = None
    if price_response.status_code == 200:
        price_data = price_response.json()["data"]
        raw_price = price_data.get("avg_price")
        # format price to two decimal places
        if raw_price is not None:
            avg_price = f"{float(raw_price):.2f}"

    result = {
        "id": item_no,
        "name": catalog_data.get("name"),
        "price": avg_price,
        "image": local_image_path,
        "theme": get_theme_from_id(item_no),
        "year": catalog_data.get("year_released")
    }

    # save to cache with timestamp
    with _cache_lock:
        cache[item_no] = {
            "data": result,
            "cached_at": time.time()
        }
        cache_module.save_cache(cache)

    return result

@app.route("/")
def index():
    cache = cache_module.load_cache()
    item_ids = load_minifigure_ids()
    minifigures = []

    try:
        # build full list of minifigure data to pass to the template
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(get_minifigure_data, item_id, cache): item_id for item_id in item_ids}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    minifigures.append(result)
    except ConnectionError as e:
        # throw exceptions if connection has an error or IP has mismatched
        error = str(e)
        if "TOKEN_IP_MISMATCHED" in error:
            return render_template("error.html", 
                message="Your IP address has changed since registering with BrickLink.",
                fix="Update your IP address in BrickLink API settings and restart the app."
            )
        return render_template("error.html",
            message="Could not connect to BrickLink.",
            fix="Check your API credentials in .env and try again."
        )

    # calculate total number of minifigures
    total_figures = len(minifigures)

    # calculate total value of minifigures
    total_value = sum(float(fig["price"]) for fig in minifigures if fig["price"] is not None)
    total_value = f"{total_value:.2f}"

    # calculate the most common theme of minifigures
    theme_counts = Counter(fig["theme"] for fig in minifigures)
    most_common_theme = theme_counts.most_common(1)[0][0] if theme_counts else None

    # calculate the year distribution of minifigures
    year_counts = Counter(fig["year"] for fig in minifigures if fig["year"] is not None)
    year_distribution = dict(sorted(year_counts.items()))

    # calculate theme distribution
    theme_distribution = dict(theme_counts)

    # calculate top 3 minifigures
    top_3 = sorted(
        [f for f in minifigures if f["price"] is not None],
        key=lambda x: float(x["price"]),
        reverse=True
    )[:3]

    # calculate average price per minifigure
    avg_price_raw = sum(float(fig['price']) for fig in minifigures if fig['price'] is not None) / total_figures if total_figures > 0 else 0
    avg_price = f"{avg_price_raw:.2f}"

    # calculate the number of different themes
    num_themes = len(theme_counts)

    # 
    cached_times = [
        cache[item_id]["cached_at"]
        for item_id in item_ids
        if item_id in cache
    ]
    last_updated = (
        datetime.datetime.fromtimestamp(max(cached_times)).strftime("%d %b %Y, %H:%M")
        if cached_times else "Never"
    )

    return render_template(
        "index.html", 
        minifigures=minifigures,
        total_figures=total_figures,
        total_value=total_value,
        most_common_theme=most_common_theme,
        year_distribution=year_distribution,
        theme_distribution=theme_distribution,
        top_3=top_3,
        avg_price=avg_price,
        num_themes=num_themes,
        last_updated=last_updated
    )

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
