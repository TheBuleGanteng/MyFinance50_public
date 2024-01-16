from datetime import datetime
import os
import time
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd

# Must declare this before app initialization to avoid circular import.
db = SQLAlchemy()

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
    
    # Custom filter
    app.jinja_env.filters['usd'] = usd

    Session(app)
    db.init_app(app)

    # Configure CS50 Library to use SQLite database
    #CS50_db = SQL("sqlite:///finance.sqlite")

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
        print(f'running / ...  starting / ')    
        print(f'running / ... session.get(user) is: { session.get("user") }')

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
        print(f'running /buy ... session.get(user) is: { session.get("user") }')

        
        # Step 2: If the user submitted the info via get, then display the buy page:
        if request.method == "GET":
            return render_template("buy.html")

        # Step 3: If the user submitted the info via post, then run the following code:
        if request.method == "POST":

            # Step 1: Pull in the user inputs from buy.html
            symbol = request.form.get("symbol")
            # Since the form receives shares as a string, convert it to an integer.
            try:
                shares = int(request.form.get("shares"))
            except ValueError:
                return apology("Apology: Please enter integer for number of shares", 400)
            print(f'running / ...  symbol is: { symbol } ')
            print(f'running / ...  shares is: { shares } ')

            # Step 3.1: Check: Has user filled the boxes for symbol and shares?
            if not symbol or not shares:
                return apology("Apology: Please complete stock symbol and number of shares.", 403)

            # Step 3.2: Check: Has user provided a valid symbol?
            # Use the lookup function to ensure the stock symbol entered by the user is valid.
            if (lookup(symbol)) == None:
                return apology("Apology: No such symbol found", 400)

            # Step 3.3: Check: Has user entered an integer for number of shares?
            # If the symbol is found, then check to ensure the user entered an integer for number of shares.
            elif not isinstance(shares, int):
                return apology("Apology: Please enter integer for number of shares", 400)

            # Check: Has user entered negative number for shares?
            # If the symbol is found, and the number is an integer, check that the integer is positive.
            elif int(shares) < 0:
                return apology("Apology: Please enter a positive integer for number of shares", 400)

            # Use lookup to get the price of the stock.
            price_bot = (lookup(symbol))["price"]
            # Calculate the total transaction value.
            txn_value = float(shares) * price_bot

            # Query the SQL database to see how much cash the user has on hand.
            # Here, we query the value for cash from the current user.
            user = db.session.query(User).filter_by(id = session.get('user')).scalar()
            if not user:
                print(f'running /buy... no user found in database')
                return redirect("/login")
            print(f'running /buy... user is: { user }')

            if txn_value >= user.cash:
                print(f'running /buy... txn_value is: { txn_value } and user.cash is only: { user.cash }')
                return apology("Apology: Insufficient cash to complete transaction", 403)
            else:
                # Get current date and time, needed for txn timestamp
                timestamp = datetime.now().replace(microsecond=0)

                # Capitalize user inputted stock symbol to eliminate any issues re capitalization
                symbol = symbol.upper()
                
                # Add new entry into the transaction table to represent the share purchase.
                new_transaction = Transaction(
                    user_id=user.id, 
                    txn_date=timestamp, 
                    txn_type='BOT', 
                    symbol=symbol, 
                    txn_shrs=shares, 
                    txn_shr_price=price_bot, 
                    txn_value=txn_value
                )
                db.session.add(new_transaction)
                db.session.commit()       
                
                # Reduce cash on hand by amount of stock purchase.
                user.cash -= txn_value
                db.session.commit()
                                
                # Flash an indication to the user that the share sale was successful and then redirect to index.
                print(f'running /buy... purchase successful, redirecting to / ')
                flash("Share purchase processed successfully!")
                time.sleep(3)
                return redirect("/")
    
# -----------------------------------------------------------------------
    
    @app.route("/history")
    @login_required
    def history():
        print('running /history... route started ')

        # Pull the symbol and the total shares owned from the transactions database
        history = db.session.query(Transaction).filter_by(user_id = session['user']).order_by(Transaction.txn_date.desc()).all()
        print(f'running /history... history is: { history } ')
           
        # Render index.html and pass in the values in the portfolio pull and for cash.
        return render_template("history.html", history=history)

# -----------------------------------------------------------------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""
        print(f'running /login ...  starting /login ')
        print(f'running /login... database URL is: { os.path.abspath("finance.sqlite") }')

        # Step 1: Forget any user_id
        session.clear()

        # Step 2: User reached route via POST (as by submitting a form via POST)
        if request.method == 'POST':
            print(f'running /login... user submitted via post ')
            
            # Step 2.1: Ensure username was submitted
            if not request.form.get('username'):
                print(f'running /login... error 2.1, returning apology')
                return apology('must provide username', 403)

            # Step 2.2: Ensure password was submitted
            elif not request.form.get('password'):
                print(f'running /login... error 2.2, returning apology')
                return apology('must provide password', 403)

            # Step 2.3: Query database for username
            username = request.form.get('username')
            print(f'running /login... username is: { username }')
            
            user = db.session.query(User).filter_by(username = username).scalar()
            print(f'running /login... queried database on user-entered username, result is: { user }')
            
            # Step 2.4: Ensure username exists
            if not user or not check_password_hash(user.hash, request.form.get("password")):
                print(f'running /login... error 2.4, returning apology')
                return apology("invalid username and/or password", 403)

            # Step 2.5: Remember which user has logged in
            session['user'] = user.id
            print(f'running /login... session[user_id] is: { session["user"] }')

            # Step 2.6: Redirect user to home page
            print(f'running /login... redirecting to /index.  User is: { session }')
            print(f'running /login ... session.get(user) is: { session.get("user") }')
            return redirect("/")

        # Step 3: User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")
        
# --------------------------------------------------------------------------------

    @app.route("/logout")
    def logout():
        """Log user out"""

        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

# -----------------------------------------------------------------------

    @app.route("/quote", methods=["GET", "POST"])
    @login_required
    def quote():
        print(f'running /quote... route started ')

        # If the user submitted the info via get, then run the following code:
        if request.method == "GET":
            return render_template("quote.html")

        # If the user submitted the info via post, then run the following code:
        if request.method == "POST":
            symbol = request.form.get("symbol")
            
            if not symbol:
                print(f'running /quote... user submitted with no symbol')
                return apology("Must enter a stock symbol", 400)
            
            symbol = symbol.strip().upper()
            print(f'running /quote... symbol is: { symbol } ')
            
            # If the symbol entered isn't valid, throw an apology.
            stock_info = (lookup(symbol))
            print(f'running /quote... stock_info is: { stock_info } ')
            
            if not stock_info:
                print(f'running /quote... no stock_info found, user submitted an invalid symbol of: { symbol }')
                return apology("No such symbol found", 400)
            
            name = stock_info["name"]
            price = stock_info["price"]
            return render_template("quoted.html", symbol=symbol, name=name, price=price)
    
# ------------------------------------------------------------------------------
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        print(f'running /register ...  starting /register ')
        print(f'running /register... database URL is: { os.path.abspath("finance.sqlite") }')
        
        # If the user submitted the info via get, then run the following code:
        if request.method == "GET":
            return render_template("register.html")

        # If the user submitted the info via post, then run the following code:
        if request.method == "POST":
            # Take the values for username and password from the registration form, respectively.
            username = request.form.get("username")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")
            print(f'running /register ...  user-entered username is: { username } ')

            # If username, password, or password_confirmation are blank, throw an error message.
            if not username or not password or not confirmation:
                print(f'running /register ...  Error: user failed to enter username, password, or confirmation ')    
                return apology("Apology: Please complete username, password, and password confirmation.", 400)
                # return redirect("/register")
            print(f'running /register ...  user-entered username is: { username } ')

            # If password and password_confirmation don't match, throw an error message.
            if password != confirmation:
                print(f'running /register ...  Error: user entry for password and confirmation do not match ')
                return apology("Apology: Please ensure password and password confirmation match.", 400)

            # If user is already registered, throw an error message.
            # Execute the query and fetch one result
            duplicates_username = db.session.query(User).filter_by(username = username).first()

            if duplicates_username:
                print(f'running /register ...  Error: username already taken ')
                return apology("Apology: User already registered", 400)

            # Then, insert the username and hased password into their corresponding columns in the database.
            new_user = User(username = username, hash = generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in, whith the user's session id = their id in the database (which was auto-generated when we added the user to the db, in accordance with .schema)
            session['user'] = db.session.query(User.id).filter_by(username = username).scalar()
            # Flash an indication to the user that the share sale was successful and then redirect to index.
            print(f'running /register ...  successfully registered user, redirecting to /buy ')
            flash("Registration processed successfully!", 200)
            time.sleep(3)
            return redirect("/buy")

# --------------------------------------------------------------------------------
    
    @app.route("/password_change", methods=["GET", "POST"])
    @login_required
    def password_change():
        print(f'running /password_change ...  starting /password_change ')
        print(f'running /password_change... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /password_change... session[user] is: { session["user"] }')

        # If the user submitted the info via get, then run the following code:
        if request.method == "GET":
            return render_template("password_change.html")

        # If the user submitted the info via post, then run the following code:
        if request.method == "POST":
            # Take the values for username, current password, new password, and new password confirmation from the registration form, respectively.
            username = request.form.get("username")
            password = request.form.get("password")
            password_new = request.form.get("password_new")
            password_new_confirmed = request.form.get("password_new_confirmed")

            # If username, password, password_new, or password_new_confirmation are blank, throw an error message.
            if not username or not password or not password_new or not password_new_confirmed:
                print(f'running /password_change ...  Error: missing user entry for username, password, password_new, and password_new_confirmed ')
                return apology("Apology: Please complete username, current password, new password, and new password confirmation.", 403)

            # If password_new and password_new_confirmed don't match, throw an error.
            if password_new != password_new_confirmed:
                print(f'running /password_change ...  Error: password_new != password_new_confirmed ')
                return apology("Apology: Please ensure new password and new password confirmation match.", 403)

            # Query database for username
            user = db.session.query(User).filter_by(username = username).scalar()
            
            # Ensure username exists and password is correct
            if not user or not check_password_hash(user.hash, password):
                print(f'running /password_change ...  Error: user not found in db or user-entered password is incorrect ')
                return apology("Apology: Invalid username and/or password", 403)

            # Hash the new password and update the DB.
            user.hash = generate_password_hash(password_new)
            db.session.commit()

            # Flash an indication to the user that the password password_change was successful and then redirect to index.
            print(f'running /password_change ...  successfully changed user password, redirecting to /buy ')
            flash("Password password change successful!")
            time.sleep(3)
            return redirect("/buy")

# ---------------------------------------------------------------------------------

    @app.route("/sell", methods=["GET", "POST"])
    @login_required
    def sell():
        print(f'running /sell ...  starting /sell ')
        print(f'running /sell... database URL is: { os.path.abspath("finance.sqlite") }')
        print(f'running /sell... session[user] is: { session["user"] }')
        
        user = db.session.query(User).filter_by(id = session['user']).scalar()

        # If the user submitted the info via get, then display the buy page:
        if request.method == "GET":
            # Call the list of stocks from the SQL database, so that it can be passed to sell.html
            symbols = db.session.query(Transaction.symbol).filter(Transaction.user_id == session['user']).distinct().order_by(Transaction.symbol).all()
            symbols = [symbol[0] for symbol in symbols]
            print(f'running /sell... symbols is: { symbols }')
            
            # Pass the aforementioned list of stocks to sell.html
            print(f'running /sell ...  user arrived via GET, displaying page ')
            return render_template('sell.html', symbols = symbols)

        # If the user submitted the info via post, then run the following code:
        if request.method == "POST":
            print(f'running /sell ...  user submitted via POST ')

            # Pull in the user entry for the share they want to sell ("symbol") and the number of shares ("shares")
            try:
                symbol = str(request.form.get("symbol")).strip().upper()
                shares = int(request.form.get("shares"))
            except ValueError as e:
                print(f'running /sell ...  Error: user entered invalid data to form. Error is: { e } ')
                return apology("Apology: Please complete stock symbol and number of shares.", 400)

            # Check: User entered an integer for number of shares?
            if (type(shares)) != int:
                print(f'running /sell ...  Error: user did not enter an int shares ')
                return apology("Apology: Please enter a integer for number of shares", 400)

            # Check 3: User entered positive integer?
            if shares < 1:
                print(f'running /sell ...  Error: user entered a negative number for shares ')
                return apology("Apology: Please enter a positive integer for number of shares", 400)

            # Will need to call the db again to check number of shares user requested to sell against the user's actual holdings.
            total_shares = db.session.query(func.sum(Transaction.txn_shrs))\
                .filter(Transaction.user_id == user.id, Transaction.symbol == symbol)\
                .scalar()
            print(f'running /sell ...  total shares is: { total_shares } ')

            # Check 4: User has enough shares to sell?
            if shares > total_shares:
                print(f'running /sell ...  Error: user tried to sell more shares than they own; total_shares is : { total_shares } ')
                return apology("Apology: You cannot sell more shares than you own", 400)

            # Passed all checks- proceed
            # Get current date and time, needed for txn timestamp
            timestamp = datetime.now().replace(microsecond=0)

            # Use lookup to get the price of the stock.
            txn_shr_price = (lookup(symbol))['price']

            # Calculate the total transaction value.
            txn_value = -shares * txn_shr_price

            # Add new entry into the transaction table to represent the share purchase.
            # Note the negative value. This is to ensure that the total value of share holdings and cash are incremented appropriately.
            txn_shrs = shares * -1
            
            new_transaction = Transaction(
                user_id = session['user'],
                txn_date = timestamp,
                txn_type = 'SLD',
                symbol = symbol,
                txn_shrs = txn_shrs,
                txn_shr_price = txn_shr_price,
                txn_value = txn_value
            )
            print(f'running /sell ...  new_transaction is: { new_transaction } ')
            db.session.add(new_transaction)
            db.session.commit()
            print(f'running /sell ...  new_transaction added to DB ')

            # Reduce cash on hand by amount of stock purchase.
            print(f'running /sell ...  user.cash before deducting txn_value is: { user.cash } ')
            user.cash = user.cash - txn_value
            db.session.commit()
            print(f'running /sell ...  user.cash after deducting txn_value is: { user.cash } ')

            # Flash an indication to the user that the share sale was successful and then redirect to index.
            print(f'running /sell ...  sale processed successfully. Redirecting user to / ')
            flash("Share sale processed successfully!")
            time.sleep(3)
            return redirect("/")

# -------------------------------------------------------------------------------------

    return app

if __name__ == '__main__': 
    app.run()