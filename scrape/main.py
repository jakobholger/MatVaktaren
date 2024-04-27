from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from foodFunction import searchStore, willys, ica, coop, mathem
import sqlite3

#Initiera databas

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Create the products table
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    product_name TEXT,
                    store_name TEXT,
                    category TEXT
                )''')

# Create the price history table
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


#Hämta data om följande produkter:
#Bröd och spannmål: mjöl, ris, pasta
#Mejeriprodukter: mjölk, ägg, smör
#Frukt och grönt: isbergssallad, tomat, gurka, potatis
#Kött och fisk: nötkött, kyckling, fläskkött, lax
#Konserver: Gulashsoppa, tomatsoppa, tonfisk
#Drycker: kaffe: te, oboy
#Snacks och godis: chips, surgodis, choklad

#Totalt: 23 olika matvaruprodukter från 7 kategorier

#Mathem mjölk
searchStore('https://www.mathem.se/se/categories/78-mejeri-ost-juice/91-mjolk/', mathem, "l", "milk")

#Mathem ägg
searchStore('https://www.mathem.se/se/categories/78-mejeri-ost-juice/129-agg-jast/130-agg/', mathem, "st", "egg")

#Mathem smör&margarin
searchStore('https://www.mathem.se/se/categories/78-mejeri-ost-juice/113-smor-margarin/114-bordsask-smor-margarin/', mathem, "kg", "butter")

#Mathem mjöl
searchStore('https://www.mathem.se/se/categories/329-skafferi/354-mjol-bakning/356-vetemjol/', mathem, "kg", "flour")

#Willys ägg
searchStore('https://www.willys.se/sortiment/mejeri-ost-och-agg/agg?q=%3AtopRated%3AproductLabelTypes%3ASWEDISH_FLAG', willys, "st", "egg")


#mjöl
#searchStore('https://www.willys.se/sortiment/skafferi/bakning/mjol', willys)

#långkornigt ris
#searchStore('https://www.willys.se/sortiment/skafferi/pasta-ris-och-matgryn/ris', willys)

#pasta
#searchStore('https://www.willys.se/sok?q=pasta', willys)

#mellanmjölk
#searchStore('https://www.willys.se/sok?q=mellanmj%C3%B6lk', willys)


#Todo Push elements to database