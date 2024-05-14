from flask import Flask, flash, redirect, render_template, request, session, g, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import pyodbc
from config import DATABASE_CONFIG

# Configure application
app = Flask(__name__)


def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={DATABASE_CONFIG['driver']};SERVER={DATABASE_CONFIG['server']};DATABASE={DATABASE_CONFIG['database']};UID={DATABASE_CONFIG['username']};PWD={DATABASE_CONFIG['password']}"
    )


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def get_list_of_dict(keys, list_of_tuples):
    """
    This function will accept keys and list_of_tuples as args and return list of dicts
    """
    list_of_dict = [
        dict(zip(keys, values))
        for values in list_of_tuples
    ]
    return list_of_dict

@app.route("/")
#@login_required
def index():
    # Connect to DB
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT category, COUNT(*) AS count
    FROM products
    GROUP BY category
    """)

    results = cursor.fetchall()

    keys = ("category", "count")

    list_of_results = get_list_of_dict(keys, results)

    connection.close()
    
    df = pd.DataFrame(list_of_results, columns=['category', 'count'])

    fig = px.pie(df, values='count', names='category', labels={'category': 'Kategori', 'count': 'Antal produkter'}, title='Produkt Kategori Distribution')

    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="#293251",
        plot_bgcolor="#37414e",
        font=dict(color='white', size = 9),  # Set the color of all text to white
        title=dict(font=dict(color='white')),  # Set the color of the title text to white
        xaxis=dict(title=dict(font=dict(color='white'))),  # Set the color of the x-axis title text to white
        yaxis=dict(title=dict(font=dict(color='white'))),  # Set the color of the y-axis title text to white
        legend=dict(title=dict(font=dict(color='white')), font=dict(color='white')),  # Set the color of legend text to white
    )

    graph_json = fig.to_json()


    return render_template("index.html", graph_json=graph_json)


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
        connection = get_db_connection()
        cursor = connection.cursor()
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
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
# Define your route for the product page
@app.route('/products/<product_code>')
def product_page(product_code):
    # Connect to DB
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query database for product
    product = cursor.execute("SELECT * FROM products WHERE product_code = ?", (product_code,)).fetchone()
    if product is None:
        connection.close()
        return apology("Product not found", 404)
    
    # Convert product tuple to dictionary
    product_dict = {
        'id': product[0],
        'product_name': product[1],
        'weight': product[2],
        'max_price': product[3],
        'min_price': product[4],
        'category': product[5],
        'product_code': product[6]
}
    
    priceHistory = cursor.execute("SELECT * FROM price_history WHERE product_id = ?", (product_dict['id'],)).fetchall()

    connection.close()
    priceHistory_list = []
    # Convert price history to dictionary or list of dictionaries based on length
    for row in priceHistory:
        priceHistory_list.append({
        'id': row[0],
        'product_id': row[1],
        'price': row[2],
        'currency': row[3],
        'unit': row[4],
        'date': row[5]
        })

    # Calculate average price
    average_price = round(sum(row['price'] for row in priceHistory_list) / len(priceHistory_list),2)

    # Calculate the dates for different time periods
    current_date = datetime.now().date()
    seven_days_ago = current_date - timedelta(days=7)
    fourteen_days_ago = current_date - timedelta(days=14)
    thirty_days_ago = current_date - timedelta(days=30)

    current_price = "N/A"
    price_7_days_ago = "N/A"
    price_14_days_ago = "N/A"
    price_30_days_ago = "N/A"
    price_percentage_7_days = "N/A"
    price_percentage_14_days = "N/A"
    price_percentage_30_days = "N/A"
    price_change_7_days = "N/A"
    price_changes_14_days = "N/A"
    price_changes_30_days = "N/A"

    for row in priceHistory_list:
        if row['date'] == current_date:
            current_price = row['price']

        if row['date'] == seven_days_ago:
            price_7_days_ago = row['price']

        if row['date'] == fourteen_days_ago:
            price_14_days_ago = row['price']

        if row['date'] == thirty_days_ago:
            price_30_days_ago = row['price']


    # Calculate price changes for different time periods
    if current_price != "N/A":
        if price_7_days_ago != "N/A":
            price_change_7_days = current_price - price_7_days_ago
            price_percentage_7_days = round_float_to_one_decimals(((current_price-price_7_days_ago)/price_7_days_ago)*100)
        if price_14_days_ago != "N/A":
            price_changes_14_days = current_price - price_14_days_ago
            price_percentage_14_days = round_float_to_one_decimals(((current_price-price_14_days_ago)/price_14_days_ago)*100)
        if price_30_days_ago != "N/A":
            price_changes_30_days = current_price - price_30_days_ago
            price_percentage_30_days = round_float_to_one_decimals(((current_price-price_30_days_ago)/price_30_days_ago)*100)

    # Create a dictionary with all the values
    product_metrics = {
        "current_price": current_price,
        "all_time_high": product_dict['max_price'],
        "all_time_low": product_dict['min_price'],
        "average_price": average_price,
        "price_change_7_days": price_change_7_days,
        "price_percentage_7_days" : price_percentage_7_days,
        "price_change_14_days": price_changes_14_days,
        "price_percentage_14_days" : price_percentage_14_days,
        "price_change_30_days": price_changes_30_days,
        "price_percentage_30_days" : price_percentage_30_days
    }

    df = pd.DataFrame(priceHistory_list)

    fig = px.line(df, x='date', y='price', labels={'price': 'Pris (kr)', 'date' : 'Datumn'}, title=f'{dict(product_dict)['product_name']} Pris över tid')

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
    return render_template('specificProduct.html', graph_json=graph_json, product=product_dict, price_history=priceHistory_list, product_metrics=product_metrics)

@app.route('/products/category/<category>', methods=['GET', 'POST'])
def category(category):
    if request.method == 'POST':
        # Get the selected category from the form
        selected_category = request.form['category']
        # Redirect to a new route with the selected category as parameter
        return redirect(url_for('category', category=selected_category))

    # Connect to DB
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query database for products where the category column contains the specified category
    query = "SELECT * FROM products WHERE category LIKE ?"
    products = cursor.execute(query, ('%' + category + '%',)).fetchall()

    # Ensure products were found
    if not products:
        return apology("No products found in the specified category", 400)
    

    product_keys = ("id", "product_name", "weight", "max_price", "min_price", "category", "product_code")
    product_list = get_list_of_dict(product_keys, products)


    current_date = datetime.now().date()
    # Fetch price history for each product
    price_history = []
    for product in product_list:
        history = cursor.execute("SELECT * FROM price_history WHERE product_id = ? AND date = ?", (product['id'], current_date,)).fetchall()
        price_history.extend(get_list_of_dict(("id", "product_id", "price", "currency", "unit", "date"), history))

    # Ensure price history was found
    if not price_history:
        return apology("No price history found for the products in the specified category", 400)
    
    price_stats = []
    for product in product_list:
        item = cursor.execute("SELECT * FROM price_history WHERE product_id = ?", (product['id'],)).fetchall()
        price_stats.extend(get_list_of_dict(("id", "product_id", "price", "currency", "unit", "date"),item))

    if not price_stats:
        return apology("No price history found for the products in the specified category", 400)
    
    seven_days_ago = current_date - timedelta(days=7)
    fourteen_days_ago = current_date - timedelta(days=14)
    thirty_days_ago = current_date - timedelta(days=30)

    current_price = "N/A"
    price_7_days_ago = "N/A"
    price_14_days_ago = "N/A"
    price_30_days_ago = "N/A"
    price_percentage_7_days = "N/A"
    price_percentage_14_days = "N/A"
    price_percentage_30_days = "N/A"

    for row in price_stats:
        if row['date'] == current_date:
            current_price = row['price']
        if row['date'] == seven_days_ago:
            price_7_days_ago = row['price']
        if row['date'] == fourteen_days_ago:
            price_14_days_ago = row['price']
        if row['date'] == thirty_days_ago:
            price_30_days_ago = row['price']

    # Calculate price changes for different time periods
    if current_price != "N/A":
        if price_7_days_ago != "N/A":
            price_percentage_7_days = round_float_to_one_decimals(((current_price-price_7_days_ago)/price_7_days_ago)*100)
        if price_14_days_ago != "N/A":
            price_percentage_14_days = round_float_to_one_decimals(((current_price-price_14_days_ago)/price_14_days_ago)*100)
        if price_30_days_ago != "N/A":
            price_percentage_30_days = round_float_to_one_decimals(((current_price-price_30_days_ago)/price_30_days_ago)*100)


    # Create a dictionary with all the values
    category_metrics = {
        "price_percentage_7_days" : price_percentage_7_days,
        "price_percentage_14_days" : price_percentage_14_days,
        "price_percentage_30_days" : price_percentage_30_days
    }

    product_info_data  = cursor.execute("""
    SELECT id, product_name
    FROM products
    WHERE category LIKE ?
    """, ('%' + category + '%',)).fetchall()

    product_info_keys = ("id", "product_name")
    product_info_list = get_list_of_dict(product_info_keys, product_info_data)

    price_history_data = []
    for product in product_info_list:
        history = cursor.execute("SELECT product_id, price, date FROM price_history WHERE product_id = ?", (product['id'],)).fetchall()
        price_history_data.extend(get_list_of_dict(("product_id", "price", "date"),history))
        product['product_name'] = f"{product['product_name']} (ID: {product['id']})"

    connection.close()

    # Convert fetched data to DataFrames
    product_info_df = pd.DataFrame(product_info_list, columns=['id', 'product_name'])
    price_history_df = pd.DataFrame(price_history_data, columns=['product_id', 'date', 'price'])

    # Merge product information with price history
    merged_df = pd.merge(price_history_df, product_info_df, left_on='product_id', right_on='id')

    # Plot prices over time using Plotly Express
    fig = px.line(merged_df, x='date', y='price', color='product_name',
              labels={'date': 'Datumn', 'price': 'Pris (kr)', 'product_name': 'Produkt'}, title='Prisutveckling av kategorins produkter över tid')


    # Convert fetched data into dictionaries
    data_price_history = [dict(row) for row in price_history]

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

    return render_template('category.html', graph_json=graph_json, products=products, price_history=data_price_history, category_metrics=category_metrics)

def round_float_to_one_decimals(num):
    # Convert the float to a string
    num_str = str(num)
    # Find the index of the dot (".") character
    dot_index = num_str.find(".")
    if dot_index != -1:  # Check if dot exists in the string
        # Slice the string up to two characters after the dot index
        rounded_str = num_str[:dot_index + 2]
        # Convert the rounded string back to float and return
        return float(rounded_str)
    else:
        # If there's no dot, just return the original number
        return float(num)



@app.route("/products", methods=['GET', 'POST'])
def product():
    if request.method == 'POST':
        # Get the selected category from the form
        selected_category = request.form['category']
        # Redirect to a new route with the selected category as parameter
        return redirect(url_for('category', category=selected_category))
    
    # Connect to DB
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query database for products and prices
    products = cursor.execute("SELECT * FROM products").fetchall()
    priceHistory = cursor.execute("SELECT * FROM price_history WHERE date = ?", (datetime.now().date(),)).fetchall()



    # Ensure Data was not empty
    if not priceHistory or not products:
        return apology("no products found", 400)

    # Convert each row of products into dictionaries
    dataProducts = [dict(zip(('id', 'product_name', 'quantity', 'price', 'price_per_unit', 'category', 'product_code'), product)) for product in products]

    # Convert each row of priceHistory into dictionaries
    dataPriceHistory = [dict(zip(('id', 'product_id', 'price', 'currency', 'unit', 'date'), price)) for price in priceHistory]


    # Create a dictionary to map product IDs to product names
    product_id_to_name = {item['id']: item['product_name'] for item in dataProducts}

    # Assign product names to dataPriceHistory items based on their product IDs
    for d in dataPriceHistory:
        product_id = d['product_id']
        product_name = product_id_to_name.get(product_id, 'Unknown Product')
        d['name'] = f"{product_name} (ID: {product_id})"  # Append product ID to the product name


    df = pd.DataFrame(dataPriceHistory)

    fig = px.bar(df, x='name', y='price', labels={'price': 'Pris (kr)', 'name' : 'Namn'}, title='Nuvarande pris för samtliga produkter')

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


    total_prices = cursor.execute("SELECT * FROM total_price").fetchall()
    total_price_history = [dict(zip(('id', 'value', 'date'), price)) for price in total_prices]

    connection.close()

        # Ensure Data was not empty
    if not total_prices:
        return apology("no total prices found", 400)

        # Find all-time high and all-time low prices
    all_time_high = max(row['value'] for row in total_price_history)
    all_time_low = min(row['value'] for row in total_price_history)

    # Calculate average price
    average_price = round(sum(row['value'] for row in total_price_history) / len(total_price_history),2)

    # Calculate the dates for different time periods
    current_date = datetime.now().date()

    seven_days_ago = current_date - timedelta(days=7)
    fourteen_days_ago = current_date - timedelta(days=14)
    thirty_days_ago = current_date - timedelta(days=30)

    current_price = "N/A"
    price_7_days_ago = "N/A"
    price_14_days_ago = "N/A"
    price_30_days_ago = "N/A"
    price_percentage_7_days = "N/A"
    price_percentage_14_days = "N/A"
    price_percentage_30_days = "N/A"

    for row in total_price_history:
        if row['date'] == current_date:
            current_price = row['value']
        if row['date'] == seven_days_ago:
            price_7_days_ago = row['value']
        if row['date'] == fourteen_days_ago:
            price_14_days_ago = row['value']
        if row['date'] == thirty_days_ago:
            price_30_days_ago = row['value']

    # Calculate price changes for different time periods
    if current_price != "N/A":
        if price_7_days_ago != "N/A":
            price_percentage_7_days = round_float_to_one_decimals(((current_price-price_7_days_ago)/price_7_days_ago)*100)
        if price_14_days_ago != "N/A":
            price_percentage_14_days = round_float_to_one_decimals(((current_price-price_14_days_ago)/price_14_days_ago)*100)
        if price_30_days_ago != "N/A":
            price_percentage_30_days = round_float_to_one_decimals(((current_price-price_30_days_ago)/price_30_days_ago)*100)


    # Create a dictionary with all the values
    total_metrics = {
        "all_time_high": all_time_high,
        "all_time_low": all_time_low,
        "average_price": average_price,
        "price_percentage_7_days" : price_percentage_7_days,
        "price_percentage_14_days" : price_percentage_14_days,
        "price_percentage_30_days" : price_percentage_30_days
    }

    dataframe = pd.DataFrame(total_price_history)

    fig2 = px.line(dataframe, x='date', y='value', labels={'price': 'Pris (kr)', 'value' : 'Värde', 'date' : 'Datumn'}, title= 'Total summa av samtliga produktpriser som spåras över tid')

    fig2.update_layout(
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

    graph2_json = fig2.to_json()

    return render_template('products.html', graph_json=graph_json, graph2_json=graph2_json, products=products, price_history=priceHistory, total_metrics=total_metrics)

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
        connection = get_db_connection()
        cursor = connection.cursor()

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

        connection.close()
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)  # Run the app on all available network interfaces
