from flask import Flask
from flask_caching import Cache
from datetime import datetime

import os
import requests


"""
Default currency list:

 1. USD (US Dollar)
 2. EUR (Euro)
 3. YEN (Japanese Yen)
 4. AUD (Austrailian Dollar)
 5. CAD (Canadian Dollar)
 6. CHF (Swiss Franc)
 7. CNY (Chinese Yuan)
 8. HKD (Hong Kong Dollar)
 9. NZD (New Zealand Dollar)
 10. BTC (Bitcoin)
"""

CURRENCY_LIST = [
    "usd", "eur", "jpy", "aud", "cad",
    "chf", "cny", "hkd", "nzd", "btc"
]

# API_URI = "https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/"
API_URI = "https://raw.githubusercontent.com/fawazahmed0/currency-api/1/latest"

app_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 1000,
    "CACHE_REDIS_HOST": os.environ.get("REDIS_HOST"),
    "CACHE_REDIS_PORT": int(os.environ.get("REDIS_PORT")),
    "CACHE_REDIS_DB": 1,
}

app = Flask("currency-value")
app.config.from_mapping(app_config)
cache = Cache(app)

def reformat_date(date: str) -> str:
    """
    Reformats the date string received from the API into a string that is
    easily parsible into Human speech.
    """

    date: datetime = datetime.strptime(date, "%Y-%m-%d")

    return date.strftime("%A %-d %B %Y")

@cache.memoize(1000)
def get_title(currency_id: str) -> str:
    """
    Gets the actual name of the currency from the given `currency_id`.
    """

    url = f"{API_URI}/currencies.min.json"
    title: str = dict(requests.get(url = url).json())[currency_id]

    words: list[str] = title.split(' ')
    words = [x.capitalize() for x in words]
    title =  ' '.join(words)

    return title

def reformat_dict(
        data: dict[str, any],
        currency_id: str,
        base_currency_id: str
    ) -> dict[str, str | int]:
    """
    Reformats the comparative data received from the API into a format that
    fits the schema supplied.
    """

    title = get_title(currency_id)
    base_currency_title = get_title(base_currency_id)
    value = ""
    date = reformat_date(data["date"])

    # If rounded to two decimal places, GBP to BTC registers as GBP being worth
    # 0 BTC, which is obviously not true. So for Bitcoin, we increase the
    # precision to 8 d.p. so that a more accurate result can be displayed.
    #
    # This should hold true for lower value currencies too.
    if currency_id != "btc":
        value = f"{data[currency_id]:.2f}"
    else:
        value = f"{data[currency_id]:.8f}"

    return {
        "title": title,
        "description": f"As of {date}, the {base_currency_title} is worth {value} {title}."
    }

@cache.memoize(1000)
def get_data(base_currency_id: str) -> list[dict[str, any]]:
    """
    Returns the full comparison list for each of the specified currencies in
    CURRENCY_LIST, calling the appropriate formatting functions so that the
    data can be presented to the telephony API in the expected format.
    """

    currency_comparisons = []

    for currency_id in CURRENCY_LIST:
        url = f"{API_URI}/currencies/{base_currency_id}/{currency_id}.min.json"
        data: dict[str, any] = dict(requests.get(url = url).json())
        currency_comparisons.append(reformat_dict(data, currency_id, base_currency_id))

    return currency_comparisons

@app.get("/")
@app.get("/<currency_id>")
@cache.cached()
def root(currency_id: str = "gbp"):
    return { "items": get_data(currency_id) }

