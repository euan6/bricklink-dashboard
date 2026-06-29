import os
from dotenv import load_dotenv

load_dotenv()

# load and store API credentials
CONSUMER_KEY = os.getenv("BRICKLINK_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("BRICKLINK_CONSUMER_SECRET")
TOKEN = os.getenv("BRICKLINK_TOKEN")
TOKEN_SECRET = os.getenv("BRICKLINK_TOKEN_SECRET")
