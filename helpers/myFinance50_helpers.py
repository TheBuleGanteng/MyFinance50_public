import base64
import csv
from datetime import datetime, timedelta
from extensions import db
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app
from flask_babel import Babel, format_decimal
from google.auth import impersonated_credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from itsdangerous import TimedSerializer as Serializer
import mimetypes
from models import Listing, Transaction
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


# Count API pings per day (to use, simply call increment_ping(). You can then print last_pint[pings])
last_ping = { # Global variable to store the counter
    'pings': 0,
    'timestamp': datetime.now()
}

def increment_ping(): # Function to increment the counter
    global last_ping
    if datetime.now().date() != last_ping['timestamp'].date():
        last_ping['pings'] = 0
        
    last_ping['pings'] += 1
    last_ping['timestamp'] = datetime.now()
    print(f'PING COUNTER: {last_ping["pings"]}')


# Apology (CS50 legacy)
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



# Pull company data via FMP API
def company_data(symbol, fmp_key):
    print(f'running get_stock_info(symbol): ... symbol is: { symbol }')
        
    try:
        limit = 1
        response = requests.get(f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={fmp_key}')       
        increment_ping()
        print(f'running get_stock_info(symbol): ... response is: { response }')
        data = response.json()
        #print(f'running get_stock_info(symbol): ... data is: { data }')

        # Check if data contains at least one item
        if data and isinstance(data, list):
            return data[0]
        else:
            return None

    except Exception as e:
        print(f'running get_stock_info(symbol): ... function tried symbol: { symbol } but errored with error: { e }')
        return None


# Converts a timestamp into YYYY-MM-DD HH:MM format (can be called directly or used as jinja filter)
def date_time(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ""
    # Check if 'value' is already a datetime object
    if isinstance(value, datetime):
        return value.strftime(format)
    # If 'value' is a string, then parse it (this part might be optional based on your use case)
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f').strftime(format)


# Defines key for FMP api
fmp_key = os.getenv('FMP_API_KEY')


# Login required (CS50 legacy)
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



# Generates a nonce to work with Talisman-managed CSP
def generate_nonce():
        return os.urandom(16).hex()


# Token generation for password reset and registration
def generate_unique_token(id, secret_key):
    print(f'running generate_unique_token(id)... starting')
    s = Serializer(secret_key, salt='reset-salt')
    print(f'running generate_unique_token(id)... generated token')
    return s.dumps({'id': id})


# Set token age (used for token generation and to set auto removal of stale DB records)
max_token_age_seconds = os.getenv('MAX_TOKEN_AGE_SECONDS')


# Formats number with commas and periods, relative to user's location 
# Can be called directly or used as jinja filter.
def number_format(value):
    if value is None:
        return ""
    # Format number
    try:
        # Convert to integer for formatting
        value = int(value)
        # Use Flask-Babel's format_decimal to format the number according to the current locale
        return format_decimal(value)
    except (ValueError, TypeError):
        return value



# Custom jinja filter: x.xx% or (x.xx%)
def percentage(value):
    """Format value as USD."""
    if value >= 0:
        return f"{value*100:,.2f}%"
    else:
        return f"({-value*100:,.2f}%)"


# Processes share purchase
def process_purchase(symbol, shares, user, result):
    print(f'running /process_purchase() ...  for user { user.id } ...  function started')

    new_transaction = Transaction(
                    user_id = user.id,
                    type = 'BOT',
                    symbol = symbol,
                    transaction_shares = shares,
                    transaction_value_per_share = result['transaction_value_per_share'], 
                    transaction_value_total= result['transaction_value_total'],
                    shares_outstanding = shares,
                    )
    db.session.add(new_transaction)
    db.session.commit()
    print(f'running /process_purchase() ...  for user { user.id } ...  new transaction added: { new_transaction }')


# Processes share sale
def process_sale(symbol, shares, user, result):
    print(f'running /process_sale() ...  for user { user.id } ...  function started')

    # Initialize shares_to_fill variable to avoid confusion
    shares_to_fill = shares
    symbol_market_price = company_data(symbol, fmp_key)['price']
    cutoff_date = datetime.now() - timedelta(days=365)
    tax_offset_coefficient = 1 if user.tax_loss_offsets == 'Yes' else 0
    tax_rate_STCG = user.tax_rate_STCG / 100
    tax_rate_LTCG = user.tax_rate_LTCG / 100
    
    print(f'running /process_sale() ...  for user { user.id } ...  shares is: { shares }')
    print(f'running /process_sale() ...  for user { user.id } ...  symbol_market_price is: { symbol_market_price }')
    print(f'running /process_sale() ...  for user { user.id } ...  cutoff_date is: { cutoff_date }')
    print(f'running /process_sale() ...  for user { user.id } ...  tax_offset_coefficient is: { tax_offset_coefficient }')

    # We initialize a list of transaction changes to commit all at once once the loop below is complete
    updated_transactions = []
    print(f'running /process_sale() ...  for user { user.id } ...  updated_transactions list initialized')

    # Initialize capital gains variables that will be incremented later
    STCG = 0
    STCG_tax = 0
    LTCG = 0
    LTCG_tax = 0

    # Set method of cycling closing out open positions relative to user accounting_method setting
    transactions_to_iterate = user.transactions if user.accounting_method == 'FIFO' else reversed(user.transactions)
    print(f'running /process_sale() ...  for user { user.id } ...  transactions_to_iterate is: { transactions_to_iterate }')

    # Loop through each of the user's BOT transactions
    for transaction in transactions_to_iterate:    
        # Look at only the purchases
        if transaction.symbol == symbol and transaction.type == 'BOT':
            # If txn has enough shares, fill the order
            if transaction.shares_outstanding > shares_to_fill:
                transaction.shares_outstanding -= shares_to_fill 
                if transaction.timestamp > cutoff_date:
                    STCG += round((shares_to_fill * symbol_market_price) - (shares_to_fill * transaction.transaction_value_per_share),2)
                    STCG_tax += round(STCG * tax_rate_STCG,2)  
                else:
                    LTCG += round((shares_to_fill * symbol_market_price) - (shares_to_fill * transaction.transaction_value_per_share),2)
                    LTCG_tax += round(LTCG * tax_rate_LTCG,2)
                shares_to_fill = 0
                updated_transactions.append(transaction)
                print(f'running /process_sale() ...  for user { user.id } ... sell order filled with transaction: { transaction }')
                break
            else:
                transaction.shares_outstanding = 0
                shares_to_fill -= transaction.shares_outstanding
                updated_transactions.append(transaction)
    
    # Update the DB once the loop above is finished running
    for transaction in updated_transactions:
        db.session.add(transaction)
    db.session.commit()
    print(f'running /process_sale() ...  for user { user.id } ... updated_transactions updated to: { updated_transactions }')
    
    # Que up the new transaction to be added to the transactions table (shares_outstanding is omitted because this is a sale)
    new_transaction = Transaction(
                    user_id = user.id,
                    type = 'SLD',
                    symbol = symbol,
                    transaction_shares = shares,
                    transaction_value_per_share = result['transaction_value_per_share'], 
                    transaction_value_total= result['transaction_value_total'],
                    STCG = STCG,
                    LTCG = LTCG,
                    STCG_tax = STCG_tax,
                    LTCG_tax = LTCG_tax
                )
    db.session.add(new_transaction)
    print(f'running /sell ...  user.cash before deducting transaction_value_total is: { user.cash } ')
    
    # Adjust cash and commit changes to DB
    user.cash = user.cash + result['transaction_value_total']
    print(f'running /sell ...  user.cash after deducting transaction_value_total is: { user.cash } ')        
    
    # Commit all the changes made via the loop and the creation of new_transaction
    db.session.commit()
    print(f'running /sell ...  new_transaction added to DB is: { new_transaction } and user.cash is: { user.cash }')

# Set project name (used in emails)
project_name = 'myFinance50'


# Purge unconfirmed accounts
def purge_unconfirmed_accounts():
    print(f'running purge_unconfirmed_accounts ... started: { datetime.now() }')
    
    token_validity = os.getenv('MAX_TOKEN_AGE_SECONDS')
    cutoff_time = datetime.now() - timedelta(seconds=token_validity)

    unconfirmed_accounts = db.session.query(User).filter(User.confirmed =='No', User.created < cutoff_time).delete()
    print(f'running purge_unconfirmed_accounts ... unconfirmed_accounts is: { unconfirmed_accounts }')
    db.session.commit
    print(f'running purge_unconfirmed_accounts ... completed: { datetime.now() }')


# Send emails
def send_email(body, recipient):    
    print(f'running send_email ... body is: {body}')
    
    # Load service account credentials
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '..', 'gitignored', 'gmail_access_credentials.json')
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


# Update the listings table in the DB
def update_listings(fmp_key):
    with current_app.app_context():
        url = f'https://financialmodelingprep.com/api/v3/available-traded/list?apikey={fmp_key}'
        response = requests.get(url)
        increment_ping()
        print(f'running purge_unconfirmed_accounts ... started: { datetime.now() }')
        
        # If the response is not problematic, do the following..
        if response.status_code == 200:
            listings_data = response.json()
            for item in listings_data:
                listing = Listing(
                    symbol=item.get('symbol'),
                    name=item.get('name'),
                    price=item.get('price'),
                    exchange=item.get('exchange'),
                    exchange_short=item.get('exchangeShortName'),
                    listing_type=item.get('type')
                )
                # Use current_app.extensions to access 'db'
                db.session.merge(listing)
            db.session.commit()
        else:
            print("Failed to fetch data from API")


# Custom jinja filter: $x.xx or ($x.xx)
def usd(value):
    """Format value as USD."""
    if value >= 0:
        return f"${value:,.2f}"
    else:
        return f"(${-value:,.2f})"


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