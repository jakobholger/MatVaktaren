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
            max_price NUMERIC,
            min_price NUMERIC,
            category TEXT,
            product_code TEXT,
            store TEXT
        )''')
        db.execute('''CREATE TABLE price_history (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            price NUMERIC,
            currency TEXT,
            unit TEXT,
            date DATE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )''')
        db.execute('''CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            username TEXT NOT NULL,
            hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )''')
        db.execute('''CREATE TABLE total_price (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            value NUMERIC,
            date DATE
        )''')


        # Add unique index on username in users table
        db.execute('''CREATE UNIQUE INDEX username ON users (username)''')
        db.execute('''INSERT INTO users (username, hash, is_admin) VALUES ('admin', 'scrypt:32768:8:1$0Jx26kSeWTf1BTFw$6208faa0624e04691e5ac42793b0711f51b26dd56cce6d67cd3c834534d0b5c280acbc2c21a7233f8945d5b096394ca1e1d7f90cfaec68b103c4b60c064dfa94', 1)''')
        db.commit()
        print("Created DataBase")
        db.close()
    else:
        print("DataBase Already Exists")
    # If no test.db then create test.db and create tables
    # Else skip
