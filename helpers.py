import base64
import csv
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_oauthlib.client import OAuth
from google.auth import impersonated_credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from itsdangerous import TimedSerializer as Serializer
import mimetypes
import os
import pytz
import random
import requests
import string
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
        #print(f'running lookup(symbol)... resonse is: { response }')
        #print(f'running lookup(symbol)... price is: { price }')
        #print(f'running lookup(symbol)... quotes is: { quotes }')
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


# Pull company data via FMP API
def company_data(symbol, fmp_key):
    print(f'running get_stock_info(symbol): ... symbol is: { symbol }')
    print(f'running get_stock_info(symbol): ... fmp_key is: { fmp_key }')
    
    try:
        limit = 1
        response = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={fmp_key}')       
        print(f'running get_stock_info(symbol): ... response is: { response }')
        data = response.json()
        print(f'running get_stock_info(symbol): ... data is: { data }')

        # Check if data contains at least one item
        if data and isinstance(data, list):
            return data[0]
        else:
            return None

        
    except Exception as e:
        print(f'running get_stock_info(symbol): ... function tried symbol: { symbol } but errored with error: { e }')
        return None


# Send emails
def send_email(body, recipient):
    
    print(f'running send_email ... body is: {body}')
    
    # Load service account credentials
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'gitignored', 'gmail_access_credentials.json')
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    # Now use the source credentials to acquire credentials to impersonate another service account
    credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # If you're using domain-wide delegation, specify the user to impersonate
    credentials = credentials.with_subject('donotreply@mattmcdonnell.net')

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=credentials)

    # Create and send email
    email_msg = body
    mime_message = MIMEMultipart()
    mime_message['to'] = f'{recipient}'
    mime_message['from'] = 'donotreply@mattmcdonnell.net'
    mime_message.attach(MIMEText(email_msg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    print('Message Id: %s' % message['id'])
