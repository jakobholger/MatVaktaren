import requests
import json
import sqlite3
from scraperFunction import scrape
from datetime import datetime
import csv
from dbFunctions import create_total_price

csv_file_path = 'WillysProducts.csv'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}


with open(csv_file_path, mode='r', newline='') as file:
    reader = csv.reader(file)

    next(reader)

    for row in reader:
        product_code = row[1]
        scrape(product_code)

create_total_price(datetime.now().date())

print("done")