import os
import sqlite3

def configure_database(dbFile):
    # Check if site.db exists
    if not os.path.exists(dbFile):
        open(dbFile, 'w').close()
        db=sqlite3.connect(dbFile)

        # Create tables
        db.execute('''CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            product_name TEXT,
            weight TEXT,
            category TEXT,
            product_code TEXT
        )''')
        db.execute('''CREATE TABLE price_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            price REAL,
            unit TEXT,
            pushed_date DATE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        db.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )''')

        # Add unique index on username in users table
        db.execute('''CREATE UNIQUE INDEX username ON users (username)''')

        print("Created DataBase")
        db.close()
    else:
        print("DataBase Already Exists")
    # If no test.db then create test.db and create tables
    # Else skip
