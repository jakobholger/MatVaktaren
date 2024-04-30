import requests
import json
import sqlite3
from scraperFunction import scrape

# Connect to SQLite database
conn = sqlite3.connect('products.db')

# Create a cursor object
cursor = conn.cursor()

# Create the products table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    weight TEXT,
                    product_code TEXT
                )''')

# Create the price history table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY,
                    product_id INTEGER,
                    price REAL,
                    unit TEXT,
                    pushed_date DATE,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )''')
conn.commit()
conn.close()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

products = ['101145716_ST', '101523778_ST', '101248845_ST', '101243524_ST',
            '101220577_ST', '101234821_ST', '101352143_ST', '101277483_ST',
            '101240218_ST', '101302991_ST', '101240219_ST', '100087978_ST',
            '101233933_ST', '101233931_ST', '101205891_ST', '101125998_ST',
            '100657772_ST', '101187348_ST', '101218667_ST', '101334752_ST',
            '101017249_ST', '101090926_ST', '101231483_ST', '101244335_ST',
            '101273878_KG', '100672960_ST', '101281488_ST', '101281472_ST',
            '100152264_KG', '100152282_KG', '100819660_ST', '101267404_ST',
            '101254251_ST', '100594965_ST', '101350773_ST', '101243958_ST',
            '101257800_KG', '100942919_KG', '101257801_KG', '100943366_KG',
            '101266948_ST', '101223961_ST', '101294827_ST', '101053976_KG',
            '101232055_KG', '100945355_KG', '100942278_KG', '100984892_KG',
            '101263061_ST', '101263071_ST', '101327491_ST', '101306409_ST',
            '100592823_ST', '100469440_ST', '101176088_ST', '100897120_ST',
            '100842313_ST', '101245722_ST', '101340309_ST', '101290100_ST',
            '101361686_ST', '101361685_ST', '101458683_ST', '101228250_ST',
            '101291230_ST', '101225750_ST', '101268569_ST', '101346207_ST',
            '100480178_ST', '101274109_ST', '100020969_ST', '101499081_ST',
            '101307358_ST', '101307337_ST', '101545141_ST', '101231346_ST',
            '101250980_ST', '101250927_ST', '101250964_ST', '101235685_ST',
            '101219084_ST', '101252646_ST', '101197249_ST', '101545428_ST',
            '101544931_ST', '101288362_ST', '101179861_ST', '101283040_ST' ]

for product in products:
    scrape(product)
