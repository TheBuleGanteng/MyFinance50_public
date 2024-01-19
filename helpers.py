import csv
from datetime import datetime, timedelta
from itsdangerous import TimedSerializer as Serializer
import os
import pytz
import requests
import subprocess
import urllib
import uuid

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            print(f'running login_required()... no value for session[user]')
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.now()
    start = end - timedelta(days=7)

    # Yahoo Finance API
    url = (
        f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
        f"?period1={int(start.timestamp())}"
        f"&period2={int(end.timestamp())}"
        f"&interval=1d&events=history&includeAdjustedClose=true"
    )

    # Query API
    try:
        response = requests.get(url, cookies={"session": str(uuid.uuid4())}, headers={"User-Agent": "python-requests", "Accept": "*/*"})
        response.raise_for_status()

        # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
        quotes.reverse()
        price = round(float(quotes[0]["Adj Close"]), 2)
        print(f'running lookup(symbol)... resonse is: { response }')
        print(f'running lookup(symbol)... price is: { price }')
        print(f'running lookup(symbol)... quotes is: { quotes }')
        return {
            "name": symbol,
            "price": price,
            "symbol": symbol
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def timestamp_SG():
    singapore_tz = pytz.timezone("Asia/Singapore")
    timestamp_singapore = datetime.now(pytz.utc).astimezone(singapore_tz).replace(microsecond=0)

    print(f"Generated Timestamp (Singapore Time): {timestamp_singapore}")
    print(f"Timezone Info: {timestamp_singapore.tzinfo}")
    return timestamp_singapore

# Generates a nonce to work with Talisman-managed CSP
def generate_nonce():
        return os.urandom(16).hex()


# Set token age (used for token generation and to set auto removal of stale DB records)
max_token_age_seconds = os.getenv('MAX_TOKEN_AGE_SECONDS')

# Token generation for password reset and registration
def generate_unique_token(id, secret_key):
    print(f'running generate_unique_token(id)... starting')
    print(f'running generate_unique_token(id)... secret_key is: { secret_key }')
    s = Serializer(secret_key, salt='reset-salt')
    print(f'running generate_unique_token(id)... generated token')
    return s.dumps({'id': id})

# Token validation for password reset and registration
def verify_unique_token(token, secret_key, max_age):
    print(f'running verify_unique_token(token, max_age=max_token_age_seconds)... starting')
    from models import User
    print(f'running verify_unique_token(token, max_age=max_token_age_seconds)... user is: { User }')
    s = Serializer(secret_key, salt='reset-salt')
    print(f'running verify_unique_token(token, max_age=max_token_age_seconds):... s from Serializer is: { s }')
    try:
        data = s.loads(token, max_age=max_age)
        print(f'running verify_unique_token(token, max_age=max_token_age_seconds):... data is: { data }')
        user = data['id']
        print(f'running verify_unique_token(token, max_age=max_token_age_seconds):... data[id] is: { data["id"] }')
        return user
    except Exception as e:
        print(f'running verify_unique_token(token, max_age=max_token_age_seconds):... error is: { e }')
        return None