import sqlite3
from datetime import datetime

# Function to add a new price for an existing product
def add_price_for_product(product_name, price, pushed_date):
    product_id = get_product_id(product_name)
    if product_id is not None:

        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO price_history (product_id, price, pushed_date)
                      VALUES (?, ?, ?)''', (product_id, price, pushed_date))

        conn.commit()
        conn.close()
    else:
        print(f"Product '{product_name}' not found.")

# Function to create a new product in the products table
def create_product(product_name):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Insert the new product into the products table
    cursor.execute('''INSERT INTO products (product_name) VALUES (?)''', (product_name,))

    conn.commit()
    conn.close()


# Function to fetch the product_id based on the product name
def get_product_id(product_name):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Execute a SELECT query to retrieve the product_id
    cursor.execute('''SELECT id FROM products WHERE product_name = ?''', (product_name,))
    row = cursor.fetchone()
    conn.close()

    # If product_id exists, return it; otherwise, return None
    return row[0] if row else None


# Function to query and print all records from the database
def print_all_records():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()

    # Query and print all records from the products table
    print("Products:")
    cursor.execute('''SELECT * FROM products''')
    for row in cursor.fetchall():
        print(row)

    # Query and print all records from the price_history table
    print("\nPrice History:")
    cursor.execute('''SELECT * FROM price_history''')
    for row in cursor.fetchall():
        print(row)

    conn.close()


#Import in other python file