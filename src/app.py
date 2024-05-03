from flask import Flask, flash, redirect, render_template, request, session, g, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import sqlite3

# Configure application
app = Flask(__name__)

# DB File configure
from dbConfig import configure_database

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DATABASE"] = "site.db"
Session(app)

# Configure Database if not setup
configure_database(app.config['DATABASE'])

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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

        # Connect to DB
        cursor = get_db().cursor()
        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session['username'] = rows[0]["username"]
        # Redirect user to home page
        return redirect("/products")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
# Define your route for the product page
@app.route('/products/<product_code>')
def product_page(product_code):
    # Connect to DB
    cursor = get_db().cursor()

    # Query database for products and prices
    product = cursor.execute("SELECT * FROM products WHERE product_code = ?", (product_code,)).fetchone()
    if product:
        priceHistory = cursor.execute("SELECT * FROM price_history WHERE product_id = ?", (product['id'],)).fetchall()


    # Return dictionarie with data of price_history
    dataPriceHistory = []
    for row in priceHistory:
        dataPriceHistory.append(dict(row))

    for dictionary in dataPriceHistory:
        if 'pushed_date' in dictionary:
            value = dictionary.pop('pushed_date')
            dictionary['date'] = value

    df = pd.DataFrame(dataPriceHistory)

    fig = px.line(df, x='date', y='price', labels={'price': 'price'}, title=f'{dict(product)['product_name']} Price Over Time')

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

    # and render the corresponding template
    return render_template('specificProduct.html', graph_json=graph_json, product=product, price_history=priceHistory)

@app.route('/products/category/<category>')
def category(category):
    # Connect to DB
    cursor = get_db().cursor()

    # Query database for products where the category column contains the specified category
    query = "SELECT * FROM products WHERE category LIKE ?"
    products = cursor.execute(query, ('%' + category + '%',)).fetchall()

    # Ensure products were found
    if not products:
        return apology("No products found in the specified category", 400)

    # Fetch price history for each product
    price_history = []
    for product in products:
        history = cursor.execute("SELECT * FROM price_history WHERE product_id = ?", (product['id'],)).fetchall()
        price_history.extend(history)

    # Ensure price history was found
    if not price_history:
        return apology("No price history found for the products in the specified category", 400)

    # Convert fetched data into dictionaries
    data_products = [dict(product) for product in products]
    data_price_history = [dict(row) for row in price_history]

    # Assign product names to price history data
    for d in data_price_history:
        product_id = d['product_id']
        for item in data_products:
            if item['id'] == product_id:
                d['name'] = item['product_name']

    # Create DataFrame from price history data
    df = pd.DataFrame(data_price_history)

    # Plot graph using Plotly Express
    fig = px.bar(df, x='name', y='price', labels={'price': 'price (kr)'}, title=f'Products Price Over Time')

    # Update layout
    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="#212529",
        plot_bgcolor="#37414e",
        font=dict(color='white', size=9),  # Set font color and size
        title=dict(font=dict(color='white')),  # Set title font color
        xaxis=dict(title=dict(font=dict(color='white')), tickangle=45),  # Set x-axis font color and tick angle
        yaxis=dict(title=dict(font=dict(color='white'))),  # Set y-axis font color
        legend=dict(title=dict(font=dict(color='white')), font=dict(color='white')),  # Set legend font color
    )

    # Convert figure to JSON
    graph_json = fig.to_json()

    return render_template('category.html', graph_json=graph_json, products=products, price_history=data_price_history)



@app.route("/products", methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        # Get the selected category from the form
        selected_category = request.form['category']
        # Redirect to a new route with the selected category as parameter
        return redirect(url_for('category', category=selected_category))
    
    # Connect to DB
    cursor = get_db().cursor()

    # Query database for products and prices
    products = cursor.execute("SELECT * FROM products").fetchall()
    priceHistory = cursor.execute("SELECT * FROM price_history").fetchall()

    # Ensure Data was note empty
    if not priceHistory or not products:
        return apology("no products found", 400)

    # Return dictionarie with data of products
    dataProducts = []
    for product in products:
        dataProducts.append(dict(product))

    # Return dictionarie with data of price_history
    dataPriceHistory = []
    for row in priceHistory:
        dataPriceHistory.append(dict(row))

    # Names for the graphs
    for d in dataPriceHistory:
        product_id = d['product_id']
        for item in dataProducts:
            if item['id'] == product_id:
                d['name'] = item['product_name']


    df = pd.DataFrame(dataPriceHistory)

    fig = px.bar(df, x='name', y='price', labels={'price': 'price (kr)'}, title=f'{"Products"} Price Over Time')

    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="#212529",
        plot_bgcolor="#37414e",
        font=dict(color='white', size = 9),  # Set the color of all text to white
        title=dict(font=dict(color='white')),  # Set the color of the title text to white
        xaxis=dict(title=dict(font=dict(color='white')), tickangle = 45),  # Set the color of the x-axis title text to white
        yaxis=dict(title=dict(font=dict(color='white'))),  # Set the color of the y-axis title text to white
        legend=dict(title=dict(font=dict(color='white')), font=dict(color='white')),  # Set the color of legend text to white
    )

    graph_json = fig.to_json()

    return render_template('products.html', graph_json=graph_json, products=products, price_history=priceHistory)

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

        # Field input website
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password was submitted
        elif not confirmation:
            return apology("must provide repassword", 400)

        elif not confirmation == password:
            return apology("passwords does not match", 400)

        # DB Connect
        cursor = get_db().cursor()

        # Query database for username
        rows = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchall()

        if len(rows) == 1:
            return apology("Username already exists", 400)

        # Hash password
        hashedPassword = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   (username, hashedPassword))

        # Commit changes
        cursor.connection.commit()

        row = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        # Ensure that the query returned a row
        if row is not None:
            # Access the user's ID from the tuple using index 0
            user_id = row["id"]
            username = row["username"]
            # Store the user ID in the session
            session["user_id"] = user_id
            session["username"] = username
        else:
            # Handle the case where the user was not found
            return apology("Failed to fetch user information", 500)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

