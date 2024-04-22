from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, lookupExtended

import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pandas_market_calendars as mcal


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
    """Show portfolio of stocks"""
    stock_balance = 0
    stocks = db.execute(
        "SELECT symbol, (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions WHERE user_id = ? GROUP BY symbol HAVING net_holdings > 0;", session["user_id"])
    
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.Timedelta(days=1)
    market_dates_nyse = get_market_dates(start_date, end_date)
    market_dates_eurex = get_market_dates(start_date, end_date, 'EUREX')

    total_weighted_development = {}
    total_weighted_development['value'] = 0
    total_weighted_development['percentage'] = 0
    total_weight = 0
    overall_development = {}

    for stock in stocks:
        x = 0
        if pd.to_datetime('today') not in market_dates_nyse or pd.to_datetime('today') not in market_dates_eurex:
            x = 1
            stock_lookup = (lookupExtended(stock['symbol'], x))
            while stock_lookup == None:
                x += 1
                stock_lookup = (lookupExtended(stock['symbol'], x))
        else:
            stock_lookup = (lookupExtended(stock['symbol'], x))
        stock['price_per_stock'] = float(stock_lookup[0]["Adj Close"])
        stock['price_total'] = round(stock['price_per_stock'] * int(stock['net_holdings']), 2)
        stock['price_opening'] = float(stock_lookup[0]["Open"])
        stock_balance += stock['price_total']

        stock['development_value'] = round((stock['price_per_stock'] - stock['price_opening']), 2)
        stock['development_percentage'] = round(((stock['price_per_stock'] - stock['price_opening'] ) / stock['price_per_stock'] * 100), 2)

        # Accumulate the weighted development
        total_weighted_development['value'] += (stock['development_value'] * stock['net_holdings'])
        total_weighted_development['percentage'] += stock['price_total'] * stock['development_percentage']
        total_weight += stock['price_total']

        stock['price_per_stock'] = round(stock['price_per_stock'], 2)

    # Calculate the overall development using the weighted average formula
    overall_development['value'] = round(total_weighted_development['value'], 2)
    overall_development['percentage'] = round(total_weighted_development["percentage"] / total_weight if total_weight > 0 else 0, 2)

    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    account_balance = rows[0]["cash"]
    total_balance = account_balance + stock_balance
    return render_template("index.html", stocks=stocks, stock_balance=usd(stock_balance), total_balance=usd(total_balance), overall_development=overall_development)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # return render_template("buy.html")
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not symbol:
            return apology("Missing Stock", 400)
        elif not lookup(symbol):
            return apology("Stock does not exist", 400)
        elif not shares:
            return apology("No Shares selected", 400)
        try:
            shares = int(shares)
            if not isinstance(shares, int):
                return apology("Please select an positive integer", 400)
            elif shares < 0:
                return apology("Please select an positive integer", 400)
        except:
            return apology("Please select an positive integer", 400)
        
        price = shares * float(lookup(symbol)["price"])

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        account_balance = rows[0]["cash"]

        if account_balance < price:
            return apology("Not enough balance for transaction", 400)
        
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, 'BUY');", 
                   session["user_id"], symbol, shares, price)
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?;", price, session["user_id"])
        session["cash"] = usd(rows[0]["cash"] - shares * int(lookup(symbol)["price"]))

        return render_template("buy.html", symbol=lookup(symbol)["name"], pricePerShare=usd(lookup(symbol)["price"]), shares=shares, price=usd(price))
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transacted_at DESC;", session["user_id"])
    for transaction in transactions:
        transaction['price_total'] = transaction['shares'] * transaction['price']
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["cash"] = usd((rows[0]["cash"]))
        session['username'] = rows[0]["username"]
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
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Missing Stock", 400)
        elif not lookup(symbol):
            return apology("Stock does not exist", 400)
        
        data = lookupExtended(symbol, 365)
        # Check if the data DataFrame is empty
        if not data:
            return apology("No data available for the specified symbol", 200)
        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data)
        # Convert the 'Date' column to datetime format
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Convert the 'Close' column to numeric format
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        percentage_change = {}
        value_change = {}
        value_change["one_year"], percentage_change["one_year"] = calculate_change(df, 365)
        value_change["six_months"], percentage_change["six_months"] = calculate_change(df, 183)
        value_change["three_months"], percentage_change["three_months"] = calculate_change(df, 91)
        value_change["one_month"], percentage_change["one_month"] = calculate_change(df, 30)
        value_change["one_week"], percentage_change["one_week"] = calculate_change(df, 7)
        value_change["one_day"], percentage_change["one_day"] = calculate_change(df, 1)
        fig = create_stock_price_chart(df, symbol)

        # Convert the Plotly JSON to a string and pass it to the template
        graph_json = fig.to_json()
        return render_template("quote.html", symbol=lookup(symbol)["name"], price=usd(lookup(symbol)["price"]), graph_json=graph_json, development_value=value_change, development_percentage=percentage_change)
    else:
        stocks = db.execute("SELECT symbol, (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions GROUP BY symbol HAVING net_holdings > 0 ORDER BY net_holdings DESC LIMIT 10;")
        return render_template("quote.html", stocks=stocks)

def create_stock_price_chart(df, symbol):
    # Plotting with Plotly Express
    fig = px.line(df, x='Date', y='Close', labels={'Close': 'Closing Price'}, title=f'{symbol} Stock Price Over Time')

    #Fixes hover for date and price
    fig.update_traces(hovertemplate='%{y:.2f} USD<br>%{x|%Y-%m-%d}')

    # Make the chart responsive
    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="#212529",
        plot_bgcolor="#37414e",
        font=dict(color='white'),  # Set the color of all text to white
        title=dict(font=dict(color='white')),  # Set the color of the title text to white
        xaxis=dict(title=dict(font=dict(color='white'))),  # Set the color of the x-axis title text to white
        yaxis=dict(title=dict(font=dict(color='white'))),  # Set the color of the y-axis title text to white
        legend=dict(title=dict(font=dict(color='white')), font=dict(color='white')),  # Set the color of legend text to white
    )

    # Example: Customize line appearance
    fig.update_traces(line=dict(color='#00ccff', width=2, dash='solid'))

    # Example: Customize axis labels and title
    fig.update_layout(xaxis_title='Date', yaxis_title='Closing Price (USD)', title=f'{symbol} Stock Price Over Time')

    return fig

def get_market_dates(start_date, end_date, symbol="XNYS"):
    nyse = mcal.get_calendar(symbol)
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    market_dates = schedule.index
    return market_dates

def get_data_for_dates(df, timeframe):
    # Get market dates for the desired timeframe
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.Timedelta(days=timeframe)
    market_dates = get_market_dates(start_date, end_date)

    # Filter data based on market dates
    filtered_data = df[df['Date'].isin(market_dates)]
    return filtered_data

def calculate_change(df, timeframe):
    # Convert necessary columns to numeric
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['Adj Close'] = pd.to_numeric(df['Adj Close'], errors='coerce')

    filtered_data = get_data_for_dates(df, timeframe)
    x = 0
    while len(filtered_data) < 1:
        # Get market dates for the desired timeframe
        x += 1
        filtered_data = get_data_for_dates(df, timeframe+x)

    while len(filtered_data) > 1 and len(filtered_data) < 5:
        # Get market dates for the desired timeframe
        x += 1
        filtered_data = get_data_for_dates(df, timeframe+x)

    # Check if there is enough data for calculation
    if len(filtered_data) < 2:
        percentage_change = ((filtered_data['Adj Close'].iloc[0] - filtered_data['Open'].iloc[-1]) / filtered_data['Adj Close'].iloc[-1]) * 100
        value_change = filtered_data['Adj Close'].iloc[0] - filtered_data['Open'].iloc[-1]
    else:
        # Calculate percentage change
        percentage_change = ((filtered_data['Adj Close'].iloc[0] - filtered_data['Open'].iloc[-1]) / filtered_data['Adj Close'].iloc[-1]) * 100
        value_change = filtered_data['Adj Close'].iloc[0] - filtered_data['Open'].iloc[-1]


    return round(value_change, 2), round(percentage_change, 2)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        
        # Ensure password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide repassword", 400)
        
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords does not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        #   if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #       return apology("invalid username and/or password", 403)
        if len(rows) == 1:
            return apology("Username already exists", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", 
                   request.form.get("username"), generate_password_hash(request.form.get("password")))
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["cash"] = usd((rows[0]["cash"]))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # return render_template("buy.html")
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("Missing Stock", 400)
        elif not lookup(symbol):
            return apology("Stock does not exist", 400)
        elif not shares:
            return apology("No Shares selected", 400)
        try:
            shares = int(shares)
            if not isinstance(shares, int):
                return apology("Please select an positive integer", 400)
            elif shares < 0:
                return apology("Please select an positive integer", 400)
        except:
            return apology("Please select an positive integer", 400)
        
        price = shares * float(lookup(symbol)["price"])

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        account_balance = rows[0]["cash"]

        stock = db.execute(
            "SELECT (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol HAVING net_holdings > 0;", session["user_id"], symbol)
        try:
            stock[0]['net_holdings']
        except:
            return apology("Not enough shares for transaction", 400)
        if int(stock[0]['net_holdings']) < shares:
            return apology("Not enough shares for transaction", 400)
        
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, transaction_type) VALUES (?, ?, ?, ?, 'SELL');", 
                   session["user_id"], symbol, shares, price)
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?;", price, session["user_id"])
        session["cash"] = usd(rows[0]["cash"] + shares * int(lookup(symbol)["price"]))

        return render_template("sell.html", symbol=lookup(symbol)["name"], pricePerShare=usd(lookup(symbol)["price"]), shares=shares, price=usd(price))
    else:
        stocks = db.execute(
            "SELECT symbol, (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions WHERE user_id = ? GROUP BY symbol HAVING net_holdings > 0;", session["user_id"])
        return render_template("sell.html", stocks=stocks)

@app.route("/leaderboard")
@login_required
def leaderboard():
    current_user_username = db.execute("SELECT username FROM users WHERE id = ?;", session["user_id"])
    users_balance = get_total_balance()
    for user in users_balance:
        user["total_balance"] = usd(user["total_balance"])
    return render_template("leaderboard.html", current_user_username=current_user_username, users_balance=users_balance)

def get_total_balance():
    """Get total balance for all users with percentage and difference"""
    users_balance = []

    users = db.execute("SELECT id, username, cash FROM users")

    current_user_id = session["user_id"]
    current_user_total_balance = db.execute("SELECT cash FROM users WHERE id = ?", current_user_id)[0]["cash"]

    # Create a dictionary to store stock prices for each symbol
    stock_prices = {stock['symbol']: lookup(stock['symbol'])['price'] for stock in db.execute("SELECT DISTINCT symbol FROM transactions")}

    # Calculate total stock value for all users
    total_stock_value = 0

    for user_id in [user["id"] for user in users]:
        stocks = db.execute(
            "SELECT symbol, (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions WHERE user_id = ? GROUP BY symbol HAVING net_holdings > 0;",
            user_id
        )

        for stock in stocks:
            total_stock_value += stock_prices.get(stock['symbol'], 0) * stock['net_holdings']
        if user_id == current_user_id:
            current_user_total_balance += total_stock_value

    # Calculate total net worth including cash and stock portfolio for each user
    total_net_worth = db.execute("SELECT SUM(cash) FROM users")[0]["SUM(cash)"] + total_stock_value

    for user in users:
        stock_balance = 0

        stocks = db.execute(
            "SELECT symbol, (SUM(CASE WHEN transaction_type = 'BUY' THEN shares ELSE 0 END) - SUM(CASE WHEN transaction_type = 'SELL' THEN shares ELSE 0 END)) AS net_holdings FROM transactions WHERE user_id = ? GROUP BY symbol HAVING net_holdings > 0;",
            user["id"]
        )

        for stock in stocks:
            stock_balance += stock_prices.get(stock['symbol'], 0) * stock['net_holdings']

        account_balance = user["cash"]
        total_balance = account_balance + stock_balance

        # Calculate the percentage
        if total_net_worth != 0:
            percentage = (total_balance / total_net_worth) * 100
        else:
            percentage = 0

        # Calculate the percentage difference
        if current_user_id != user["id"]:
            difference_percentage = ((total_balance - current_user_total_balance) / current_user_total_balance * 100)
        else:
            difference_percentage = 0  # Current user, no difference

        user_balance = {
            "username": user["username"],
            "account_balance": account_balance,
            "stock_balance": stock_balance,
            "total_balance": total_balance,
            "percentage": round(percentage, 2),
            "difference_percentage": round(difference_percentage, 2)  # Round to two decimal places
        }

        users_balance.append(user_balance)

     # Sort users by total_balance in descending order
    users_balance = sorted(users_balance, key=lambda x: x["total_balance"], reverse=True)

    # Assign rankings
    for i, user_balance in enumerate(users_balance):
        user_balance["ranking"] = i + 1

    return users_balance
