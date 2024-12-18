from datetime import datetime, timedelta
import pyodbc
from config import DATABASE_CONFIG

def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={DATABASE_CONFIG['driver']};SERVER={DATABASE_CONFIG['server']};DATABASE={DATABASE_CONFIG['database']};UID={DATABASE_CONFIG['username']};PWD={DATABASE_CONFIG['password']}"
    )


# Function to add a new price for an existing product
def add_price_for_product(product_name, price, currency, date, unit, product_code):
    product_id = get_product_id(product_code)
    
    if product_id is not None:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

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


        cursor.execute('''SELECT * FROM price_history WHERE product_id = ? ORDER BY date DESC''',(product_id,))

        latest_record = cursor.fetchone()

        if float(price) == float(latest_record[2]):
            print("Same value as last entry, not pushing to database.")
        else:
            cursor.execute('''INSERT INTO price_history (product_id, price, currency, date, unit)
                    VALUES (?, ?, ?, ?, ?)''', (product_id, price, currency, date, unit))

        conn.commit()
        conn.close()
    else:
        print(f"Product '{product_name}' not found.")

# Function to create a new product in the products table
def create_product(product_name, weight, max_price, min_price, product_code, category):
    conn = get_db_connection()
    cursor = conn.cursor()

    product_id = get_product_id(product_code)
    if product_id is None:
        # Insert the new product into the products table
        cursor.execute('''INSERT INTO products (product_name, weight, max_price, min_price, category, product_code) VALUES (?, ?, ?, ?, ?, ?)''', (product_name, weight, max_price, min_price, category, product_code,))
        conn.commit()
        conn.close()
        print("Product created successfully.")
    else:
        conn.commit()
        conn.close()



# Function to fetch the product_id based on the product name and store name
def get_product_id(product_code):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a SELECT query to retrieve the product_id
    cursor.execute('''SELECT id FROM products WHERE product_code = ?''', (product_code,))
    row = cursor.fetchone()
    conn.close()

    # If product_id exists, return it; otherwise, return None
    return row[0] if row else None


# Function to query and print all records from the database
def print_all_records():
    conn = get_db_connection()
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

    # Query and print all records from the total_price table
    print("\nTotal price History:")
    cursor.execute('''SELECT * FROM total_price''')
    for row in cursor.fetchall():
        print(row)

    conn.close()

def check_exists_for_current_date(product_id, date):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(''' SELECT * FROM price_history WHERE product_id = ? AND date = ?''', (product_id, date) )

        # If any rows are returned, it means there's a match
        rows = cursor.fetchall()
        conn.close()
        if len(rows)>0:
            return False
        return True

def create_total_price():
    current_date = datetime.now().date()

    # Create total price for all products
    conn = get_db_connection()
    cursor = conn.cursor()

    item = cursor.execute('''SELECT * FROM total_price WHERE date = ?''', (current_date,)).fetchall()

    if len(item) == 0:
        total_sum = 0
        products = cursor.execute('''SELECT * FROM products''').fetchall()

        for product in products:
            price = cursor.execute('''SELECT * FROM price_history WHERE product_id = ? ORDER BY date DESC''',(product[0],)).fetchone()
            if price:
                total_sum += price[2]
            else:
                print("No previous price was found.")
                
        cursor.execute('''INSERT INTO total_price (value, date) VALUES (?, ?)''', (total_sum, current_date,))

        conn.commit()
        conn.close()
        print('Total price for:', current_date , "was" , round(total_sum, 2) , "kr")
    else:
        print("Total price already exists for this day.")
        conn.close()


#Import in other python file