from Custom_FlaskWtf_Filters_and_Validators.validators_generic import pw_strength, pw_req_length, pw_req_letter, pw_req_num, pw_req_symbol, user_input_allowed_symbols
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_talisman import Talisman
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf.csrf import CSRFProtect, generate_csrf
from forms.forms import BuyForm, LoginForm, PasswordChangeForm, PasswordResetRequestForm, PasswordResetRequestNewForm, ProfileForm, QuoteForm, RegisterForm, SellForm
from helpers import apology, generate_nonce, generate_unique_token, login_required, lookup, timestamp_SG, usd, verify_unique_token
import logging
from logging.handlers import RotatingFileHandler
import os
import re
from sqlalchemy import func
import sys
import time
from urllib.parse import unquote
from werkzeug.security import check_password_hash, generate_password_hash


# Must declare this before app initialization to avoid circular import.
db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()
talisman = Talisman()
load_dotenv()

def create_app(config_name=None):    
    app = Flask(__name__)

    # Set app mode according to setting in .env
    if config_name == 'testing':    
        from configs.config_testing import TestingConfig
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        from configs.config_prod import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from configs.config_dev import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Set up logging to file
    if app.config.get('LOG_TO_FILE', False):
        file_handler = RotatingFileHandler(app.config.get('LOG_FILE_PATH'), maxBytes=10000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        app.logger.addHandler(file_handler)

    # Set up logging to console
    if app.config.get('LOG_TO_CONSOLE', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)

    # Custom filter
    app.jinja_env.filters['usd'] = usd

    # Enable flask-migrate (allows db changes via models.py)
    migrate = Migrate(app, db)

    # For flask-wtf generalized filters and validator, only append to sys.path if the path is set
    sys.path.append(app.config.get('CUSTOM_FLASKWTF_PATH'))

    Session(app)
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    talisman.init_app(app, content_security_policy=app.config['CONTENT_SECURITY_POLICY'])

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    from models import Transaction, User
    
    with app.app_context():
        print(f'running setup... SQLAlchemy Engine URL is { db.engine.url }')
        db.create_all()
        print('running setup... db.create_all has run')
    
# ------------------------------------------------------------------------    

    @app.route("/")
    @login_required
    def index():
        print(f'running / ...  starting /  ')
        print(f'running / ... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running / ... session.get(user) is: { session.get("user", None) }')
        print(f'running / ... CSRF token is: { session.get("csrf_token", None) }')

        # Step 1: Pull user object based on session[user].
        user = db.session.query(User).filter_by(id = session.get('user')).scalar()

        # Step 2: Handle if no id (unlikely).
        if not user:
            print(f'running / ...  error 2.0: no user data found for session[user] of: { session["user"] }')
            session['temp_flash'] = 'Error 2.0: User not found. Please log in again.'
            return redirect(url_for('login'))
        print(f'running /...  user is: { user }')

        # Step 3: Construct User's portfolio, w/ a row for each stock owned and the following cols:
        # (a) ticker (b) current price per shr (c) total shrs owned (d) mkt val. of shrs owned
        # Step 3.1: Initialize the dict
        portfolio = {}
        # Step 3.2: Loop for each transaction record in user_data
        for transaction in user.transactions:
            symbol = transaction.symbol
            # Step 3.2.1: If a symbol is new to the portfolio, initialize it to the portfolio
            if transaction.symbol not in portfolio:
                portfolio[symbol] = {
                    'symbol': symbol,
                    'summed_txn_shares': 0, 
                    'txn_shr_price': transaction.txn_shr_price, 
                    'summed_txn_value': 0
                }
            # Step 3.2.2: Populate the fields for that txn
            portfolio[symbol]['summed_txn_shares'] += transaction.txn_shrs
            portfolio[symbol]['summed_txn_value'] += transaction.txn_value
        
        # Recreates portfolio, including symbols only if the corresponding summed_txn_value data != 0    
        portfolio = {symbol: data for symbol, data in portfolio.items() if data['summed_txn_value'] != 0}
        print(f'running /...  finished populating portfolio, which is: { portfolio }')

        # Step 3.3: Append the mkt price for each stock in portfolio
        for symbol in portfolio:
            try:
                # For that row (stock), append a field called "current price" which looks up the symbol and retrieves the price, setting that to "current price"
                portfolio[symbol]['current_price'] = lookup(symbol)['price']
                print(f'running /...  portfolio[symbol][current_price] for symbol: { symbol } is= { portfolio[symbol]["current_price"] }')
            except Exception as e:
                print(f'running /...  Error 3.3: Error fetching price for {symbol}: {e}')
                portfolio[symbol]['current_price'] = 0

        # Step 3.4: Pull cash from the customers table
        if not user.cash:
            print(f'running /...  cash is 0')
            cash = 0
        else:
            # Convert that value to a real number
            cash = user.cash
            print(f'running /...  cash is: { cash }')

        # Step 3.5: Get the value of all share holdings.
        total_shares_value = 0        
        for symbol in portfolio:
            total_shares_value = total_shares_value + portfolio[symbol]['summed_txn_value']
            print(f'running /...  total_shares_value for symbol: { symbol } is: { total_shares_value }')
        print(f'running /...  total_shares_value overall is: { total_shares_value }')

        # Step 3.6: Calculate total portfolio value (cash + total share holdings).
        total_portfolio = total_shares_value + cash
        print(f'running /...  total_portfolio is: { total_portfolio }')

        # Step 3.7: Pass username into a variable
        username = user.username
        print(f'running /...  username is: { username }')

        # Step 3.8: Render index.html and pass in portfolio, cash, total_portfolio, username
        return render_template(
            "index.html", portfolio=portfolio, cash=cash, total_portfolio=total_portfolio, username=username
        )

# ---------------------------------------------------------------------
    
    @app.route("/buy", methods=["GET", "POST"])
    @login_required
    def buy():
        print(f'running /buy ...  starting /buy ')
        print(f'running /buy... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /buy ... session.get(user) is: { session.get("user", None) }')
        print(f'running /buy ... CSRF token is: { session.get("csrf_token", None) }')

        form = BuyForm()

        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 1.1.1: Pull in the user inputs from buy.html
                symbol = form.symbol.data
                shares = form.shares.data
                print(f'running /buy ...  symbol is: { symbol } ')
                print(f'running /buy ...  shares is: { shares } ')

                # Step 1.1.2: Check if symbol is a valid ticker. If yes, store data in symbol_data.
                if lookup(symbol):
                    symbol_data = lookup(symbol)
                else:
                    print(f'running /buy ... user-entered symbol is not valid: { symbol }. Flashing message and returning user to /buy.')
                    flash('Error: Invalid symbol')
                    return render_template('buy.html', form=form)

                # Step 1.1.3: Store the txn data
                txn_price_per_share = symbol_data["price"]
                txn_total_value = shares * txn_price_per_share
                
                # Step 1.1.4: Pull the user data (needed for cash balance)
                try:
                    user = db.session.query(User).filter_by(id = session.get('user')).scalar()
                    if txn_total_value > user.cash:
                        print(f'running /buy... Error 1.1.4 (insufficient cash) txn_total_value is: { txn_total_value } and user.cash is only: { user.cash }')
                        flash('Error: Insufficient cash to complete transaction')
                        return render_template('buy.html', form=form) 
                    print(f'running /buy... txn_total_value is: { txn_total_value } and user.cash is: { user.cash }')
                except ValueError as e:
                    print(f'running /buy... Error 1.1.4 (user not found in DB). Redirecting to /login.')
                    session['temp_flash'] = 'Error: Must log in.'
                    return redirect(url_for('login'))
                
                # Step 1.1.5: Update database
                                # Add new entry into the transaction table to represent the share purchase.
                new_transaction = Transaction(
                    user_id=user.id, 
                    txn_type='BOT', 
                    symbol=symbol, 
                    txn_shrs=shares, 
                    txn_shr_price=txn_price_per_share, 
                    txn_value=txn_total_value
                )
                db.session.add(new_transaction)
                user.cash -= txn_total_value
                db.session.commit()

                # Step 1.1.6: Flash success message and redirect to /
                print(f'running /buy... purchase successful, redirecting to / ')
                flash("Share purchase processed successfully!")
                time.sleep(1)
                return redirect(url_for('index'))

            # Step 1.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /buy ... Error 1.2 (form validation errors), flashing message and redirecting user to /buy')    
                for field, errors in form.errors.items():
                    print(f"Running /buy ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /buy ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('buy.html', form=form)

        # Step 2: User arrived via GET
        else:
            print(f'Running /buy ... user arrived via GET')
            return render_template('buy.html', form=form)
            """response = make_response(render_template('login.html', form=form nonce=nonce))
            print(f'response.headers is: {response.headers}')
            return response"""
                
# -----------------------------------------------------------------------
    
    @app.route('/check_email_registered', methods=['GET', 'POST'])
    
    def check_email_registered_route():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')
        return check_email_registered(user_input, False)

    # Returns True if user input is a registered email address.
    def check_email_registered(user_input, is_internal_call=False):
        user = db.session.query(User).filter_by(email=user_input).scalar()
        if user:
            print(f'running /check_email_registered... user_input is a registered email: { user_input }')
            return 'True' if not is_internal_call else True
        else:
            print(f'running /check_email_registered... user_input is not a registered email: { user_input }')
            return 'False' if not is_internal_call else False

# -----------------------------------------------------------------------

    @app.route('/check_valid_symbol', methods=['POST'])
    
    # Function returns True if user entry is a valid symbol
    def check_valid_symbol(user_input):
        print(f'running /check_valid_symbol... user_input is: { user_input }')    
        if lookup(user_input) != None:
            print(f'running /check_valid_symbol... user_input is a valid stock symbol: { user_input }')
            return lookup(user_input)
        else:
            print(f'running /check_valid_symbol... user_input is not a valid stock symbol: { user_input }')
        
# -----------------------------------------------------------------------

    @app.route('/check_valid_password', methods=['GET', 'POST'])
    def check_valid_password():
        # Step 1: Pull in data passed in by JavaScript
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')
        
        # Step 2: Initialize checks_passed array
        checks_passed = []
        print(f'running /check_valid_password... initialized checks_passed array ')
        
        # Step 3: Start performing checks, adding the name of each check passed to the checks_passed array.
        if len(password) >= pw_req_length:
                checks_passed.append('pw_reg_length')
                print(f'running /check_valid_password... appended pw_reg_length to checks_passed array ')
        if len(re.findall(r'[a-zA-Z]', password)) >= pw_req_letter:
                checks_passed.append('pw_req_letter')
                print(f'running /check_valid_password... appended pw_req_letter to checks_passed array ')
        if len(re.findall(r'[0-9]', password)) >= pw_req_num:
                checks_passed.append('pw_req_num')
                print(f'running /check_valid_password... appended pw_req_num to checks_passed array ')
        if len(re.findall(r'[^a-zA-Z0-9]', password)) >= pw_req_symbol:
                checks_passed.append('pw_req_symbol')
                print(f'running /check_valid_password... appended pw_req_symbol to checks_passed array ')
        print(f'running /check_valid_password... checks_passed array contains: { checks_passed }')

        # Step 4: Ensure password and confirmation match
        if password == password_confirmation:
            confirmation_match = True
        else:
            confirmation_match = False
        print(f'running /check_valid_password... confirmation_match is: { confirmation_match }')

        # Step 5: Pass the checks_passed array and confirmation_match back to JavaScript
        print(f'running /check_valid_password... check finished, passing data back to JavaScript')
        return jsonify({'checks_passed': checks_passed, 'confirmation_match': confirmation_match} )

# -----------------------------------------------------------------------

    @app.route('/check_username_registered', methods=['GET', 'POST'])
    def check_username_registered_route():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')
        return check_username_registered(user_input, False)

    # Returns True if user input is a registered username.
    def check_username_registered(user_input, is_internal_call=False):
        user = db.session.query(User).filter_by(username=user_input).scalar()
        if user:
            print(f'running /check_username_registered... user_input is a registered username: { user_input }')
            return 'True' if not is_internal_call else True
        else:
            print(f'running /check_username_registered... user_input is not a registered username: { user_input }')
            return 'False' if not is_internal_call else False
           
# -----------------------------------------------------------------------

    @app.route('/csp-violation-report', methods=['POST'])
    @csrf.exempt
    def csp_report():
        if request.content_type in ['application/csp-report', 'application/json']:
            report = request.get_json(force=True)
            # Process the report
            # Log the report for debugging
            print(f"CSP Report: {report}")
        else:
            # Handle unexpected content-type
            print(f"Unexpected Content-Type: {request.content_type}")
            return 'Unsupported Media Type', 415
        return '', 204

# -----------------------------------------------------------------------

    @app.route("/history")
    @login_required
    def history():
        print('running /history... route started ')

        # Pull the symbol and the total shares owned from the transactions database
        history = db.session.query(Transaction).filter_by(user_id = session['user']).order_by(Transaction.txn_date.desc()).all()
        print(f'running /history... history is: { history } ')
        
        for transaction in history:
            print(f'running history... transaction timestamp is: { transaction.txn_date }')

        # Render index.html and pass in the values in the portfolio pull and for cash.
        return render_template("history.html", history=history)

# -----------------------------------------------------------------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        print(f'running /login ...  starting /login ')
        print(f'running /login... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /login ... CSRF token is: { session.get("csrf_token", None) }')

        nonce = generate_nonce()
        print(f'running /login ... nonce is:{nonce}')
        form = LoginForm()

        # Step 1: Store CSRF token and flash temp message, if any.
        temp_flash = session.get('temp_flash', None)
        csrf_token = session.get('csrf_token', None)
        session.clear()
        if temp_flash:
            flash(temp_flash)
        if csrf_token:
            session['csrf_token'] = csrf_token

        # Step 2: Handle submission via post
        if request.method == 'POST':
            
            # Step 2.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User submitted via post and user input passed form validation')
                
                # Step 2.1.1: Pull in email and password from form and pull user item from DB.
                email = form.email.data
                password = form.password.data
                print(f'running /login... user-submitted email is: { email }')
                
                user = db.session.query(User).filter_by(email = email).scalar()
                print(f'running /login... queried database on user-entered email, result is: { user }')
                
                # Step 2.1.2: Validate that user-submitted password is correct
                if not check_password_hash(user.hash, form.password.data):
                    print(f'running /login... error 2.1.2 (invalid password), flashing message and redirecting user to /login')
                    session['temp_flash'] = 'Error: Invalid username and/or password. If you have not yet registered, please click the link below. If you have recently requested a password reset, check your email inbox and spam folders.'
                    time.sleep(1)
                    return redirect('/login')

                # Step 2.1.3: Validate that user account is confirmed
                if user.confirmed != 'Yes':
                    print(f'running /login... error 2.1.3 (user.confirmed != yes), flashing message and redirecting user to /login')
                    session['temp_flash'] = 'Error: This account has not yet been confirmed. Please check your email inbox and spam folder for email instructions regarding how to confirm your registration. You may re-register below, if needed.'
                    time.sleep(1)
                    return redirect('/login')

                # Step 2.1.4: Remember which user has logged in
                session['user'] = user.id
                print(f'running /login... session[user_id] is: { session["user"] }')

                # Step 2.1.5: Redirect user to home page
                print(f'running /login... redirecting to /index.  User is: { session }')
                print(f'running /login ... session.get(user) is: { session.get("user") }')
                return redirect(url_for('index'))
            
            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /login ... Error 2.2, flashing message and redirecting user to /login')
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('login.html', form=form)
        
        # Step 3: User arrived via GET
        print(f'running /login ... user arrived via GET')
        response = make_response(render_template('login.html', form=form, nonce=nonce))
        print(f'running /login... response.headers is: {response.headers}')
        return response
                  
# --------------------------------------------------------------------------------

    @app.route("/logout")
    def logout():
        """Log user out"""

        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect(url_for('index'))

# -----------------------------------------------------------------------

    @app.route("/password_change", methods=["GET", "POST"])
    @login_required
    def password_change():
        print(f'running /password_change... route started ')
        print(f'running /password_change... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /password_change ... session.get(user) is: { session.get("user", None) }')
        print(f'running /password_change ... CSRF token is: { session.get("csrf_token", None) }')

        form = PasswordChangeForm()
        
        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 1.1.1: Pull in the user inputs from password_change.html
                try:
                    user = db.session.query(User).filter_by(email = form.email.data).scalar()
                    print(f'running /password_change ... User object retrieved from DB via user-provided email is: { user }')
                    # Step 1.1.1.1 If user-entered email and password don't match, flash error and render password_change.html
                    if not check_password_hash(user.hash, form.password_old.data):
                        print(f'running /password_change ... Error 1.1.1.1 (email + password mismatch) user entered email of: { form.email.data } does not correspond with the password entered.')
                        flash('Error: invalid entry for email address and/or current password. Please check your input and try again.')
                        return render_template('password_change.html', form=form)

                    # Step 1.1.1.2: Hash the new password and update the DB.
                    user.hash = generate_password_hash(form.password.data)
                    db.session.commit()
                    print(f'running /password_change ... updated user.hash in DB.')

                    # Step 1.1.1.3: Flash success msg redirect to index.
                    print(f'running /password_change ...  successfully changed user password, redirecting to / ')
                    flash('Password password change successful!')
                    time.sleep(1)
                    return redirect(url_for('index'))
                
                # Step 1.1.2: If can't pull in email address and password from DB, flash error and render password_change.html
                except Exception as e:
                    print(f'running /password_change ...  Error 1.1.2 (email not registered) User-submitted email address not in DB. Flashing error and rendering password_change.html')
                    flash('Error: invalid entry for email address and/or current password. Please check your input and try again.')
                    return render_template('password_change.html', form=form)
            
            # Step 1.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /password_change ... Error 1.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    print(f"Running /password_change ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /password_change ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('password_change.html', form=form)
        
        # Step 2: User arrived via GET
        else:
            print(f'Running /password_change ... user arrived via GET')
            return render_template('password_change.html', form=form)
            
# ---------------------------------------------------------------------------------
    
    @app.route("/password_reset_request", methods=["GET", "POST"])
    def password_reset_request():
        print(f'running /password_reset_request... route started ')
        print(f'running /password_reset_request... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /password_reset_request ... CSRF token is: { session.get("csrf_token", None) }')

        form = PasswordResetRequestForm()

        # Step 1: Store CSRF token and flash temp message, if any.
        temp_flash = session.get('temp_flash', None)
        csrf_token = session.get('csrf_token', None)
        session.clear()
        if temp_flash:
            flash(temp_flash)
        if csrf_token:
            session['csrf_token'] = csrf_token

        
        # Step 2: Handle submission via post
        if request.method == 'POST':
        
            # Step 2.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_reset_request ... User submitted via post and user input passed form validation')

                # Step 2.1.1: Pull in the user inputs from form
                user = db.session.query(User).filter_by(email = form.email.data).scalar()

                try:
                    print(f'running /password_reset_request ... User object retrieved from DB via user-provided email is: { user }. The corresponding user.id is: { user.id } and the corresponding user.email is: { user.email }')
                    
                    # Step 2.1.1.1: Generate token
                    token = generate_unique_token(user.id, app.config['SECRET_KEY'])
                    print(f'running /password_reset_request ... token generated')

                    # Step 2.1.1.2: Formulate email
                    token_age_max_minutes = int(int(app.config['MAX_TOKEN_AGE_SECONDS']) / 60)
                    username = user.username
                    sender = 'info@mattmcdonnell.net'
                    recipients = [user.email]
                    subject = 'Password reset from MyFinance50'
                    url = url_for('password_reset_request_new', token=token, _external=True)
                    body = f'''Dear { username }: to reset your password, please visit the following link within the next { token_age_max_minutes } minutes: { url }

    If you did not make this request, you may ignore it.

    Thank you,
    Team MyFinance50'''

                    # Step 2.1.1.3: Send email.
                    msg = Message(subject=subject, body=body, sender=sender, recipients=recipients)
                    mail.send(msg)
                    print(f'Running /password_reset_request... reset email sent to email address: { user.email }.')

                    # Step 2.1.1.4: Flash success msg redirect to login.
                    print(f'running /password_reset_request ...  successfully changed user password, redirecting to / ')
                    session['temp_flash'] = 'Reset email sent. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
                
                # Step 2.1.2: If can't send email (likely due to user entering an unregistered email address), still flash
                # email sent message and redirect to login. This is done to reduce chances of brute force attack.
                except Exception as e:
                    print(f'running /password_reset_request ...  Error 1.1.2 (user-submitted email not registered) Flashing sent email msg and redirecting to /login')
                    session['temp_flash'] = 'Reset email sent. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
            
            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /password_reset_request ... Error 1.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    print(f"Running /password_reset_request ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /password_reset_request ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('password_reset_request.html', form=form)
        
        # Step 3: User arrived via GET
        else:
            print(f'Running /password_reset_request ... user arrived via GET')
            return render_template('password_reset_request.html', form=form)
            
# ---------------------------------------------------------------------------------
    
    @app.route('/password_reset_request_new/<token>', methods=['GET', 'POST'])
    def password_reset_request_new(token):
        print(f'running /password_reset_request_new... route started ')
        print(f'running /password_reset_request_new... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /password_reset_request_new ... CSRF token is: { session.get("csrf_token", None) }')
        
        # Step 1: Take the token and decode it
        decoded_token = unquote(token)
        user = verify_unique_token(decoded_token, app.config['SECRET_KEY'], int(os.getenv('MAX_TOKEN_AGE_SECONDS')))
        
        # Step 2: If token is invalid, flash error msg and redirect user to login
        if not user:
            print(f'Running /password_reset_request_new ... no user found.')
            session['temp_flash'] = 'Error: Invalid or expired reset link. Please login or re-request your password reset.'    
            return redirect(url_for('login'))
        
        # Step 3: If token is valid, set user.id to user['user_id'] property from token
        user = user
        print(f'Running /pw_reset_new ... user is: { user }.')

        form = PasswordResetRequestNewForm()
        
        # Step 4: Handle submission via post
        if request.method == 'POST':
        
            # Step 4.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_reset_request_new ... User submitted via post and user input passed form validation')

                # Step 4.1.1: Pull in the user inputs from form
                user = db.session.query(User).filter_by(id = user).scalar()
                print(f'running /password_reset_request_new ... user object extracted from token is: { user }')
                print(f'running /password_reset_request_new ... user.hash is: { user.hash }')
                print(f'running /password_reset_request_new ... form.password.data is: { form.password.data }')

                try:                    
                    # Step 4.1.1.1: Check to ensure new password does not match existing password
                    if check_password_hash(user.hash, form.password.data):
                        print(f'running /password_reset_request_new ... Error 4.1.1.1 (new password matches existing). Flashing error and rendering password_reset_request_new.html')
                        flash('Error: new password cannot match old password. Please try again.')
                        return render_template('password_reset_request_new.html', 
                                token=token,
                                form=form,
                                pw_req_length=pw_req_length, 
                                pw_req_letter=pw_req_letter, 
                                pw_req_num=pw_req_num, 
                                pw_req_symbol=pw_req_symbol,
                                user_input_allowed_symbols=user_input_allowed_symbols)    
                    
                    # Step 4.1.1.2: Update DB with new password
                    user.hash = generate_password_hash(form.password.data)
                    db.session.commit()
                    print(f'running /password_reset_request_new ... password reset for user { user } entered into DB')

                    # Step 4.1.1.3: Flash success message and redirect user to index
                    print(f'running /password_reset_request_new ... completed route for { user }. Flashing success message and redirecting to /index')
                    session['temp_flash'] = 'Password reset successful!'
                    time.sleep(1)
                    return redirect(url_for('index'))
                
                # Step 4.1.2: If can't update password (likely due to no user object resulting from
                # use of an invalid token) flash error msg and redirect to login.
                except Exception as e:
                    print(f'running /password_reset_request_new ...  Error 4.1.2 (unable to update DB) Flashing error msg and redirecting to /login')
                    session['temp_flash'] = 'Error: Invalid token. Please login or repeat your password reset request via the link below.'
                    time.sleep(1)
                    return redirect(url_for('login'))
            
            # Step 4.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /password_reset_request_new ... Error 4.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    print(f"Running /password_reset_request_new ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /password_reset_request_new ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('password_reset_request_new.html', 
                                token=token,
                                form=form,
                                pw_req_length=pw_req_length, 
                                pw_req_letter=pw_req_letter, 
                                pw_req_num=pw_req_num, 
                                pw_req_symbol=pw_req_symbol,
                                user_input_allowed_symbols=user_input_allowed_symbols)
        
        # Step 5: User arrived via GET
        else:
            print(f'Running /password_reset_request_new ... user arrived via GET')
            return render_template('password_reset_request_new.html', 
                                token=token,
                                form=form,
                                pw_req_length=pw_req_length, 
                                pw_req_letter=pw_req_letter, 
                                pw_req_num=pw_req_num, 
                                pw_req_symbol=pw_req_symbol,
                                user_input_allowed_symbols=user_input_allowed_symbols)
            
# ---------------------------------------------------------------------------------

    @app.route("/profile", methods=["GET", "POST"])
    @login_required
    def profile():
        print(f'running /profile ...  starting /profile  ')
        print(f'running /profile ... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /profile ... session.get(user) is: { session.get("user", None) }')
        print(f'running /profile ... CSRF token is: { session.get("csrf_token", None) }')

        form = ProfileForm()

        # Step 1: Pull user object based on session[user].
        user = db.session.query(User).filter_by(id = session.get('user')).scalar()

        # Step 2: Handle submission via post
        if request.method == 'POST':

            # Step 2.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 2.1.1: Pull in data from form
                try:
                    # Step 2.1.1.1: Check if (a) there is user entry for username and if so, (b) whether it represents an already-taken username.
                    if form.username.data and check_username_registered(form.username.data) == True:
                        print(f'running /profile ... Error 2.1.1.1 (username already registered). User input for username: { form.username.data } is already registered. Flash error and render profile.html')
                        flash(f'Error: Username: { form.username.data } is already registered. Please try another username.')
                        return render_template('profile.html', form=form )
                                        
                    # Step 2.1.1.2: Update user data as needed
                    if form.name_first.data:
                        user.name_first = form.name_first.data
                        print(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.name_last.data:
                        user.name_last = form.name_last.data
                        print(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.username.data:
                        user.username = form.username.data
                        print(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.accounting_method.data != user.accounting_method:
                        user.accounting_method = form.accounting_method.data
                        print(f'running /profile ... user.accounting_method updated to: { form.accounting_method.data }')
                    if form.tax_loss_offsets.data != user.tax_loss_offsets:
                        user.tax_loss_offsets = form.tax_loss_offsets.data
                        print(f'running /profile ... user.tax_loss_offsets updated to: { form.tax_loss_offsets.data }')
                    if form.tax_rate_STCG.data != user.tax_rate_STCG:
                        user.tax_rate_STCG = form.tax_rate_STCG.data
                        print(f'running /profile ... user.tax_rate_STCG updated to: { form.tax_rate_STCG.data }')
                    if form.tax_rate_LTCG.data != user.tax_rate_LTCG:
                        user.tax_rate_LTCG = form.tax_rate_LTCG.data
                        print(f'running /profile ... user.tax_rate_LTCG updated to: { form.tax_rate_LTCG.data }')
                    db.session.commit()
                    print(f'running /profile ... successfully updated database')

                    # Step 2.1.1.3: Query DB to get updated data
                    user = db.session.query(User).filter_by(id=session.get('user')).scalar()
                    print(f'running /profile ... refreshed user object for user: { user }')
                    name_full = user.name_first+" "+user.name_last
                    form.name_full.data = name_full
                    form.username_old.data = user.username
                    form.email.data = user.email
                    form.created.data = user.created
                    form.accounting_method.data = user.accounting_method
                    form.tax_loss_offsets.data = user.tax_loss_offsets
                    
                    form.tax_rate_STCG.data = user.tax_rate_STCG
                    print(f'running /profile ... new value for user.tax_rate_STCG is: { user.tax_rate_STCG }')
                    
                    form.tax_rate_LTCG.data = user.tax_rate_LTCG
                    
                    # Step 2.1.1.4: Flash success message and render profile.html
                    print(f'running /profile ... DB successfully updated with user changes. Flashing success message and rendering profile.html')
                    flash('Profile updated successfully!')
                    time.sleep(1)
                    return render_template('profile.html', form=form )
                
                # Step 2.1.2: If can't pull in data from form, flash error and render profile.html
                except Exception as e:
                    print(f'running /profile ...  Error 2.1.2 (unable to update DB): { e }. Flashing error and rendering profile.html')
                    flash('Error: invalid entry. Please check your input and try again.')
                    return render_template('profile.html', form=form )
            
            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /profile ... Error 2.2 (form validation errors), flashing message and redirecting user to /profile')    
                for field, errors in form.errors.items():
                    print(f"Running /profile ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /profile ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('profile.html', form=form )
        
        # Step 2: User arrived via GET
        else:
            name_full = user.name_first+" "+user.name_last
            form.name_full.data = name_full
            form.username_old.data = user.username
            form.email.data = user.email
            form.created.data = user.created
            form.accounting_method.data = user.accounting_method
            form.tax_loss_offsets.data = user.tax_loss_offsets
            form.tax_rate_STCG.data = user.tax_rate_STCG
            form.tax_rate_LTCG.data = user.tax_rate_LTCG
            print(f'running /password_change ... on loading page, tax_rate_STCG is: { user.tax_rate_STCG } ')
            #print(f'running /password_change ... on loading page, tax_rate_STCG_value is: { form.tax_rate_STCG_value.data } ')
            print(f'running /password_change ... on loading page, tax_rate_LTCG is: { user.tax_rate_LTCG } ')
            #print(f'running /password_change ... on loading page, tax_rate_LTCG_value is: { form.tax_rate_LTCG_value.data } ')

                
            print(f'Running /profile ... user arrived via GET')
            return render_template('profile.html', form=form)

# --------------------------------------------------------------------------

    @app.route("/quote", methods=["GET", "POST"])
    @login_required
    def quote():
        print(f'running /quote... route started ')
        print(f'running /quote... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /quote ... session.get(user) is: { session.get("user", None) }')
        print(f'running /quote ... CSRF token is: { session.get("csrf_token", None) }')

        form = QuoteForm()

        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 1.1.1: Pull in the user inputs from quote.html
                symbol = form.symbol.data

                # Step 1.1.2: Pull quote, returning error message if symbol is invalid
                try:
                    name = check_valid_symbol(symbol)['name']
                    price = check_valid_symbol(symbol)['price']
                    print(f'running /quote... name is: { name }')
                    print(f'running /quote... price is: { price }')
                    print(f'running /quote... successfully pulled quote. Flashing message and directing user to quoted.html')
                    return render_template("quoted.html", symbol=symbol, name=name, price=price)
                except TypeError as e:
                    print(f'running /quote... user submitted with invalid symbol: { symbol }. Flashing error and returning user to /quote.')
                    flash('Error: Invalid stock symbol')
                    return render_template('quote.html', form=form)
            
            # Step 1.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /quote ... Error 1.2 (form validation errors), flashing message and redirecting user to /quote')    
                for field, errors in form.errors.items():
                    print(f"Running /quote ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /quote ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('quote.html', form=form)
        
        # Step 2: User arrived via GET
        else:
            print(f'Running /quote ... user arrived via GET')
            return render_template('quote.html', form=form)
            """response = make_response(render_template('login.html', form=form nonce=nonce))
            print(f'response.headers is: {response.headers}')
            return response"""
    
# ------------------------------------------------------------------------------
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        print(f'running /register ...  starting /register ')
        print(f'running /register... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /register ... CSRF token is: { session.get("csrf_token", None) }')

        form = RegisterForm()

        # Step 1: Store CSRF token and flash temp message, if any.
        temp_flash = session.get('temp_flash', None)
        csrf_token = session.get('csrf_token', None)
        session.clear()
        if temp_flash:
            flash(temp_flash)
        if csrf_token:
            session['csrf_token'] = csrf_token

        # Step 2: Handle submission via post
        if request.method == 'POST':

            # Step 2.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User submitted via post and user input passed form validation')
                
                # Step 2.1.1: Pull in email and password from form and pull user item from DB.
                name_first = form.name_first.data
                name_last = form.name_last.data
                username = form.username.data
                email = form.email.data
                password = form.password.data
                accounting_method = form.accounting_method.data
                tax_loss_offsets = form.tax_loss_offsets.data
                tax_rate_STCG = form.tax_rate_STCG.data
                tax_rate_LTCG = form.tax_rate_LTCG.data

                try:
                    print(f'running /register... user-submitted name_first is: { name_first }')
                    print(f'running /register... user-submitted name_last is: { name_last }')
                    print(f'running /register... user-submitted username is: { username }')
                    print(f'running /register... user-submitted email address is: { email }')
                    print(f'running /register... user-submitted accounting_method is: { accounting_method }')
                    print(f'running /register... user-submitted tax_loss_offsets is: { tax_loss_offsets }')
                    print(f'running /register... user-submitted tax_rate_STCG is: { tax_rate_STCG }')
                    print(f'running /register... user-submitted tax_rate_LTCG is: { tax_rate_LTCG }')
                    
            
                    # Step 2.1.1.1: Ensure username and email address are not already registered
                    if check_email_registered(email) == True or check_username_registered(username) == True:
                        print(f'Running /register ... Error 2.1.1.1   (email and/or username already registered), flashing message and redirecting user to /register')
                        session['temp_flash'] = 'Error: Email address and/or username is unavailable. If you already have an account, please log in. Otherwise, please amend your entries.'
                        time.sleep(1)
                        return render_template(
                            'register.html',
                            form=form,
                            pw_req_length=pw_req_length,
                            pw_req_letter=pw_req_letter,
                            pw_req_num=pw_req_num,
                            pw_req_symbol=pw_req_symbol,
                            user_input_allowed_symbols=user_input_allowed_symbols
                            )
                       
                    # Step 2.1.1.2: Input data to DB.
                    new_user = User(
                        name_first = name_first,
                        name_last = name_last,
                        email = email,
                        username = username, 
                        hash = generate_password_hash(password),
                        accounting_method = accounting_method,
                        tax_loss_offsets = tax_loss_offsets,
                        tax_rate_STCG = tax_rate_STCG,
                        tax_rate_LTCG = tax_rate_LTCG)
                    db.session.add(new_user)
                    db.session.commit()
                    print(f'running /register ... new_user added to DB w/ unconfirmed=0')

                    # Step 2.1.1.3: Query new user object from DB to get id.
                    user = db.session.query(User).filter_by(email = email).scalar()

                    # Step 2.1.1.3: Generate token
                    token = generate_unique_token(user.id, app.config['SECRET_KEY'])
                    print(f'running /register ... token generated')
                    print(f'running /register ... int(os.getenv(MAX_TOKEN_AGE_SECONDS) is: { int(os.getenv("MAX_TOKEN_AGE_SECONDS")) }')

                    # Step 2.1.1.4: Formulate email
                    token_age_max_minutes = int(int(os.getenv('MAX_TOKEN_AGE_SECONDS'))/60)
                    username = user.username
                    sender = 'info@mattmcdonnell.net'
                    recipients = [user.email]
                    subject = 'Confirm you registration with MyFinance50'
                    url = url_for('register_confirmation', token=token, _external=True)
                    body = f'''Dear { user.username }: to confirm your registration with MyFinance50, please visit the following link within the next { token_age_max_minutes } minutes: { url }

    If you did not make this request, you may ignore it.

    Thank you,
    Team MyFinance50'''

                    # Step 2.1.1.5: Send email.
                    msg = Message(subject=subject, body=body, sender=sender, recipients=recipients)
                    mail.send(msg)
                    print(f'Running /register... reset email sent to email address: { user.email }.')

                    # Step 2.1.1.6: Flash success msg redirect to login.
                    print(f'running /register ...  successfully registered user, redirecting to /login ')
                    session['temp_flash'] = 'To confirm your registration and log in, please follow the instructions sent to you by email. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
                
                # Step 2.1.2: If user entry symbol or shares is invalid, flash error and render sell.html
                except Exception as e:
                    print(f'running /register ...  Error 3.1.2 (unable to register user in DB and send email): {e}. Flashing error msg and rendering register.html ')
                    session['temp_flash'] = 'Error: Unable to send email. Please ensure you are using a valid email address.'
                    time.sleep(1)
                    return render_template(
                        'register.html',
                        form=form,
                        pw_req_length=pw_req_length,
                        pw_req_letter=pw_req_letter,
                        pw_req_num=pw_req_num,
                        pw_req_symbol=pw_req_symbol,
                        user_input_allowed_symbols=user_input_allowed_symbols
                        )

            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /register ... Error 2.2 (form validation errors), flashing message and redirecting user to /register')    
                for field, errors in form.errors.items():
                    print(f"Running /register ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /register ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template(
                        'register.html',
                        form=form,
                        pw_req_length=pw_req_length,
                        pw_req_letter=pw_req_letter,
                        pw_req_num=pw_req_num,
                        pw_req_symbol=pw_req_symbol,
                        user_input_allowed_symbols=user_input_allowed_symbols
                        )

        # Step 3: User arrived via GET
        else:
            print(f'Running /register ... user arrived via GET')
            return render_template(
                        'register.html',
                        form=form,
                        pw_req_length=pw_req_length,
                        pw_req_letter=pw_req_letter,
                        pw_req_num=pw_req_num,
                        pw_req_symbol=pw_req_symbol,
                        user_input_allowed_symbols=user_input_allowed_symbols
                        )
             
# --------------------------------------------------------------------------------

    @app.route('/register_confirmation/<token>', methods=['GET', 'POST'])
    def register_confirmation(token):
        print(f'running /register_confirmation ...  starting /register_confirmation ')
        print(f'running /register_confirmation... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /register_confirmation ... CSRF token is: { session.get("csrf_token", None) }')
        
        try:
            # Step 1: Take the token and decode it
            decoded_token = unquote(token)
            user = verify_unique_token(decoded_token, app.config['SECRET_KEY'], int(os.getenv('MAX_TOKEN_AGE_SECONDS')))
        
            # Step 2: If token is invalid, flash error msg and redirect user to register
            if not user:
                print(f'Running /register_confirmation ... no user found.')
                session['temp_flash'] = 'Error: Invalid or expired confirmation link. Please login or re-request your password reset.'    
                return redirect(url_for('register'))
        
            # Step 3: If token is valid, pull user object from DB
            user = db.session.query(User).filter_by(id = user).scalar()
            print(f'Running /register_confirmation ... user object is: { user }.')
            print(f'Running /register_confirmation ... user.confirmed is: { user.confirmed }.')

            # Step 4: If user is already confirmed, flash error and redirect to login
            if user.confirmed == 'No':
                user.confirmed = 'Yes'
                db.session.commit()
                print(f'Running /register_confirmation ... updated user: { user } to confirmed.')
            else:
                print(f'Running /register_confirmation ... Error 4 (user already confirmed). Flashing msg and redirecting to login.')
                session['temp_flash'] = 'Error: This account is already confirmed. Please log in.'
                time.sleep(1)
                return redirect(url_for('login'))
            

            # Step 5: Flash success message and return to index
            session['user'] = user.id
            print(f'Running /register_confirmation ... successfully updated confirmed for user object: { user } to: 1.')
            flash('Your registration is confirmed. Welcome to MyFinance50!')
            time.sleep(1)
            return redirect(url_for('index'))

        # Step 6: If token is invalid or DB update fails, flask error message and redirect to reset.html
        except Exception as e:
                print(f'running /register_confirmation ...  Error 3.1.2 (unable to register user in DB and send email): {e}. Flashing error msg and rendering register.html ')
                session['temp_flash'] = 'Error: Unable to send email. Please ensure you are using a valid email address.'
                time.sleep(1)
                return redirect(url_for('register'))
                        
# -------------------------------------------------------------------------------

    @app.route("/sell", methods=["GET", "POST"])
    @login_required
    def sell():
        print(f'running /sell ...  starting /sell ')
        print(f'running /sell... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /sell... session[user] is: { session["user"] }')
        
        form = SellForm()
        
        # Step 1: Populate the symbols dropdown in sell.html
        # Step 1.1: Call the list of stocks from the SQL database and convert to a list
        symbols = db.session.query(Transaction.symbol).filter(Transaction.user_id == session['user']).distinct().order_by(Transaction.symbol).all()
        symbols = [symbol[0] for symbol in symbols]
        print(f'running /sell... symbols is: { symbols }')
        
        # Step 1.2: Pass the aforementioned list of symbols to sell.html
        print(f'running /sell ...  user arrived via GET, displaying page ')
        form.symbol.choices = symbols

        
        # Step 2: Pull the user object, which will be used throughout the route
        user = db.session.query(User).filter_by(id = session['user']).scalar()

        # Step 3: Handle submission via post
        if request.method == 'POST':

            # Step 3.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                print(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 3.1.1: Pull in the user inputs from sell.html
                try:
                    # Step 3.1.1.1: Pull data from form
                    symbol = form.symbol.data
                    shares = form.shares.data
                    txn_shr_price = (lookup(symbol))['price']
                    txn_value = -shares * txn_shr_price
                    txn_shrs = shares * -1

                    # Step 3.1.1.2: Retrieve from DB the shares owned in the specified symbol
                    total_shares_owned = db.session.query(func.sum(Transaction.txn_shrs))\
                    .filter(Transaction.user_id == user.id, Transaction.symbol == symbol)\
                    .scalar()
                    print(f'running /sell ...  total shares of symbol: { symbol } is: { total_shares_owned } ')
                    
                    # Step 3.1.1.3: Check if user has enough shares to sell
                    if shares > total_shares_owned:
                        print(f'running /sell ...  Error 2.1.1.3 (insufficient shrs to sell): user requested to sell: { shares } shares, but user only owns: { total_shares_owned } in symbol: { symbol }')
                        flash(f'Error 3.1.1.3: Shares sold ({ shares }) cannot exceed shares owned ({ total_shares_owned }).')
                        return render_template('sell.html', form=form, symbols = symbols)

                    # Step 3.1.1.4: Create entry for the transaction in the DB.
                    new_transaction = Transaction(
                        user_id = session['user'],
                        txn_type = 'SLD',
                        symbol = symbol,
                        txn_shrs = txn_shrs,
                        txn_shr_price = txn_shr_price,
                        txn_value = txn_value
                    )
                    db.session.add(new_transaction)
                    
                    print(f'running /sell ...  user.cash before deducting txn_value is: { user.cash } ')
                    user.cash = user.cash - txn_value
                    print(f'running /sell ...  user.cash after deducting txn_value is: { user.cash } ')        
                    
                    db.session.commit()
                    print(f'running /sell ...  new_transaction added to DB is: { new_transaction } and user.cash is: { user.cash }')

                    # Step 3.1.1.5: Flash success message and redirect user to /.
                    print(f'running /sell ...  sale processed successfully. Redirecting user to / ')
                    flash("Share sale processed successfully!")
                    time.sleep(1)
                    return redirect(url_for('index'))

                # Step 3.1.2: If user entry symbol or shares is invalid, flash error and render sell.html
                except Exception as e:
                    print(f'running /sell ...  Error 3.1.2 (invalid entry for symbol and/or shares and/or ): User entry for symbol and/or shares was invalid. Error is: {e}')
                    flash(f'Error: Please enter a valid share symbol and positive number of shares not exceeding your current holdings.')
                    return render_template('sell.html', form=form, symbols = symbols)
            
            # Step 3.2: Handle submission via post + user input fails form validation
            else:
                print(f'Running /sell ... Error 3.2 (form validation errors), flashing message and redirecting user to /sell')    
                for field, errors in form.errors.items():
                    print(f"Running /sell ... erroring field is: {field}")
                    for error in errors:
                        print(f"Running /sell ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('sell.html', form=form, symbols = symbols)

        # Step 4: User arrived via GET
        else:
            print(f'Running /sell ... user arrived via GET')
            return render_template('sell.html', form=form, symbols = symbols)

# -------------------------------------------------------------------------------------

    return app

if __name__ == '__main__': 
    app.run()