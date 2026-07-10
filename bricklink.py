from requests_oauthlib import OAuth1
import requests
import config

# set up OAuth so every request to BrickLink is signed with credentials
auth = OAuth1(
    config.CONSUMER_KEY,
    config.CONSUMER_SECRET,
    config.TOKEN,
    config.TOKEN_SECRET
)

def fetch_catalog(item_no):
    # fetch basic catalogue info for a minifigure on BrickLink
    url = f"https://api.bricklink.com/api/store/v1/items/minifig/{item_no}"
    return requests.get(url, auth=auth)

def fetch_price(item_no):
    # fetch average sold price for a minifigure (new condition)
    url = f"https://api.bricklink.com/api/store/v1/items/minifig/{item_no}/price"
    return requests.get(url, auth=auth, params={"guide_type": "sold", "new_or_used": "N"})

def fetch_image(image_url):
    # BrickLink blocks plain server requests for images so we spoof browser headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bricklink.com/"
    }
    return requests.get(image_url, headers=headers)
    