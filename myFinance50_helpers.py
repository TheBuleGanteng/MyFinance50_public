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
#from flask_oauthlib.client import OAuth
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


# Yahoo API call (CS50 legacy)
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


# Custom jinja filter: x.xx% or (x.xx%)
def percentage(value):
    """Format value as USD."""
    if value >= 0:
        return f"{value*100:,.2f}%"
    else:
        return f"({-value*100:,.2f}%)"


# Login required (CS50 legacy)
def process_sale(symbol, shares, transaction_type, user, result):
    print(f'running /process_sale() ...  for user { user.id } ...  function started')

    # Initialize shares_to_fill variable to avoid confusion
    shares_to_fill = shares
    print(f'running /process_sale() ...  for user { user.id } ...  shares is: { shares }')


    # We initialize a list of transaction changes to commit all at once once the loop below is complete
    updated_transactions = []
    print(f'running /process_sale() ...  for user { user.id } ...  updated_transactions list initialized')

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
                    type = transaction_type,
                    symbol = symbol,
                    shares = shares,
                    transaction_value_per_share = result['transaction_value_per_share'], 
                    transaction_value_total= -result['transaction_value_total']

                )
    db.session.add(new_transaction)
    print(f'running /sell ...  user.cash before deducting transaction_value_total is: { user.cash } ')
    
    # Adjust cash and commit changes to DB
    user.cash = user.cash + result['transaction_value_total']
    print(f'running /sell ...  user.cash after deducting transaction_value_total is: { user.cash } ')        
    
    # Commit all the changes made via the loop and the creation of new_transaction
    db.session.commit()
    print(f'running /sell ...  new_transaction added to DB is: { new_transaction } and user.cash is: { user.cash }')


# Defines a class called portfolio, used for /index and /index_detail
class Portfolio:

    def __init__(self):
        self._portfolio_data = {}
        # Initialize variables not under [symbol]
        self.cash = 0
        self.portfolio_total_shares = 0
        self.portfolio_cost_basis_per_share = 0
        self.portfolio_cost_basis_ex_cash = 0
        self.portfolio_market_value_ex_cash_pre_tax = 0 
        self.portfolio_gain_or_loss_usd_ex_cash_pre_tax = 0
        self.portfolio_gain_or_loss_percent_ex_cash_pre_tax = 0 
        self.portfolio_cost_basis_incl_cash = 0
        self.portfolio_market_value_incl_cash_pre_tax = 0
        self.portfolio_gain_or_loss_usd_incl_cash_pre_tax = 0
        self.portfolio_gain_or_loss_percent_incl_cash_pre_tax = 0
    
    # Adds the symbol to portfolio
    def add_symbol(self, symbol, data):
        self._portfolio_data[symbol] = data

    # Adds symbol-level data
    def get_symbol_data(self, symbol):
        return self._portfolio_data.get(symbol, None)


# Creates an item of the portfolio class and populates it
def process_user_transactions(user):
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  function started')
    
    # Create an instance of the Portfolio class
    portfolio = Portfolio()
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  object created')

    # Initiate tax rates and whether cap loss offset is turned on
    tax_rate_STCG = user.tax_rate_STCG
    tax_rate_LTCG = user.tax_rate_LTCG
    tax_loss_offsets = 1 if user.tax_loss_offsets == 'Yes' else 0

    # Query transactions DB to see if user has transactions
    transactions = db.session.query(Transaction).filter_by(user_id= user.id).all()
   
    if not transactions:
        return portfolio
    
    # Step 3.2: Loop for each transaction record in user_data
    for transaction in user.transactions:
        # Step 3.2.1: Establish symbol as the point on which rows will be consolidated
        symbol = transaction.symbol
        # Step 3.2.1: If a symbol is new to the portfolio, initialize it to the portfolio
        if symbol not in portfolio._portfolio_data:
            # Step 3.2.2: When a new symbol is encountered, set up a new row with the following columns
            portfolio.add_symbol(symbol, {
                'symbol': symbol,
                'shares': 0, 
                'cost_basis_per_share' : 0,
                'cost_basis_total' : 0,
                'market_value_per_share': company_data(symbol, fmp_key)['price'], 
                'market_value_total_pre_tax': 0,
                'gain_or_loss_usd_pre_tax': 0,
                'gain_or_loss_percent_pre_tax': 0,
                'capital_gains_ST': 0,
                'capital_gains_T': 0,
                'market_value_total_post_tax': 0,
                'gain_or_loss_usd_post_tax': 0,
                'gain_or_loss_percent_post_tax': 0,
            })
        
        # Attach the new data fields listed above to portfolio.symbol
        symbol_data = portfolio.get_symbol_data(symbol)
        
        # Step 3.2.2: Populate the fields for that txn
        if transaction.type == 'BOT':
            symbol_data['shares'] += transaction.shares
            symbol_data['cost_basis_total'] += transaction.transaction_value_total
        else:
            symbol_data['shares'] -= transaction.shares
            symbol_data['cost_basis_total'] += transaction.transaction_value_total

    # Step 3.3: Fill in columns not completed in the loop
    for symbol, symbol_data in portfolio._portfolio_data.items():
        try:                
            symbol_data['cost_basis_per_share'] = symbol_data['cost_basis_total'] / symbol_data['shares'] 
            #symbol_data['market_value_per_share'] = company_data(symbol, fmp_key)['price']
            symbol_data['market_value_total_pre_tax'] = symbol_data['shares'] * symbol_data['market_value_per_share']
            symbol_data['gain_or_loss_usd_pre_tax'] = symbol_data['market_value_total_pre_tax'] - symbol_data['cost_basis_total']
            symbol_data['gain_or_loss_percent_pre_tax'] = symbol_data['gain_or_loss_usd_pre_tax'] / symbol_data['cost_basis_total']

        except Exception as e:
            print(f'running /process_user_transactions(user) ...  Error 3.3: Error fetching price for {symbol}: {e}')

    # Step 3.4: Pull cash from the customers table
    portfolio.cash = user.cash if user.cash else 0
    print(f'running /process_user_transactions(user) ...  portfolio.cash is: { portfolio.cash }')

    # Step 3.5: Derive total portfolio cost basis, market value, and returns, all ex cash.
    for symbol, symbol_data in portfolio._portfolio_data.items():
        portfolio.portfolio_total_shares += symbol_data['shares']
        portfolio.portfolio_cost_basis_ex_cash += symbol_data['cost_basis_total']
        portfolio.portfolio_market_value_ex_cash_pre_tax += symbol_data['market_value_total_pre_tax']

    portfolio.portfolio_cost_basis_per_share += portfolio.portfolio_cost_basis_ex_cash / portfolio.portfolio_total_shares
    portfolio.portfolio_gain_or_loss_usd_ex_cash_pre_tax = portfolio.portfolio_market_value_ex_cash_pre_tax - portfolio.portfolio_cost_basis_ex_cash
    portfolio.portfolio_gain_or_loss_percent_ex_cash_pre_tax = portfolio.portfolio_gain_or_loss_usd_ex_cash_pre_tax / portfolio.portfolio_cost_basis_ex_cash
    print(f'running /process_user_transactions(user) ...  for user { user.id } ... portfolio.portfolio_cost_basis_ex_cash is: { portfolio.portfolio_cost_basis_ex_cash }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_market_value_ex_cash_pre_tax is: { portfolio.portfolio_market_value_ex_cash_pre_tax }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_gain_or_loss_usd_ex_cash_pre_tax is: { portfolio.portfolio_gain_or_loss_usd_ex_cash_pre_tax }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_gain_or_loss_percent_ex_cash_pre_tax is: { portfolio.portfolio_gain_or_loss_percent_ex_cash_pre_tax }')


    # Step 3.5: Derive total portfolio cost basis, market value, and returns, all incl cash.
    portfolio.portfolio_cost_basis_incl_cash = portfolio.portfolio_cost_basis_ex_cash + portfolio.cash
    portfolio.portfolio_market_value_incl_cash_pre_tax = portfolio.portfolio_market_value_ex_cash_pre_tax + portfolio.cash
    portfolio.portfolio_gain_or_loss_usd_incl_cash_pre_tax = portfolio.portfolio_market_value_incl_cash_pre_tax - portfolio.portfolio_cost_basis_incl_cash
    portfolio.portfolio_gain_or_loss_percent_incl_cash_pre_tax = portfolio.portfolio_gain_or_loss_usd_incl_cash_pre_tax / portfolio.portfolio_cost_basis_incl_cash
    print(f'running /process_user_transactions(user) ...  for user { user.id } ... portfolio.portfolio_cost_basis_incl_cash is: { portfolio.portfolio_cost_basis_incl_cash }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_market_value_incl_cash_pre_tax is: { portfolio.portfolio_market_value_incl_cash_pre_tax }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_gain_or_loss_usd_incl_cash_pre_tax is: { portfolio.portfolio_gain_or_loss_usd_incl_cash_pre_tax }')
    print(f'running /process_user_transactions(user) ...  for user { user.id } ...  portfolio.portfolio_gain_or_loss_percent_incl_cash_pre_tax is: { portfolio.portfolio_gain_or_loss_percent_incl_cash_pre_tax }')

    # return the portfolio object
    return portfolio


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