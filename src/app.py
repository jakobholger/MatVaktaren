from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import pandas_market_calendars as mcal


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

dbWeb = SQL("sqlite:///../webscraper/products.db")


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
    return render_template("index.html")


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
        session['username'] = rows[0]["username"]
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/product")
def product():

    products = dbWeb.execute("SELECT * FROM products")

    prices = dbWeb.execute("SELECT * FROM price_history")

    df = pd.DataFrame(prices)
    
    fig = px.line(df, x='pushed_date', y='price', labels={'price': 'price'}, title=f'{"Productname"} Product Price Over Time')

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

    graph_json = fig.to_json()
    
    return render_template('product.html', graph_json=graph_json, products=products, price_history=prices)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


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

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

