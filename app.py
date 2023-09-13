import os

# "time" library is used for sleep function
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    # Pull the symbol and the total shares owned from the transactions database
    portfolio = db.execute(
        "SELECT symbol, SUM(txn_shrs) AS summed_txn_shares, txn_shr_price, SUM(txn_value) AS summed_txn_value FROM transactions WHERE user_id = (?) GROUP BY symbol", (session["user_id"])
    )

    # Pull the current price for each stock in the user's portfolio and append it to portfolio.
    # For each row in the portfolio (portfolio is grouped by symbol, so this effectively means for each stock held)
    for row in portfolio:
        # For that row (stock), append a field called "current price" which looks up the symbol and retrieves the price, setting that to "current price"
        row["current_price"] = lookup(row["symbol"])["price"]

    # Pull cash from the customers table
    cash = db.execute("SELECT cash FROM users WHERE id = (?)", session["user_id"])
    # Check if the person has a record for cash (they should).
    if cash[0]["cash"] == None:
        cash = 0
    else:
        # Convert that value to a real number
        cash = cash[0]["cash"]

    # Use a simple for look to calculate the total value of shares held + cash
    total_shares_value = 0

    # For each row in portfolio (the list of stock holdings grouped by symbol), add the value of that row's share holdings to get the total value of all share holdings.
    for row in portfolio:
        total_shares_value = total_shares_value + row["summed_txn_value"]

    # Calculate total portfolio value (cash + total share holdings).
    total_portfolio = total_shares_value + cash

    # Pass username into a variable, so that it can in turn be passed to index.html
    # Fist, we pull the username from the table users
    username = db.execute(
        "SELECT username FROM users WHERE id = ?", (session["user_id"])
    )
    # Second, we isloate the value in the first (row 0) key:value pair returned by the db pull above.
    username = username[0]["username"]

    # Render index.html and pass in the values in the portfolio pull and for cash.
    return render_template(
        "index.html", portfolio=portfolio, cash=cash, total_portfolio=total_portfolio, username=username
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # Pull in the user inputs from buy.html
    symbol = request.form.get("symbol")
    shares = request.form.get("shares")

    # If the user submitted the info via get, then display the buy page:
    if request.method == "GET":
        return render_template("buy.html")

    # If the user submitted the info via post, then run the following code:
    if request.method == "POST":
        # Check: Has user filled the boxes for symbol and shares?
        if not symbol or not shares:
            return apology("Apology: Please complete stock symbol and number of shares.", 403)

        # Check: Has user provided a valid symbol?
        # Use the lookup function to ensure the stock symbol entered by the user is valid.
        if (lookup(symbol)) == None:
            return apology("Apology: No such symbol found", 400)

        # Check: Has user entered an integer for number of shares?
        # If the symbol is found, then check to ensure the user entered an integer for number of shares.
        elif not isinstance(shares, int) and (not isinstance(shares, str) or not shares.isdigit()):
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
        cash_on_hand = db.execute(
            "SELECT cash FROM users WHERE id = (?)", session["user_id"]
        )
        # Here, it says take the fist record from cash_on_hand and provide it as a float.
        cash_on_hand = float(cash_on_hand[0]["cash"])

        if txn_value >= cash_on_hand:
            return apology("Apology: Insufficient cash to complete transaction", 403)
        else:
            # Get current date and time, needed for txn timestamp
            timestamp = datetime.now()
            # Capitalize user inputted stock symbol to eliminate any issues re capitalization
            symbol = symbol.upper()
            # Add new entry into the transaction table to represent the share purchase.
            db.execute(
                "INSERT INTO transactions (user_id, txn_date, txn_type, symbol, txn_shrs, txn_shr_price, txn_value) VALUES(?, ?, ?, ?, ?, ?, ?)", session["user_id"], timestamp, "BOT", symbol, shares, price_bot, txn_value
            )
            # Reduce cash on hand by amount of stock purchase.
            db.execute(
                "UPDATE users SET cash = (?) WHERE id = (?)", cash_on_hand - txn_value, session["user_id"]
            )

            # Flash an indication to the user that the share sale was successful and then redirect to index.
            flash("Share purchase processed successfully!")
            time.sleep(3)
            return redirect("/")


@app.route("/history")
@login_required
def history():
    # Pull the symbol and the total shares owned from the transactions database
    history = db.execute(
        "SELECT txn_date, txn_id, symbol, txn_type, txn_shrs, txn_shr_price, txn_value FROM transactions WHERE user_id = ?",(session["user_id"])
    )

    # Render index.html and pass in the values in the portfolio pull and for cash.
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    symbol = request.form.get("symbol")

    # If the user submitted the info via get, then run the following code:
    if request.method == "GET":
        return render_template("quote.html")

    # If the user submitted the info via post, then run the following code:
    if request.method == "POST":
        # If the symbol entered isn't valid, throw an apology.
        if symbol.strip() == "":
            return apology("Must enter a stock symbol", 400)

        # If the symbol entered isn't valid, throw an apology.
        elif (lookup(symbol)) == None:
            return apology("No such symbol found", 400)
        else:
            symbol = request.form.get("symbol")
            symbol = (lookup(symbol))["symbol"]
            name = (lookup(symbol))["name"]
            price = (lookup(symbol))["price"]
            return render_template("quoted.html", symbol=symbol, name=name, price=price)


@app.route("/register", methods=["GET", "POST"])
def register():
    # Take the values for username and password from the registration form, respectively.
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # If the user submitted the info via get, then run the following code:
    if request.method == "GET":
        return render_template("register.html")

    # If the user submitted the info via post, then run the following code:
    if request.method == "POST":
        # If username, password, or password_confirmation are blank, throw an error message.
        if not username or not password or not confirmation:
            return apology("Apology: Please complete username, password, and password confirmation.", 400)
            # return redirect("/register")

        # If password and password_confirmation don't match, throw an error message.
        elif password != confirmation:
            return apology("Apology: Please ensure password and password confirmation match.", 400)

        # If user is already registered, throw an error message.
        # Execute the query and fetch one result
        duplicates_username = db.execute(
            "SELECT * FROM users WHERE username = ?", (username)
        )

        if len(duplicates_username) > 0:
            return apology("Apology: User already registered", 400)

        # If none of the error checks above throw an error message, then first hash the user inputter password.
        hashed_password = generate_password_hash(password)
        # Then, insert the username and hased password into their corresponding columns in the database.
        db.execute(
            "INSERT INTO users (username, hash) VALUES(?, ?)", username, hashed_password
        )
        # Log the user in, whith the user's session id = their id in the database (which was auto-generated when we added the user to the db, in accordance with .schema)
        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE username=?", username
        )
        # Flash an indication to the user that the share sale was successful and then redirect to index.
        flash("Registration processed successfully!", 200)
        time.sleep(3)
        return redirect("/buy")


@app.route("/reset", methods=["GET", "POST"])
def reset():
    # Take the values for username, current password, new password, and new password confirmation from the registration form, respectively.
    username = request.form.get("username")
    password = request.form.get("password")
    password_new = request.form.get("password_new")
    password_new_confirmed = request.form.get("password_new_confirmed")

    # If the user submitted the info via get, then run the following code:
    if request.method == "GET":
        return render_template("reset.html")

    # If the user submitted the info via post, then run the following code:
    if request.method == "POST":
        # If username, password, password_new, or password_new_confirmation are blank, throw an error message.
        if not username or not password or not password_new or not password_new_confirmed:
            return apology("Apology: Please complete username, current password, new password, and new password confirmation.", 403)

        # If password_new and password_new_confirmed don't match, throw an error.
        if password_new != password_new_confirmed:
            return apology("Apology: Please ensure new password and new password confirmation match.", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Apology: Invalid username and/or password", 403)

        # If these checks pass, the person is legit and the reset process should proceed.
        # # If none of the error checks above throw an error message, then first hash the user inputter password.
        password_new_hashed = generate_password_hash(password_new)

        # Then, insert the username and hased password into their corresponding columns in the database.
        db.execute(
            "UPDATE users SET hash = (?) WHERE id = (?)", password_new_hashed, session["user_id"]
        )

        # Flash an indication to the user that the password reset was successful and then redirect to index.
        flash("Password reset successful!")
        time.sleep(3)
        return redirect("/buy")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # If the user submitted the info via get, then display the buy page:
    if request.method == "GET":
        # Call the list of stocks from the SQL database, so that it can be passed to sell.html
        portfolio = db.execute(
            "SELECT DISTINCT symbol FROM transactions WHERE user_id = ? ORDER BY symbol", (session["user_id"])
        )

        # Pass the aforementioned list of stocks to sell.html
        return render_template("sell.html", symbols = [row["symbol"] for row in portfolio])

    # If the user submitted the info via post, then run the following code:
    if request.method == "POST":
        # Pull in the user entry for the share they want to sell ("symbol") and the number of shares ("shares")
        symbol = str(request.form.get("symbol"))
        shares = int(request.form.get("shares"))

        # Will need to call the db again to check number of shares user requested to sell against the user's actual holdings.
        user_shares_num = db.execute(
            "SELECT SUM(txn_shrs) AS txn_shrs_summed FROM transactions WHERE user_id = ? AND symbol = ?", (session["user_id"]), symbol
        )
        user_shares_num_index = int(user_shares_num[0]["txn_shrs_summed"] or 0)

        # Check: User filled the boxes for symbol and shares?
        if not symbol.strip() or not shares:
            return apology("Apology: Please complete stock symbol and number of shares.", 400)

        # Check: User entered an integer for number of shares?
        elif (type(shares)) != int:
            return apology("Apology: Please enter a integer for number of shares", 400)

        # Check 3: User entered positive integer?
        elif shares < 1:
            return apology("Apology: Please enter a positive integer for number of shares", 400)

        # Check 4: User has enough shares to sell?
        elif shares > user_shares_num_index:
            return apology("Apology: You cannot sell more shares than you own", 400)

        # Passed all checks- proceed
        # Get current date and time, needed for txn timestamp
        timestamp = datetime.now()

        # Use lookup to get the price of the stock.
        price_sld = (lookup(symbol))["price"]

        # Calculate the total transaction value.
        txn_value = -shares * price_sld

        # Add new entry into the transaction table to represent the share purchase.
        # Note the negative value. This is to ensure that the total value of share holdings and cash are incremented appropriately.
        shares_neg = int(shares) * -1
        db.execute(
            "INSERT INTO transactions (user_id, txn_date, txn_type, symbol, txn_shrs, txn_shr_price, txn_value) VALUES(?, ?, ?, ?, ?, ?, ?)", session["user_id"], timestamp, "SLD", symbol, shares_neg, price_sld, txn_value
        )

        # Reduce cash on hand by amount of stock purchase.
        cash_on_hand = float(db.execute(
            "SELECT cash FROM users WHERE id = (?)", session["user_id"])[0]["cash"]
        )

        db.execute(
            "UPDATE users SET cash = (?) WHERE id = (?)", cash_on_hand - txn_value, session["user_id"]
        )

        # Flash an indication to the user that the share sale was successful and then redirect to index.
        flash("Share sale processed successfully!")
        time.sleep(3)
        return redirect("/")


if __name__ == '__main__': 
    app.run(host="0.0.0.0", port=port)