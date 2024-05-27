from scraperFunction import scrape
import csv
from dbFunctions import create_total_price
import threading
import time

csv_file_path = 'WillysProducts.csv'

threads = []

with open(csv_file_path, mode='r', newline='') as file:
    reader = csv.reader(file)

    next(reader)

    for row in reader:
        product_code = row[1]
        scrape_thread = threading.Thread(target=scrape, args=(product_code,))
        threads.append(scrape_thread)
        scrape_thread.start()
        time.sleep(0.01)
        #scrape(product_code)

# Wait for all threads to complete
for thread in threads:
    thread.join()

create_total_price()