from datetime import datetime, timedelta
from entry import Entry, create_if_not_exists
from app import app, cache, db, API_URI_TODAY, API_URI_YESTERDAY, CURRENCY_LIST

import asyncio
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

def get_yesterday_value(currency_id: str):
    """
    Fetches yesterday's value for the specified `currency_id`.
    """

    result = db.session.query(Entry.value)\
                      .filter_by(
                              currency_id = currency_id,
                              date = (datetime.today() - timedelta(1)).strftime("%Y-%m-%d")
                      )\
                      .first()

    if result:
        (value, *_) = result
        return value

    return 0

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

    url = f"{API_URI_TODAY}/currencies.min.json"
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
    yesterday_value = ""
    _y = get_yesterday_value(currency_id)
    value_change = ""
    date = reformat_date(data["date"])
    increased = False
    day_before_date = reformat_date(
        (datetime.strptime(data["date"], "%Y-%m-%d") - timedelta(1))\
            .strftime("%Y-%m-%d")
    )

    # If rounded to two decimal places, GBP to BTC registers as GBP being worth
    # 0 BTC, which is obviously not true. So for Bitcoin, we increase the
    # precision to 8 d.p. so that a more accurate result can be displayed.
    #
    # This should hold true for lower value currencies too.
    if currency_id != "btc":
        value = f"{data[currency_id]:.4f}"
        yesterday_value = f"{_y:.4f}"
        value_change=f"{((_y - data[currency_id])/data[currency_id])*100:.2f}"
    else:
        value = f"{data[currency_id]:.8f}"
        yesterday_value = f"{_y:.8f}"
        value_change=f"{((_y - data[currency_id])/data[currency_id])*100:.4f}"

    increased = float(value_change) >= 0

    return {
        "title": title,
        "detail":
            f"As of {date}, the {base_currency_title} is worth {value} {title}. " +
            f"Compared to the day before, {day_before_date}, where the {base_currency_title} was worth {yesterday_value} {title}. " +
            f"This marks a {abs(float(value_change))}% {'increase' if increased else 'decrease'} in value since last record."
    }


@cache.memoize(1000)
async def get_data(base_currency_id: str, base: str) -> list[dict[str, any]]:
    """
    Returns the full comparison list for each of the specified currencies in
    CURRENCY_LIST, calling the appropriate formatting functions so that the
    data can be presented to the telephony API in the expected format.
    """

    currency_comparisons = []

    date = ""
    if base == API_URI_YESTERDAY:
        date = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    else:
        date = datetime.now().strftime("%Y-%m-%d")

    for currency_id in CURRENCY_LIST:
        url = f"{base}/currencies/{base_currency_id}/{currency_id}.min.json"
        data: dict[str, any] = dict(requests.get(url = url).json())
        currency_comparisons.append(reformat_dict(data, currency_id, base_currency_id))
        entry = Entry(
            currency_id = currency_id,
            date = date,
            value = data[currency_id]
        )
        create_if_not_exists(entry)

    db.session.commit()

    return currency_comparisons


@cache.memoize(1000)
async def get_yesterday(base_currency_id: str) -> list[dict[str, any]]:
    """
    Fetches the data from the API about yesterday's currency values, populating
    the database for later usage.
    """

    return get_data(base_currency_id, API_URI_YESTERDAY)

@cache.memoize(1000)
async def get_today(base_currency_id: str) -> list[dict[str, any]]:
    """
    Fetches the data from the API about today's currency values, populating the
    database for later usage.
    """

    return get_data(base_currency_id, API_URI_TODAY)

@app.get("/")
@app.get("/<currency_id>")
@cache.cached()
async def root(currency_id: str = "gbp"):
    get_yesterday(currency_id)
    return { "items": get_today(currency_id) }


if __name__ == "__main__":
    asyncio.run(app.run())
