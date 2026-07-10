import os
from dotenv import load_dotenv

load_dotenv()

# load and store API credentials
CONSUMER_KEY = os.getenv("BRICKLINK_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("BRICKLINK_CONSUMER_SECRET")
TOKEN = os.getenv("BRICKLINK_TOKEN")
TOKEN_SECRET = os.getenv("BRICKLINK_TOKEN_SECRET")

# reads as a boolean, any value other than 'true' means debug is off
DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# check all required BrickLink credentials are present before running
REQUIRED_VARS = {
    "BRICKLINK_CONSUMER_KEY": CONSUMER_KEY,
    "BRICKLINK_CONSUMER_SECRET": CONSUMER_SECRET,
    "BRICKLINK_TOKEN": TOKEN,
    "BRICKLINK_TOKEN_SECRET": TOKEN_SECRET,
}

missing = [name for name, value in REQUIRED_VARS.items() if not value]
if missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing)}\n"
        "Check your .env file and ensure all BrickLink credentials are set."
    )
