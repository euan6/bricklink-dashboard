from requests_oauthlib import OAuth1
import requests
import config

auth = OAuth1(
    config.CONSUMER_KEY,
    config.CONSUMER_SECRET,
    config.TOKEN,
    config.TOKEN_SECRET
)

# API call test should return 'Obi-Wan Kenobi - Reddish Brown Robe, Dark Orange Mid-Length Tousled with Center Part Hair'
url = "https://api.bricklink.com/api/store/v1/items/minifig/sw1220"

response = requests.get(url, auth=auth)

print("Status code:", response.status_code)
print(response.json())
