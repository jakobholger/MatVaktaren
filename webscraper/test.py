# Use this file to generate random simulated data for products.

# 1. Remove site.db from src and run 'flask --app app.py run --debug' to create the database.

# 2. Run main.py from webscraper once.

# 3. Run test.py from webscraper once.

# 4. Wait for data to generate. (Can take a minute!)


import sqlite3
import random
from datetime import datetime, timedelta

# Define Database File
dbFile = '../src/site.db'
conn = sqlite3.connect(dbFile)
# Enable row factory to fetch rows as dictionaries
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

days = 30


# Execute the query to fetch products
products = cursor.execute('''SELECT * FROM products''').fetchall()

# Iterate over each product
for product in products:
    product_code = product['product_code']
    # Generate prices for each day
    for i in range(1, days+1):
        product_id_result = cursor.execute('''SELECT id FROM products WHERE product_code = ?''', (product_code,)).fetchone()

        # Extract the product_id from the result tuple
        if product_id_result:
            product_id = product_id_result[0]
            price = random.randint(15,100)
            
            cursor.execute('''SELECT max_price, min_price FROM products WHERE id = ?''', (product_id,))
            row = cursor.fetchone()

            max_price = float(row[0])
            min_price = float(row[1])

            if float(price) > max_price:
                # Update max price
                cursor.execute('''UPDATE products SET max_price = ? WHERE id = ?''', (price, product_id))
            if float(price) < min_price:
                # Update min price
                cursor.execute('''UPDATE products SET min_price = ? WHERE id = ?''', (price, product_id))

            cursor.execute('''INSERT INTO price_history (product_id, price, currency, date, unit)
                VALUES (?, ?, ?, ?, ?)''', (product_id, price,  "kr", datetime.now().date() - timedelta(days=i), "test/test"))
        
for i in range(1, days+1):
    current_date = datetime.now().date() - timedelta(days=i)
    item = cursor.execute('''SELECT * FROM total_price WHERE date = ?''', (current_date,)).fetchall()

    prices = cursor.execute('''SELECT * FROM price_history WHERE date = ?''', (current_date,)).fetchall()

    total_sum = 0
    for price in prices:
        total_sum += price[2]

    cursor.execute('''INSERT INTO total_price (value, date) VALUES (?, ?)''', (total_sum, current_date,))
conn.commit()
conn.close()