# Minifig Dashboard

A locally-hosted web dashboard for tracking and visualising a personal LEGO minifigure collection, built with Flask and the BrickLink API.

![Python](https://img.shields.io/badge/Python-3.13-blue) ![Flask](https://img.shields.io/badge/Flask-3.1.3-lightgrey) ![BrickLink API](https://img.shields.io/badge/BrickLink-API-f0c040)

## Features

- Displays total collection value, figure count, average price, and theme breakdown
- Ring chart for theme distribution and bar chart for figures by year
- Top 3 most valuable figures shown in a sidebar
- Minifigure images fetched and cached locally from BrickLink
- API responses cached for 24 hours to minimise requests and improve load times
- Parallel fetching for fast initial load across large collections
- Friendly error handling for credential and IP mismatch issues

## Prerequisites

- Python 3.13
- A BrickLink account with API credentials (consumer key, consumer secret, token, token secret)

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/bricklink-dashboard.git
cd bricklink-dashboard
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure credentials**

Create a `.env` file in the project root:

```
BRICKLINK_CONSUMER_KEY=your_key_here
BRICKLINK_CONSUMER_SECRET=your_secret_here
BRICKLINK_TOKEN=your_token_here
BRICKLINK_TOKEN_SECRET=your_token_secret_here
FLASK_DEBUG=false
```

BrickLink API credentials can be obtained from your BrickLink account under API Settings. Note that API access requires a seller account registration.

**5. Add your minifigures**

Edit `minifigures.json` with your BrickLink item numbers:

```json
{
    "_comment": "BrickLink item numbers - format: prefix + number e.g. sw = Star Wars, njo = Ninjago",
    "minifigures": [
        "sw1220",
        "sw1221"
    ]
}
```

Item numbers can be found on any minifigure's BrickLink catalogue page under "Item No".

**6. Run the app**

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
bricklink-dashboard/
├── app.py                  # Flask routes and data processing
├── bricklink.py            # BrickLink API calls
├── cache.py                # Cache reading, writing, and validation
├── config.py               # Credential loading and validation
├── minifigures.json        # Manual list of owned item numbers
├── cache.json              # Auto-generated API response cache (24hr TTL)
├── requirements.txt
├── templates/
│   ├── index.html          # Dashboard landing page
│   └── error.html          # Auth error page
└── static/
    ├── style.css
    ├── script.js
    └── images/             # Auto-populated with cached minifigure images
```

## Caching

On first load, the app fetches catalogue and price data from BrickLink for every figure in your list and saves it to `cache.json`. Images are downloaded and saved to `static/images/`. Subsequent loads read from the local cache and are near instant.

Cache data expires after 24 hours, after which the app will re-fetch updated prices from BrickLink. To force a refresh manually, delete `cache.json`.

## Adding New Themes

Minifigure themes are derived from BrickLink item number prefixes. If a figure shows as "Other" in the theme breakdown, add its prefix to the `THEME_PREFIXES` dictionary in `app.py`:

```python
THEME_PREFIXES = {
    "sw": "Star Wars",
    "njo": "Ninjago",
    # add new prefixes here
}
```

## Notes

- BrickLink API access requires your registered IP address to match the one making requests. If your home IP changes (common with most UK broadband), update it in your BrickLink API settings.
- Price data reflects the average sold price for new condition figures on BrickLink's marketplace only.
- `debug=True` is controlled via `FLASK_DEBUG` in `.env` and should be set to `false` outside of development.
