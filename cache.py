import json
import os
import time

CACHE_FILE = "cache.json"
CACHE_TTL = 31536000 # 1 year in seconds

def load_cache():
    if not os.path.exists(CACHE_FILE):
        # return empty cache if CACHE_FILE not found
        return {}
    try:
        # load the cache file
        with open(CACHE_FILE) as f:
            return json.load(f)
    except json.JSONDecodeError:
        # JSON exception thrown if file is corrupted
        print("cache.json is corrupted, starting with empty cache")
        return {}

def save_cache(cache):
    # write to cache file
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def is_cache_valid(cache, item_no):
    # check if cache is valid
    if item_no not in cache:
        return False
    age = time.time() - cache[item_no].get("cached_at", 0)
    return age < CACHE_TTL
