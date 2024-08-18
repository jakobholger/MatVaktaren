#@app.route('/products/category/<category>', methods=['GET', 'POST'])
def category(category):

    # Connect to DB
    connection = get_db_connection()
    cursor = connection.cursor()

    # Query database for products where the category column contains the specified category
    products = cursor.execute("SELECT * FROM products WHERE category LIKE ?", ('%' + category + '%',)).fetchall()

    # Ensure products were found
    if not products:
        connection.close()
        return apology("No products found in the specified category", 400)
    
    product_list = get_list_of_dict(("id", "product_name", "weight", "max_price", "min_price", "category", "product_code"), products)

    current_date = datetime.now().date()
    # Fetch price history for each product to the table for prices (down right in html page)
    price_history = []
    for product in product_list:
        history = cursor.execute("SELECT * FROM price_history WHERE product_id = ? AND date = ?", (product['id'], current_date,)).fetchall()
        price_history.extend(get_list_of_dict(("id", "product_id", "price", "currency", "unit", "date"), history))

    # Ensure price history was found
    if not price_history:
        return apology("No price history found for the products in the specified category", 400)
    

    # Create a mapping from product_id to price_history entries for quick lookup
    data_price_map = {item['product_id']: item for item in price_history}

    combined_dict = []

    # Iterate through data_products and combine with matching entries from data_price_history
    for product in product_list:
        product_id = product['id']
        if product_id in data_price_map:
            combined_entry = {**product, **data_price_map[product_id]}
            combined_dict.append(combined_entry)
        else:
            print(f"Product ID {product_id} not found in data_price_map")  # Debug statement for missing keys

    price_stats = []
    for product in product_list:
        item = cursor.execute("SELECT * FROM price_history WHERE product_id = ?", (product['id'],)).fetchall()
        price_stats.extend(get_list_of_dict(("id", "product_id", "price", "currency", "unit", "date"),item))

    if not price_stats:
        return apology("No price history found for the products in the specified category", 400)
    
    yesterday = current_date - timedelta(days=1)
    seven_days_ago = current_date - timedelta(days=7)
    fourteen_days_ago = current_date - timedelta(days=14)
    thirty_days_ago = current_date - timedelta(days=30)

    current_price = 0
    price_yesterday = 0
    price_7_days_ago = 0
    price_14_days_ago = 0
    price_30_days_ago = 0
    price_percentage_yesterday = "N/A"
    price_percentage_7_days = "N/A"
    price_percentage_14_days = "N/A"
    price_percentage_30_days = "N/A"


    # This will return the prices for the last index in price_stats list. It should sum them up and compare to the prices for previous days.
    for row in price_stats:
        if row['date'] == current_date:
            current_price += row['price']
        if row['date'] == yesterday:
            price_yesterday += row['price']
        if row['date'] == seven_days_ago:
            price_7_days_ago += row['price']
        if row['date'] == fourteen_days_ago:
            price_14_days_ago += row['price']
        if row['date'] == thirty_days_ago:
            price_30_days_ago += row['price']

    # Calculate price changes for different time periods
    if current_price != 0:
        if price_yesterday != 0:
            price_percentage_yesterday = round_float_to_one_decimals(((current_price-price_yesterday)/price_yesterday)*100)
        if price_7_days_ago != 0:
            price_percentage_7_days = round_float_to_one_decimals(((current_price-price_7_days_ago)/price_7_days_ago)*100)
        if price_14_days_ago != 0:
            price_percentage_14_days = round_float_to_one_decimals(((current_price-price_14_days_ago)/price_14_days_ago)*100)
        if price_30_days_ago != 0:
            price_percentage_30_days = round_float_to_one_decimals(((current_price-price_30_days_ago)/price_30_days_ago)*100)

    category_title = ""

    if "|" in category:
        match category.split("|")[0]:
            case "mejeri-ost-och-agg":
                category_title = "Mejeri ost och ägg" + " - " + category.split("|")[1].replace("-", " ")
            
            case "fardigmat":
                category_title = "Färdigmat" + " - " + category.split("|")[1].replace("-", " ")

            case "kott-chark-och-fagel":
                category_title = "Kött chark och fågel" + " - " + category.split("|")[1].replace("-", " ")

            case "frukt-och-gront":
                category_title = "Frukt och grönt" + " - " + category.split("|")[1].replace("-", " ")

            case _:
                category_title = category.replace("-", " ").replace("|", " ").capitalize()
    else:
        match category:
            case "mejeri-ost-och-agg":
                category_title = "Mejeri ost och ägg"
            
            case "fardigmat":
                category_title = "Färdigmat"

            case "kott-chark-och-fagel":
                category_title = "Kött chark och fågel"

            case "frukt-och-gront":
                category_title = "Frukt och grönt"

            case _:
                category_title = category.replace("-", " ").capitalize()

    # Create a dictionary with all the values
    category_metrics = {
        "title":category_title,
        "price_percentage_yesterday": price_percentage_yesterday,
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
    fig = px.line(merged_df, x='date', y='price', color='product_name', markers=True,
              labels={'date': '', 'price': 'Pris (kr)', 'product_name': 'Produkt'}, title='Prisutveckling av kategorins produkter över tid')

    # Update layout
    fig.update_layout(
        autosize=True,
        margin=dict(l=10, r=10, t=40, b=5),
        paper_bgcolor="#293251",
        plot_bgcolor="#c9c8c3",
        title=dict(font=dict(color='white', size=10)),  # Set the color of the title text to white
        font=dict(color='white', size=9),  # Set the color of all text to white
        legend=dict(
            title=dict(font=dict(color='white')),  # Set the color of legend title text to white
            font=dict(color='white',
                      size=8),  # Set the color of legend text to white
            orientation='h',
    ),
    showlegend=True  # Show legend
    )
    # Convert figure to JSON
    graph_json = fig.to_json()

    return render_template('category.html', graph_json=graph_json, products=products, price_history=price_history, category_metrics=category_metrics, combined_dict=combined_dict)
