import quart.flask_patch

from datetime import datetime, timedelta
from quart import Quart
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import create_database, database_exists

import os

CURRENCY_LIST = [
    "usd", "eur", "jpy", "aud", "cad",
    "chf", "cny", "hkd", "nzd", "btc"
]

API_URI_BASE = "https://raw.githubusercontent.com/fawazahmed0/currency-api/1/"
API_URI_TODAY = f"{API_URI_BASE}/latest/"
API_URI_YESTERDAY = f"{API_URI_BASE}/{(datetime.today() - timedelta(1)).strftime('%Y-%m-%d')}"

app_config = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 1000,
    "CACHE_REDIS_HOST": os.environ.get("REDIS_HOST"),
    "CACHE_REDIS_PORT": int(os.environ.get("REDIS_PORT")),
    "CACHE_REDIS_DB": 1,
    "SQLALCHEMY_DATABASE_URI": 
        f"postgresql://{os.environ.get('POSTGRESQL_USERNAME')}:{os.environ.get('POSTGRESQL_PASSWORD')}" +
        f"@{os.environ.get('POSTGRESQL_HOST')}:{os.environ.get('POSTGRESQL_PORT')}/{os.environ.get('POSTGRESQL_DATABASE')}"
}

app = Quart("currency-value")
app.config.from_mapping(app_config)
cache = Cache(app)
db = SQLAlchemy(app)

if not database_exists(db.engine.url):
    create_database(db.engine.url)
