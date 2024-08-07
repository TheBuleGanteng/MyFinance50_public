from Custom_FlaskWtf_Filters_and_Validators.validators_generic import pw_strength, pw_req_length, pw_req_letter, pw_req_num, pw_req_symbol, user_input_allowed_symbols
from extensions import db, csrf, talisman, load_dotenv  
from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, session, url_for
from forms.forms import BuyForm, FilterTransactionHistory, LoginForm, PasswordChangeForm, PasswordResetRequestForm, PasswordResetRequestNewForm, ProfileForm, QuoteForm, RegisterForm, SellForm
from helpers import apology, Babel, base64, build, check_password_hash, company_data, datetime, date_time, EmailMessage, fmp_key, format_decimal, func, generate_nonce, generate_password_hash, generate_unique_token, logging, login_required, Migrate, number_format, or_, os, percentage, Portfolio, process_purchase, process_sale, project_name, process_user_transactions, re, RotatingFileHandler, send_email, Session, setup_logging, sys, time, unquote, update_listings, usd, verify_unique_token


def create_app():    
    app = Flask(__name__)

    # Set app mode according to setting in .env
    if os.getenv('FLASK_ENV') == 'testing':    
        from configs.config_testing import TestingConfig
        app.config.from_object(TestingConfig)
    elif os.getenv('FLASK_ENV') == 'production':
        from configs.config_prod import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from configs.config_dev import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Custom jinja filters
    app.jinja_env.filters['usd'] = usd
    app.jinja_env.filters['percentage'] = percentage
    app.jinja_env.filters['date_time'] = date_time
    app.jinja_env.filters['number_format'] = number_format

    # Enable flask-migrate (allows db changes via models.py)
    migrate = Migrate(app, db)

    
    # For flask-wtf generalized filters and validator, only append to sys.path if the path is set
    sys.path.append(app.config.get('CUSTOM_FLASKWTF_PATH'))

    Session(app)
    setup_logging(app)
    babel = Babel(app)
    db.init_app(app)
    csrf.init_app(app)
    talisman.init_app(app, content_security_policy=app.config['CONTENT_SECURITY_POLICY'])

    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

    from models import Listing, Transaction, User
    
    with app.app_context():
        app.logger.info(f'running setup... SQLAlchemy Engine URL is { db.engine.url }')
        db.create_all()
        app.logger.info('running setup... db.create_all has run')
        

# ------------------------------------------------------------------------


    @app.route('/readiness_check')
    def readiness_check():
    # Perform any necessary checks here, such as database connectivity, 
    # availability of external services, etc.
    # For simplicity, this example assumes the app is always ready.
    
        return 'Ready', 200  # Returns a 200 OK response with text "Ready"


# ------------------------------------------------------------------------    

    @app.route("/")
    @login_required
    def index():
        app.logger.info(f'running / ...  starting /  ')
        app.logger.info(f'running / ... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running / ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running / ... CSRF token is: { session.get("csrf_token", None) }')

        # Step 1: Pull user object based on session[user].
        user = db.session.query(User).filter_by(id = session.get('user')).scalar()

        # Step 2: Handle if no id (unlikely).
        if not user:
            app.logger.info(f'running / ...  error 2.0: no user data found for session[user] of: { session["user"] }')
            session['temp_flash'] = 'Error: User not found. Please log in again.'
            return redirect(url_for('login'))
        app.logger.info(f'running /...  user is: { user }')

        # Step 3: Call the function to create the portfolio object for the user
        portfolio = process_user_transactions(user)
        app.logger.info(f'running / ... for user {user} ... portfolio.cash is: { portfolio.cash }')

        # Step 4: Render index.html and pass in portfolio, cash, total_portfolio, username
        return render_template('index.html', user=user, portfolio=portfolio)

# ---------------------------------------------------------------------
    
    @app.route("/index_detail")
    @login_required
    def index_detail():
        app.logger.info(f'running /index_detail ...  starting /index_detail  ')
        app.logger.info(f'running /index_detail ... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /index_detail ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running /index_detail ... CSRF token is: { session.get("csrf_token", None) }')

        # Step 1: Pull user object based on session[user].
        user = db.session.query(User).filter_by(id = session.get('user')).scalar()
        
        # Step 2: Handle if no id (unlikely).
        if not user:
            app.logger.info(f'running /index_detail ...  Error 2: no user data found for session[user] of: { session["user"] }')
            session['temp_flash'] = 'Error: User not found. Please log in again.'
            return redirect(url_for('login'))
        app.logger.info(f'running /index_detail...  user is: { user }')

        # Step 3: Call the function to create the portfolio object for the user
        portfolio = process_user_transactions(user)
        app.logger.info(f'running /index_detail ... for user {user} ... portfolio.cash is: { portfolio.cash }')

        # Step 4: Render index.html and pass in portfolio, cash, total_portfolio, username
        return render_template('index_detail.html', user=user, portfolio=portfolio)
    
# --------------------------------------------------------------------------

    @app.route('/buy', methods=['GET', 'POST'])
    @login_required
    def buy():
        app.logger.info(f'running /buy ...  starting /buy ')
        app.logger.info(f'running /buy... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /buy ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running /buy ... CSRF token is: { session.get("csrf_token", None) }')

        form = BuyForm()

        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /buy ... user submitted via post and user input passed form validation')
                user = db.session.query(User).filter_by(id= session['user']).scalar()
                app.logger.info(f'running /buy ... retrieved user object from DB: { user }')
                                
                # Step 1.1.1: Pull in the user inputs from buy.html
                symbol = form.symbol.data
                shares = form.shares.data
                transaction_type = 'BOT'
                app.logger.info(f'running /buy ...  symbol is: { symbol } ')
                app.logger.info(f'running /buy ...  shares is: { shares } ')

                # Step 1.1.2: Run check_valid_shares, which:
                # (a) checks if symbol is valid and (b) checks that user has sufficient cash
                result = check_valid_shares(user_input_symbol=symbol, user_input_shares=shares, transaction_type=transaction_type)

                # Step 1.1.3: Handle if check_valid_shares(symbol, shares) failed
                if result['status'] == 'error':
                    app.logger.info(f'running /buy ...  Error 1.1.3 (check_valid_shares failed): check_valid_shares resulted with status: { result["status"] } and message: {  result["message"] }. Test failed. ')
                    flash(f'Error: { result["message"]} ')
                                                             
                try:
                    # Step 1.1.4: Handle if check_valid_shares(symbol, shares) failed
                    process_purchase(symbol=symbol, shares=shares, user=user, result=result)

                    # Step 1.1.6: Flash success message and redirect to /
                    app.logger.info(f'running /buy... purchase successful, redirecting to / ')
                    flash("Share purchase processed successfully!")
                    time.sleep(1)
                    return redirect(url_for('index'))
                
                # Step 1.1.7: Handle if unable to process purchase.
                except KeyError as e:
                    app.logger.info(f'running /buy... Error 1.1.7: {e}. Unable to run process_purchase(), flashing error and returning to /buy')
                    flash(f'running /buy ...  Error: Invalid symbol. Please try again.')
                    return redirect('/buy')

            # Step 1.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /buy ... Error 1.2 (form validation errors), flashing message and redirecting user to /buy')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /buy ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /buy ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('buy.html', form=form)

        # Step 2: User arrived via GET
        else:
            app.logger.info(f'Running /buy ... user arrived via GET')
            return render_template('buy.html', form=form)
                
# -----------------------------------------------------------------------
    
    @app.route('/check_email_registered', methods=['GET', 'POST'])
    
    def check_email_registered_route():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')
        return check_email_registered(user_input, False)

    # Returns True if user input is a registered email address.
    def check_email_registered(user_input, is_internal_call=False):
        user = db.session.query(User).filter_by(email=user_input).scalar()
        if user:
            app.logger.info(f'running /check_email_registered... user_input is a registered email: { user_input }')
            return 'True' if not is_internal_call else True
        else:
            app.logger.info(f'running /check_email_registered... user_input is not a registered email: { user_input }')
            return 'False' if not is_internal_call else False

# -----------------------------------------------------------------------

    @app.route('/check_valid_shares', methods=['GET', 'POST'])
    
    def check_valid_shares_route():
        if request.method == 'POST':
            user_input_symbol = request.form.get('user_input_symbol')
            user_input_shares = request.form.get('user_input_shares')
            transaction_type = request.form.get('transaction_type')
            result = check_valid_shares(user_input_symbol, user_input_shares, transaction_type)
            return jsonify(result)
        else:
            user_input_symbol = request.args.get('user_input_symbol')
            user_input_shares = request.args.get('user_input_shares')
            transaction_type = request.args.get('transaction_type')
        
        return check_valid_shares(user_input_symbol, user_input_shares, transaction_type, False)

    # Returns a dict (status accessed via status = result['status']).
    def check_valid_shares(user_input_symbol, user_input_shares, transaction_type):
        #app.logger.info(f'running /check_valid_shares... user_input_shares is: { user_input_shares }')
        #app.logger.info(f'running /check_valid_shares... transaction_type is: { transaction_type }')
        
        # Step 1: Ensure user_input_shares is a valid stock symbol
        if check_valid_symbol(user_input_symbol) == None:
            app.logger.info(f'running /check_valid_shares... user entered the following invalid symbol { user_input_symbol }. Test failed.')
            return {'status': 'error', 'message': 'Invalid stock symbol entered.'}
        
        # Step 2: Ensure user_input_shares is a positive integer (positive or negative)
        try:
            user_input_shares = int(user_input_shares)
            if user_input_shares < 0:
                app.logger.info(f'running /check_valid_shares... user entered a non-integer for shares. Test failed.')
                return {'status': 'error', 'message': 'Cannot enter a negative value for shares.'}
        except ValueError:
            app.logger.info(f'running /check_valid_shares... user entered a non-integer for shares. Test failed.')
            return {'status': 'error', 'message': 'Non-integer value entered for shares.'}
                
        try:
            # Step 3: Pull user object for signed-in user from DB
            user = db.session.query(User).filter_by(id=session.get('user')).scalar()
            app.logger.info(f'running /check_valid_shares... pulled user object: { user }')
            app.logger.info(f'running /check_valid_shares... user_input_shares (part 2) is: { user_input_shares }')

            # Step 4: Query the API to get an updated price for user_input_symbol
            symbol_data = company_data(user_input_symbol, fmp_key)
            transaction_value_per_share = round(symbol_data['price'], 2)
            #app.logger.info(f'running /check_valid_shares... transaction_value_per_share is: { transaction_value_per_share }')
            transaction_value_total = round(user_input_shares * transaction_value_per_share, 2)
            #app.logger.info(f'running /check_valid_shares... transaction_value_total is: { transaction_value_total }')

            # Step 5: Commence logic if user is buying shares (sufficient cash to complete purchase?)
            if transaction_type == 'BOT':
                #app.logger.info(f'running /check_valid_shares... user: {user} is trying to buy shares')
                
                # Step 5.1: Test if user has sufficient cash to cover the share purchase
                if user.cash < transaction_value_total:
                    app.logger.info(f'running /check_valid_shares... user: {user} has insufficient cash to complete purchase. Test failed.')
                    return {'status': 'error', 'message': f'Current cash balance of { usd(user.cash) } is insufficient to complete purchase costing { usd(transaction_value_total) }'}
                
                else:
                    #app.logger.info(f'running /check_valid_shares... user: {user} has sufficient cash. Test passed')
                    return {'status': 'success', 'message': f'Current cash balance of { usd(user.cash) } is sufficient to complete purchase costing { usd(transaction_value_total) }', 'symbol_data': symbol_data, 'transaction_value_per_share': transaction_value_per_share, 'transaction_value_total' : transaction_value_total}
            
            # Step 6: Commence logic if user is selling shares (sufficient shares to complete sale?)
            elif transaction_type == 'SLD':
                app.logger.info(f'running /check_valid_shares... user: {user} is trying to sell shares')
                
                # Step 6.1: Test if user has sufficient shares to sell
                total_shares_owned = db.session.query(func.sum(Transaction.shares_outstanding))\
                    .filter(Transaction.user_id == session.get('user'), 
                    Transaction.symbol == user_input_symbol,
                    Transaction.type == 'BOT').scalar() or 0
                #app.logger.info(f'running /check_valid_shares... total_shares_owned is: { total_shares_owned }')
                
                # Step 6.2: If user is trying to sell more shares than owned, test fails
                if user_input_shares > total_shares_owned:
                    app.logger.info(f'running /check_valid_shares... user: {user} entered more shares than owned: { total_shares_owned}. Test failed')
                    return {'status': 'error', 'message': f'You cannot sell more than your current holdings of { total_shares_owned } shares.'}
                
                # Step 6.3: If user is trying to sell more shares than owned, test passes
                else:
                    #app.logger.info(f'running /check_valid_shares... user: {user} has sufficient shares to sell. Test passed')
                    return {'status': 'success', 'message': f'You will sell { user_input_shares } of your { total_shares_owned } shares in { user_input_symbol }', 'symbol_data': symbol_data, 'transaction_value_per_share': transaction_value_per_share, 'transaction_value_total' : transaction_value_total}
            
            # Step 7: Commence logic if the third argument passed to check_valid_shares function is neither buy nor sell (e.g. invalid input)
            else:
                app.logger.info(f'running /check_valid_shares... invalid third argument of { transaction_type } passed to check_valid_shares. Must be buy or sell')
                raise Exception 
        
        # Step 8: Handle exception 
        except Exception as e:
            app.logger.info(f'running /check_valid_shares ...  Error 8: {e}. Test failed.')
            return {'status': 'error', 'message': str(e)}

# -----------------------------------------------------------------------

    @app.route('/check_valid_symbol_new', methods=['GET', 'POST'])
    
    def check_valid_symbol_route_new():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')

        results = check_valid_symbol_new(user_input, False)

        return jsonify(results)

    
    def check_valid_symbol_new(user_input, is_internal_call=False):
        app.logger.info(f'running /check_valid_symbol_new ... function started')
        app.logger.info(f'running /check_valid_symbol_new ... user_input is: { user_input }')

        try:

            # Step 1: Determine the primary filter and ordering criterion based on the length of user_input
            if len(user_input) < 6:
                primary_filter = Listing.symbol.ilike(user_input + '%')
                primary_order = func.abs(func.length(Listing.symbol) - func.length(user_input))
            else:
                primary_filter = Listing.name.ilike('%' + user_input + '%')  # Names containing user_input
                primary_order = func.abs(func.length(Listing.name) - func.length(user_input))  # Closest length match for names

            # Step 2: Construct the query with the determined filter and ordering
            listings = db.session.query(Listing.symbol, Listing.name, Listing.exchange_short).filter(or_(
                    primary_filter,  # Primary filter based on the length of user_input
                    Listing.name.ilike('%' + user_input + '%')  # Always include name contains user_input as a secondary option
                )
            ).order_by(
                primary_order,  # Primary ordering based on the length of user_input
                func.length(Listing.symbol), # Secondary ordering by symbol length, for tie-breaking
                func.length(Listing.name)  
                
            ).limit(5).all()
            app.logger.info(f'running /check_valid_symbol_new ... listings is: {listings}')

            # Step 3: Create list into which results of DB pull will go.
            results = []

            # Step 4: Populate list
            if listings:
                for listing in listings:
                    results.append({'symbol': listing.symbol, 'name': listing.name, 'exchange_short': listing.exchange_short})
                app.logger.info(f'running /check_valid_symbol_new ... results is: { results }')
            else:
                app.logger.info(f'running /check_valid_symbol_new ... no matches for user_input, results is: { results }')
            
            return results
        
        # Step 6: Handle exceptions
        except Exception as e:
            app.logger.info(f'running /check_valid_symbol_new ... function errored: { e }')
            return []

# -----------------------------------------------------------------------
        
    @app.route('/check_valid_symbol', methods=['GET', 'POST'])
    
    def check_valid_symbol_route():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')
        
        return check_valid_symbol(user_input, False)

    # Returns True if user input is a registered email address.
    def check_valid_symbol(user_input, is_internal_call=False):
        #app.logger.info(f'running /check_valid_symbol ... function started')

        try:
            user_input = user_input.upper()
            listing = db.session.query(Listing).filter_by(symbol=user_input).first()
            #app.logger.info(f'running /check_valid_symbol ... listing is: { listing }')

            if listing == None:
                app.logger.info(f'running /check_valid_symbol ... user_input is not a valid symbol: { user_input }')
                return 'False' if not is_internal_call else None
            else:
                #app.logger.info(f'running /check_valid_symbol ... user_input is a valid symbol: { user_input }')
                return 'True' if not is_internal_call else listing
        
        except Exception as e:
            app.logger.info(f'running /check_valid_symbol ... function errored: { e }')
            return 'False' if not is_internal_call else None
        
# -----------------------------------------------------------------------

    @app.route('/check_valid_password', methods=['GET', 'POST'])
    def check_valid_password():

        # Step 1: Pull in data passed in by JavaScript
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')
        
        # Step 2: Initialize checks_passed array
        checks_passed = []
        app.logger.info(f'running /check_valid_password... initialized checks_passed array ')
        
        # Step 3: Start performing checks, adding the name of each check passed to the checks_passed array.
        if len(password) >= pw_req_length:
                checks_passed.append('pw_reg_length')
                app.logger.info(f'running /check_valid_password... appended pw_reg_length to checks_passed array ')
        if len(re.findall(r'[a-zA-Z]', password)) >= pw_req_letter:
                checks_passed.append('pw_req_letter')
                app.logger.info(f'running /check_valid_password... appended pw_req_letter to checks_passed array ')
        if len(re.findall(r'[0-9]', password)) >= pw_req_num:
                checks_passed.append('pw_req_num')
                app.logger.info(f'running /check_valid_password... appended pw_req_num to checks_passed array ')
        if len(re.findall(r'[^a-zA-Z0-9]', password)) >= pw_req_symbol:
                checks_passed.append('pw_req_symbol')
                app.logger.info(f'running /check_valid_password... appended pw_req_symbol to checks_passed array ')
        app.logger.info(f'running /check_valid_password... checks_passed array contains: { checks_passed }')

        # Step 4: Ensure password and confirmation match
        if password == password_confirmation:
            confirmation_match = True
        else:
            confirmation_match = False
        app.logger.info(f'running /check_valid_password... confirmation_match is: { confirmation_match }')

        # Step 5: Pass the checks_passed array and confirmation_match back to JavaScript
        app.logger.info(f'running /check_valid_password... check finished, passing data back to JavaScript')
        return jsonify({'checks_passed': checks_passed, 'confirmation_match': confirmation_match} )

# -----------------------------------------------------------------------

    @app.route('/check_username_registered', methods=['GET', 'POST'])
    def check_username_registered_route():
        user_input = request.form.get('user_input') if request.method == 'POST' else request.args.get('user_input')
        return check_username_registered(user_input, False)

    # Returns True if user input is a registered username.
    def check_username_registered(user_input, is_internal_call=False):
        
        # Step 1: DB query for username
        user = db.session.query(User).filter_by(username=user_input).scalar()
        
        # Step 2: Handle depending on whether there was a result.
        if user:
            #app.logger.info(f'running /check_username_registered... user_input is a registered username: { user_input }')
            return 'True' if not is_internal_call else True
        else:
            #app.logger.info(f'running /check_username_registered... user_input is not a registered username: { user_input }')
            return 'False' if not is_internal_call else False
           
# -----------------------------------------------------------------------

    @app.route('/csp-violation-report', methods=['POST'])
    @csrf.exempt
    def csp_report():
        if request.content_type in ['application/csp-report', 'application/json']:
            report = request.get_json(force=True)
            # Process the report
            # Log the report for debugging
            app.logger.info(f"CSP Report: {report}")
        else:
            # Handle unexpected content-type
            app.logger.info(f"Unexpected Content-Type: {request.content_type}")
            return 'Unsupported Media Type', 415
        return '', 204

# -----------------------------------------------------------------------

    @app.route('/history', methods=['GET', 'POST'])
    @login_required
    def history():
        user = session.get('user')
        app.logger.info(f'running /history ...  user is: { user } starting /history  ')
        app.logger.info(f'running /history ... user is: { user } database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /history ... user is: { user } CSRF token is: { session.get("csrf_token", None) }')

        form = FilterTransactionHistory()

        history = db.session.query(Transaction).filter_by(user_id = session['user']).order_by(Transaction.timestamp.desc())

        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /history ... user is: { user } submitted via post and user input passed form validation')

                
                try:
                    # Step 1.1.1: Pull in data from form (the filters) 
                    date_start = form.date_start.data
                    date_end = form.date_end.data
                    type = form.transaction_type.data
                    app.logger.info(f'running /history ... user is: { user }  type is: { type }')

                    # Step 1.1.2: Apply whatever filters are included in submission
                    if date_start:
                        date_start = datetime.combine(date_start, datetime.min.time())
                        app.logger.info(f'running /history ... user is: { user }  date_start is: { date_start }')
                        history = history.filter(Transaction.timestamp >= date_start)
                    if date_end:
                        date_end = datetime.combine(date_end, datetime.max.time())
                        app.logger.info(f'running /history ... user is: { user }  date_end is: { date_end }')
                        history = history.filter(Transaction.timestamp <= date_end)
                    if type:
                        app.logger.info(f'running /history ... user is: { user }  type is: { type }')
                        history = history.filter(Transaction.type == type)

                    # Step 1.1.3: Render transaction history with filters applied.
                    history = history.order_by(Transaction.timestamp.desc()).all()
                    return render_template('history.html', form=form, history=history)

                # Step 1.1.4: Handle inability to apply filters 
                except Exception as e:
                    app.logger.info(f'running /history ...  Flashing error and rendering history.html with no filters applied')
                    flash(f'Error: Error {e}- please check your input and try again.')
                    return render_template('history.html', form=form, history=history)
            
            # Step 1.2: If form submissions fail validation, show error and redirect to history
            else:
                app.logger.info(f'Running /history ... Error (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    app.logger.info(f'Running /history ... erroring field is: {field}')
                    for error in errors:
                        app.logger.info(f'Running /history ... erroring on this field is: { error }')
                flash('Error: Invalid input. Please see the red text below for assistance.')
                
                # Render history.html and pass in the form and transaction history.
                return render_template("history.html", form=form, history=history)

        # Step 2: User arrived via GET
        else:
            app.logger.info(f'running history... user is: { user, None } and arrived via GET')
            
            # Render history.html and pass in the form and transaction history.
            return render_template("history.html", form=form, history=history)


# -----------------------------------------------------------------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        app.logger.info(f'running /login ...  starting /login ')
        app.logger.info(f'running /login... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /login ... CSRF token is: { session.get("csrf_token", None) }')

        nonce = generate_nonce()
        app.logger.info(f'running /login ... nonce is:{nonce}')
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
                app.logger.info(f'running /login ... User submitted via post and user input passed form validation')
                
                # Step 2.1.1: Pull in email and password from form and pull user item from DB.
                email = form.email.data
                password = form.password.data
                app.logger.info(f'running /login... user-submitted email is: { email }')
                
                try:
                    user = db.session.query(User).filter_by(email = email).scalar()
                    app.logger.info(f'running /login... queried database on user-entered email, result is: { user }')
                    
                    # Step 2.1.2: Validate that user-submitted password is correct
                    if not check_password_hash(user.hash, form.password.data):
                        app.logger.info(f'running /login... error 2.1.2 (invalid password), flashing message and redirecting user to /login')
                        session['temp_flash'] = 'Error: Invalid username and/or password. If you have not yet registered, please click the link below. If you have recently requested a password reset, check your email inbox and spam folders.'
                        time.sleep(1)
                        return redirect('/login')

                    # Step 2.1.3: Validate that user account is confirmed
                    if user.confirmed != 'Yes':
                        app.logger.info(f'running /login... error 2.1.3 (user.confirmed != yes), flashing message and redirecting user to /login')
                        session['temp_flash'] = 'Error: This account has not yet been confirmed. Please check your email inbox and spam folder for email instructions regarding how to confirm your registration. You may re-register below, if needed.'
                        time.sleep(1)
                        return redirect('/login')

                    # Step 2.1.4: Remember which user has logged in
                    session['user'] = user.id
                    app.logger.info(f'running /login... session[user_id] is: { session["user"] }')

                    # Step 2.1.5: Redirect user to home page
                    app.logger.info(f'running /login... redirecting to /index.  User is: { session }')
                    app.logger.info(f'running /login ... session.get(user) is: { session.get("user") }')
                    return redirect(url_for('index'))
                
                # Step 2.1.6: Handle exception if didn't find user email in DB
                except AttributeError as e:
                    app.logger.info(f'running /login... AttributeError {e}. Flashing error and redirecting to login')
                    session['temp_flash'] = 'Error: User not found. Please check your input. If you do not yet have an account, you may register via the link below.'
                    return render_template('login.html', form=form)

            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /login ... Error 2.2, flashing message and redirecting user to /login')
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('login.html', form=form)
        
        # Step 3: User arrived via GET
        app.logger.info(f'running /login ... user arrived via GET')
        response = make_response(render_template('login.html', form=form, nonce=nonce))
        app.logger.info(f'running /login... response.headers is: {response.headers}')
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
        app.logger.info(f'running /password_change... route started ')
        app.logger.info(f'running /password_change... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /password_change ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running /password_change ... CSRF token is: { session.get("csrf_token", None) }')

        form = PasswordChangeForm()
        
        # Step 1: Handle submission via post
        if request.method == 'POST':

            # Step 1.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /password_change ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 1.1.1: Pull in the user inputs from password_change.html
                try:
                    user = db.session.query(User).filter_by(email = form.email.data).scalar()
                    app.logger.info(f'running /password_change ... User object retrieved from DB via user-provided email is: { user }')
                    
                    # Step 1.1.1.1 If user-entered email and password don't match, flash error and render password_change.html
                    if not check_password_hash(user.hash, form.password_old.data):
                        app.logger.info(f'running /password_change ... Error 1.1.1.1 (email + password mismatch) user entered email of: { form.email.data } does not correspond with the password entered.')
                        flash('Error: invalid entry for email address and/or current password. Please check your input and try again.')
                        return render_template('password_change.html', form=form)

                    # Step 1.1.1.2: Hash the new password and update the DB.
                    user.hash = generate_password_hash(form.password.data)
                    db.session.commit()
                    app.logger.info(f'running /password_change ... updated user.hash in DB.')

                    # Step 1.1.1.3: Flash success msg redirect to index.
                    app.logger.info(f'running /password_change ...  successfully changed user password, redirecting to / ')
                    flash('Password password change successful!')
                    time.sleep(1)
                    return redirect(url_for('index'))
                
                # Step 1.1.2: If can't pull in email address and password from DB, flash error and render password_change.html
                except Exception as e:
                    app.logger.info(f'running /password_change ...  Error 1.1.2 (email not registered) User-submitted email address not in DB. Flashing error and rendering password_change.html')
                    flash('Error: invalid entry for email address and/or current password. Please check your input and try again.')
                    return render_template('password_change.html', form=form)
            
            # Step 1.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /password_change ... Error 1.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /password_change ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f'Running /password_change ... erroring on this field: {error}')
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('password_change.html', form=form)
            
        # Step 2: User arrived via GET
        else:
            app.logger.info(f'Running /password_change ... user arrived via GET')
            return render_template('password_change.html', form=form)
            
# ---------------------------------------------------------------------------------
    
    @app.route("/password_reset_request", methods=["GET", "POST"])
    def password_reset_request():
        app.logger.info(f'running /password_reset_request... route started ')
        app.logger.info(f'running /password_reset_request... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /password_reset_request ... CSRF token is: { session.get("csrf_token", None) }')

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
                app.logger.info(f'running /password_reset_request ... User submitted via post and user input passed form validation')

                # Step 2.1.1: Pull in the user inputs from form
                user = db.session.query(User).filter_by(email = form.email.data).scalar()

                try:
                    app.logger.info(f'running /password_reset_request ... User object retrieved from DB via user-provided email is: { user }. The corresponding user.id is: { user.id } and the corresponding user.email is: { user.email }')
                    
                    # Step 2.1.1.1: Generate token
                    token = generate_unique_token(user.id, app.config['SECRET_KEY'])
                    app.logger.info(f'running /password_reset_request ... token generated')

                    # Step 2.1.1.2: Formulate email
                    token_age_max_minutes = int(int(os.getenv('MAX_TOKEN_AGE_SECONDS')) / 60)
                    app.logger.info(f'running /password_reset_request ... token_age_max_minutes is: { token_age_max_minutes }')
                    username = user.username
                    recipient = user.email
                    subject = 'Password reset from MyFinance50'
                    attachments = None
                    url = url_for('password_reset_request_new', token=token, _external=True)
                    body = f'''Dear { username }: to reset your password, please visit the following link within the next { token_age_max_minutes } minutes:
                    
{ url }

If you did not make this request, you may ignore it.

Thank you,
Team {project_name}'''

                    # Step 2.1.1.3: Generate token, draft email, and send email
                    send_email(body=body, recipient=recipient)
                    #gmail_send_message(draft[id])
                    app.logger.info(f'Running /password_reset_request... reset email sent to email address: { user.email }.')

                    # Step 2.1.1.4: Flash success msg redirect to login.
                    app.logger.info(f'running /password_reset_request ...  successfully changed user password, redirecting to /login ')
                    session['temp_flash'] = 'Reset email sent. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
                
                # Step 2.1.2: If can't send email (likely due to user entering an unregistered email address), still flash
                # email sent message and redirect to login. This is done to reduce chances of brute force attack.
                except Exception as e:
                    app.logger.info(f'running /password_reset_request ...  Error 1.1.2 (user-submitted email not registered): { e }. Flashing sent email msg and redirecting to /login')
                    session['temp_flash'] = 'Reset email sent. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
            
            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /password_reset_request ... Error 1.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /password_reset_request ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /password_reset_request ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('password_reset_request.html', form=form)
        
        # Step 3: User arrived via GET
        else:
            app.logger.info(f'Running /password_reset_request ... user arrived via GET')
            return render_template('password_reset_request.html', form=form)
            
# ---------------------------------------------------------------------------------
    
    @app.route('/password_reset_request_new/<token>', methods=['GET', 'POST'])
    def password_reset_request_new(token):
        app.logger.info(f'running /password_reset_request_new... route started ')
        app.logger.info(f'running /password_reset_request_new... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /password_reset_request_new ... CSRF token is: { session.get("csrf_token", None) }')
        
        # Step 1: Take the token and decode it
        decoded_token = unquote(token)
        user = verify_unique_token(decoded_token, app.config['SECRET_KEY'], int(os.getenv('MAX_TOKEN_AGE_SECONDS')))
        
        # Step 2: If token is invalid, flash error msg and redirect user to login
        if not user:
            app.logger.info(f'Running /password_reset_request_new ... no user found.')
            session['temp_flash'] = 'Error: Invalid or expired reset link. Please login or re-request your password reset.'    
            return redirect(url_for('login'))
        
        # Step 3: If token is valid, set user.id to user['user_id'] property from token
        user = user
        app.logger.info(f'Running /password_reset_request_new ... user is: { user }.')

        form = PasswordResetRequestNewForm()
        
        # Step 4: Handle submission via post
        if request.method == 'POST':
        
            # Step 4.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /password_reset_request_new ... User submitted via post and user input passed form validation')

                # Step 4.1.1: Pull in the user inputs from form
                user = db.session.query(User).filter_by(id = user).scalar()
                app.logger.info(f'running /password_reset_request_new ... user object extracted from token is: { user }')
                app.logger.info(f'running /password_reset_request_new ... user.hash is: { user.hash }')
                app.logger.info(f'running /password_reset_request_new ... form.password.data is: { form.password.data }')

                try:                    
                    # Step 4.1.1.1: Check to ensure new password does not match existing password
                    if check_password_hash(user.hash, form.password.data):
                        app.logger.info(f'running /password_reset_request_new ... Error 4.1.1.1 (new password matches existing). Flashing error and rendering password_reset_request_new.html')
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
                    app.logger.info(f'running /password_reset_request_new ... password reset for user { user } entered into DB')

                    # Step 4.1.1.3: Flash success message and redirect user to index
                    app.logger.info(f'running /password_reset_request_new ... completed route for { user }. Flashing success message and redirecting to /index')
                    session['temp_flash'] = 'Password reset successful!'
                    time.sleep(1)
                    return redirect(url_for('index'))
                
                # Step 4.1.2: If can't update password (likely due to no user object resulting from
                # use of an invalid token) flash error msg and redirect to login.
                except Exception as e:
                    app.logger.info(f'running /password_reset_request_new ...  Error 4.1.2 (unable to update DB) Flashing error msg and redirecting to /login')
                    session['temp_flash'] = 'Error: Invalid token. Please login or repeat your password reset request via the link below.'
                    time.sleep(1)
                    return redirect(url_for('login'))
            
            # Step 4.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /password_reset_request_new ... Error 4.2 (form validation errors), flashing message and redirecting user to /password_change')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /password_reset_request_new ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /password_reset_request_new ... erroring on this field is: {error}")
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
            app.logger.info(f'Running /password_reset_request_new ... user arrived via GET')
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
        app.logger.info(f'running /profile ...  starting /profile  ')
        app.logger.info(f'running /profile ... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /profile ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running /profile ... CSRF token is: { session.get("csrf_token", None) }')

        form = ProfileForm()

        # Step 1: Pull user object based on session[user].
        user = db.session.query(User).filter_by(id = session.get('user')).scalar()

        # Step 2: Handle submission via post
        if request.method == 'POST':

            # Step 2.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /profile ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 2.1.1: Pull in data from form
                try:
                    # Step 2.1.1.1: Check if (a) there is user entry for username and if so, (b) whether it represents an already-taken username.
                    if form.username.data and check_username_registered(form.username.data) == True:
                        app.logger.info(f'running /profile ... Error 2.1.1.1 (username already registered). User input for username: { form.username.data } is already registered. Flash error and render profile.html')
                        flash(f'Error: Username: { form.username.data } is already registered. Please try another username.')
                        return render_template('profile.html', form=form )
                                        
                    # Step 2.1.1.2: Update user data as needed
                    if form.name_first.data:
                        user.name_first = form.name_first.data
                        app.logger.info(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.name_last.data:
                        user.name_last = form.name_last.data
                        app.logger.info(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.username.data:
                        user.username = form.username.data
                        app.logger.info(f'running /profile ... user.name_first updated to: { form.name_first.data }')
                    if form.accounting_method.data != user.accounting_method:
                        user.accounting_method = form.accounting_method.data
                        app.logger.info(f'running /profile ... user.accounting_method updated to: { form.accounting_method.data }')
                    if form.tax_loss_offsets.data != user.tax_loss_offsets:
                        user.tax_loss_offsets = form.tax_loss_offsets.data
                        app.logger.info(f'running /profile ... user.tax_loss_offsets updated to: { form.tax_loss_offsets.data }')
                    if form.tax_rate_STCG.data != user.tax_rate_STCG:
                        user.tax_rate_STCG = form.tax_rate_STCG.data
                        app.logger.info(f'running /profile ... user.tax_rate_STCG updated to: { form.tax_rate_STCG.data }')
                    if form.tax_rate_LTCG.data != user.tax_rate_LTCG:
                        user.tax_rate_LTCG = form.tax_rate_LTCG.data
                        app.logger.info(f'running /profile ... user.tax_rate_LTCG updated to: { form.tax_rate_LTCG.data }')
                    db.session.commit()
                    app.logger.info(f'running /profile ... successfully updated database')

                    # Step 2.1.1.3: Query DB to get updated data
                    user = db.session.query(User).filter_by(id=session.get('user')).scalar()
                    app.logger.info(f'running /profile ... refreshed user object for user is: { user }')
                    name_full = user.name_first+" "+user.name_last
                    form.name_full.data = name_full
                    form.username_old.data = user.username
                    form.email.data = user.email
                    form.created.data = user.created
                    form.cash_initial.data = usd(user.cash_initial)
                    app.logger.info(f'running /profile ... usd(user.cash_initial) is: { usd(user.cash_initial) }')
                    form.accounting_method.data = user.accounting_method
                    form.tax_loss_offsets.data = user.tax_loss_offsets
                    form.tax_rate_STCG.data = user.tax_rate_STCG
                    form.tax_rate_LTCG.data = user.tax_rate_LTCG
                    
                    # Step 2.1.1.4: Flash success message and render profile.html
                    app.logger.info(f'running /profile ... DB successfully updated with user changes. Flashing success message and rendering profile.html')
                    flash('Profile updated successfully!')
                    time.sleep(1)
                    return render_template('profile.html', form=form )
                
                # Step 2.1.2: If can't pull in data from form, flash error and render profile.html
                except Exception as e:
                    app.logger.info(f'running /profile ...  Error 2.1.2 (unable to update DB): { e }. Flashing error and rendering profile.html')
                    flash('Error: invalid entry. Please check your input and try again.')
                    return render_template('profile.html', form=form )
            
            # Step 2.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /profile ... Error 2.2 (form validation errors), flashing message and redirecting user to /profile')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /profile ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /profile ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('profile.html', form=form )
        
        # Step 2: User arrived via GET
        else:
            name_full = user.name_first+" "+user.name_last
            form.name_full.data = name_full
            form.username_old.data = user.username
            form.email.data = user.email
            form.created.data = user.created
            form.cash_initial.data = usd(user.cash_initial)
            form.accounting_method.data = user.accounting_method
            form.tax_loss_offsets.data = user.tax_loss_offsets
            form.tax_rate_STCG.data = user.tax_rate_STCG
            form.tax_rate_LTCG.data = user.tax_rate_LTCG
            
                
            app.logger.info(f'Running /profile ... user arrived via GET')
            return render_template('profile.html', form=form)

# --------------------------------------------------------------------------

    @app.route("/quote", methods=["GET", "POST"])
    @login_required
    def quote():
        app.logger.info(f'running /quote... route started ')
        app.logger.info(f'running /quote... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /quote ... session.get(user) is: { session.get("user", None) }')
        app.logger.info(f'running /quote ... CSRF token is: { session.get("csrf_token", None) }')

        form = QuoteForm()

        # Step 1: Check if there is a symbol in the query string (used to enable links)
        symbol = request.args.get('symbol')

        # Step 2: If the route was accessed via a direct link with a symbol parameter
        if symbol:
            try:
                # Step 2.1: Populate the form and submit automatically
                company_profile = company_data(symbol, fmp_key)
                return render_template("quoted.html", company_profile=company_profile)
            
            # Step 2.2: Handle if the link passed a bogus symbol
            except TypeError as e:
                flash(f'Error {e}: Invalid stock symbol')
                return redirect(url_for('quote'))  # Redirect to the quote page if symbol is invalid

        # Step 3: Handle submission via post
        if request.method == 'POST':

            # Step 3.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /quote ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 3.1.1: Pull in the user inputs from quote.html
                symbol = form.symbol.data

                # Step 3.1.2: Pull quote, returning error message if symbol is invalid
                try:
                    company_profile = company_data(symbol, fmp_key)
                    app.logger.info(f'running /quote... successfully pulled company_profile. Flashing message and directing user to quoted.html')
                    if company_profile:
                        return render_template("quoted.html", company_profile=company_profile)
                    else:
                        app.logger.info(f'running /quote... user submitted with invalid symbol: { symbol }. Flashing error and returning user to /quote.')
                        flash(f'Error: Invalid stock symbol')
                        return render_template('quote.html', form=form)

                except TypeError as e:
                    app.logger.info(f'running /quote... user submitted with invalid symbol: { symbol }. Flashing error and returning user to /quote.')
                    flash(f'Error {e}: Invalid stock symbol')
                    return render_template('quote.html', form=form)
            
            # Step 3.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /quote ... Error 1.2 (form validation errors), flashing message and redirecting user to /quote')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /quote ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /quote ... erroring on this field is: {error}")
                flash('Error: Invalid input. Please see the red text below for assistance.')
                return render_template('quote.html', form=form)
        
        # Step 4: User arrived via GET
        else:
            app.logger.info(f'Running /quote ... user arrived via GET')
            return render_template('quote.html', form=form)
    
# ------------------------------------------------------------------------------
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        app.logger.info(f'running /register ...  starting /register ')
        app.logger.info(f'running /register... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /register ... CSRF token is: { session.get("csrf_token", None) }')

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
                app.logger.info(f'running /register ... User submitted via post and user input passed form validation')
                
                # Step 2.1.1: Pull in email and password from form and pull user item from DB.
                name_first = form.name_first.data
                name_last = form.name_last.data
                username = form.username.data
                email = form.email.data
                password = form.password.data
                cash_initial = form.cash_initial.data
                cash = cash_initial
                accounting_method = form.accounting_method.data
                tax_loss_offsets = form.tax_loss_offsets.data
                tax_rate_STCG = form.tax_rate_STCG.data
                tax_rate_LTCG = form.tax_rate_LTCG.data

                try:
                    app.logger.info(f'running /register... user-submitted name_first is: { name_first }')
                    app.logger.info(f'running /register... user-submitted name_last is: { name_last }')
                    app.logger.info(f'running /register... user-submitted username is: { username }')
                    app.logger.info(f'running /register... user-submitted email address is: { email }')
                    app.logger.info(f'running /register... user-submitted accounting_method is: { accounting_method }')
                    app.logger.info(f'running /register... user-submitted tax_loss_offsets is: { tax_loss_offsets }')
                    app.logger.info(f'running /register... user-submitted tax_rate_STCG is: { tax_rate_STCG }')
                    app.logger.info(f'running /register... user-submitted tax_rate_LTCG is: { tax_rate_LTCG }')
                    
                    # Step 2.1.1.1: Ensure username and email address are not already registered
                    if check_email_registered(email) == True or check_username_registered(username) == True:
                        app.logger.info(f'Running /register ... Error 2.1.1.1   (email and/or username already registered), flashing message and redirecting user to /register')
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
                        cash_initial = cash_initial,
                        cash = cash_initial,
                        accounting_method = accounting_method,
                        tax_loss_offsets = tax_loss_offsets,
                        tax_rate_STCG = tax_rate_STCG,
                        tax_rate_LTCG = tax_rate_LTCG)
                    db.session.add(new_user)
                    db.session.commit()
                    app.logger.info(f'running /register ... new_user added to DB w/ unconfirmed=0')

                    # Step 2.1.1.3: Query new user object from DB to get id.
                    user = db.session.query(User).filter_by(email = email).scalar()

                    # Step 2.1.1.3: Generate token
                    token = generate_unique_token(user.id, app.config['SECRET_KEY'])
                    app.logger.info(f'running /register ... token generated')
                    app.logger.info(f'running /register ... int(os.getenv(MAX_TOKEN_AGE_SECONDS) is: { int(os.getenv("MAX_TOKEN_AGE_SECONDS")) }')

                    # Step 2.1.1.4: Formulate email
                    token_age_max_minutes = int(int(os.getenv('MAX_TOKEN_AGE_SECONDS'))/60)
                    username = user.username
                    recipient = user.email
                    subject = 'Confirm your registration with MyFinance50'
                    url = url_for('register_confirmation', token=token, _external=True)
                    body = f'''Dear { user.username }: to confirm your registration with MyFinance50, please visit the following link within the next { token_age_max_minutes } minutes:
                    
{ url }

If you did not make this request, you may ignore it.

Thank you,
Team {project_name}'''

                    # Step 2.1.1.5: Send email.
                    send_email(body=body, recipient=recipient)
                    app.logger.info(f'Running /register... reset email sent to email address: { user.email }.')
                    
                    # Step 2.1.1.6: Flash success msg redirect to login.
                    app.logger.info(f'running /register ...  successfully registered user, redirecting to /login ')
                    session['temp_flash'] = 'To confirm your registration and log in, please follow the instructions sent to you by email. Please do not forget to check your spam folder!'
                    time.sleep(1)
                    return redirect(url_for('login'))
                
                # Step 2.1.2: If user entry symbol or shares is invalid, flash error and render sell.html
                except Exception as e:
                    app.logger.info(f'running /register ...  Error 3.1.2 (unable to register user in DB and send email): {e}. Flashing error msg and rendering register.html ')
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
                app.logger.info(f'Running /register ... Error 2.2 (form validation errors), flashing message and redirecting user to /register')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /register ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /register ... erroring on this field is: {error}")
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
            app.logger.info(f'Running /register ... user arrived via GET')
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
        app.logger.info(f'running /register_confirmation ...  starting /register_confirmation ')
        app.logger.info(f'running /register_confirmation... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /register_confirmation ... CSRF token is: { session.get("csrf_token", None) }')
        
        try:
            # Step 1: Take the token and decode it
            decoded_token = unquote(token)
            user = verify_unique_token(decoded_token, app.config['SECRET_KEY'], int(os.getenv('MAX_TOKEN_AGE_SECONDS')))
        
            # Step 2: If token is invalid, flash error msg and redirect user to register
            if not user:
                app.logger.info(f'Running /register_confirmation ... no user found.')
                session['temp_flash'] = 'Error: Invalid or expired confirmation link. Please login or re-request your password reset.'    
                return redirect(url_for('register'))
        
            # Step 3: If token is valid, pull user object from DB
            user = db.session.query(User).filter_by(id = user).scalar()
            app.logger.info(f'Running /register_confirmation ... user object is: { user }.')
            app.logger.info(f'Running /register_confirmation ... user.confirmed is: { user.confirmed }.')

            # Step 4: If user is already confirmed, flash error and redirect to login
            if user.confirmed == 'No':
                user.confirmed = 'Yes'
                db.session.commit()
                app.logger.info(f'Running /register_confirmation ... updated user: { user } to confirmed.')
            else:
                app.logger.info(f'Running /register_confirmation ... Error 4 (user already confirmed). Flashing msg and redirecting to login.')
                session['temp_flash'] = 'Error: This account is already confirmed. Please log in.'
                time.sleep(1)
                return redirect(url_for('login'))
            

            # Step 5: Flash success message and return to index
            session['user'] = user.id
            app.logger.info(f'Running /register_confirmation ... successfully updated confirmed for user object: { user } to: 1.')
            flash('Your registration is confirmed. Welcome to MyFinance50!')
            time.sleep(1)
            return redirect(url_for('index'))

        # Step 6: If token is invalid or DB update fails, flask error message and redirect to reset.html
        except Exception as e:
                app.logger.info(f'running /register_confirmation ...  Error 3.1.2 (unable to register user in DB and send email): {e}. Flashing error msg and rendering register.html ')
                session['temp_flash'] = 'Error: Unable to send email. Please ensure you are using a valid email address.'
                time.sleep(1)
                return redirect(url_for('register'))
                        
# -------------------------------------------------------------------------------

    @app.route("/sell", methods=["GET", "POST"])
    @login_required
    def sell():
        app.logger.info(f'running /sell ...  starting /sell ')
        app.logger.info(f'running /sell... database URL is: { os.path.abspath("finance.sqlite") }')
        app.logger.info(f'running /sell... session[user] is: { session["user"] }')
        
        form = SellForm()
        
        # Step 1: Populate the symbols dropdown in sell.html
        # Step 1.1: Call the list of stocks from the SQL database and convert to a list
        query_results = db.session.query(Transaction.symbol).filter(Transaction.user_id == session['user']).distinct().order_by(Transaction.symbol).all()
        symbols = [(symbol[0], symbol[0]) for symbol in query_results]
        app.logger.info(f'running /sell... symbols is: { symbols }')
        
        # Step 1.2: Pass the aforementioned list of symbols to sell.html
        app.logger.info(f'running /sell ...  user arrived via GET, displaying page ')
        form.symbol.choices = [('', 'Select Symbol')] + symbols

        # Step 2: Pull the user object, which will be used throughout the route
        user = db.session.query(User).filter_by(id = session['user']).scalar()

        # Step 3: Handle submission via post
        if request.method == 'POST':

            # Step 3.1: Handle submission via post + user input clears form validation
            if form.validate_on_submit():
                app.logger.info(f'running /sell ... User: { session["user"] } submitted via post and user input passed form validation')

                # Step 3.1.1: Pull in the user inputs from sell.html
                try:
                    # Step 3.1.1.1: Pull data from form
                    symbol = form.symbol.data
                    shares = form.shares.data
                    transaction_type = form.transaction_type.data
                    app.logger.info(f'running /sell ... shares is: { shares }')

                    # Step 3.1.1.2: Retrieve from DB the shares owned in the specified symbol
                    result = check_valid_shares(user_input_symbol=symbol, user_input_shares=shares, transaction_type=transaction_type)

                    # Step 3.1.1.3: Handle if check_valid_shares(symbol, shares) failed
                    if result['status'] == 'error':
                        app.logger.info(f'running /sell ...  error 1.1.3 (check_valid_shares failed): check_valid_shares resulted with status: { result["status"] } and message: {  result["message"] }. Test failed. ')
                        flash(f'Error: { result["message"]} ')

                    # Step 3.1.1.4: Update the DB
                    process_sale(symbol=symbol, shares=shares, user=user, result=result)
                    
                    # Step 3.1.1.5: Flash success message and redirect user to /.
                    app.logger.info(f'running /sell ...  sale processed successfully. Redirecting user to / ')
                    flash("Share sale processed successfully!")
                    time.sleep(1)
                    return redirect(url_for('index'))

                # Step 3.1.2: If user entry symbol or shares is invalid, flash error and render sell.html
                except Exception as e:
                    app.logger.info(f'running /sell ...  Error 3.1.2 (invalid entry for symbol and/or shares): { e }. User entry for symbol and/or shares was invalid. Error is: {e}')
                    flash(f'Error: Please enter a valid share symbol and positive number of shares not exceeding your current holdings.')
                    return render_template('sell.html', form=form, symbols = symbols)
            
            # Step 3.2: Handle submission via post + user input fails form validation
            else:
                app.logger.info(f'Running /sell ... Error 3.2 (form validation errors), flashing message and redirecting user to /sell')    
                for field, errors in form.errors.items():
                    app.logger.info(f"Running /sell ... erroring field is: {field}")
                    for error in errors:
                        app.logger.info(f"Running /sell ... erroring on this field is: {error}")
                session['temp_flash'] = 'Error: Invalid input. Please see the red text below for assistance.'
                return render_template('sell.html', form=form, symbols = symbols)

        # Step 4: User arrived via GET
        else:
            app.logger.info(f'Running /sell ... user arrived via GET')
            return render_template('sell.html', form=form, symbols = symbols)

# -------------------------------------------------------------------------------------

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()