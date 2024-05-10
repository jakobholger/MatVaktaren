import requests
import json
import sqlite3
from scraperFunction import scrape
from datetime import datetime
import csv
from dbFunctions import create_total_price

csv_file_path = 'CityGrossProducts.csv'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

product_code = '100612017_ST'

def scrape(productCode):
    url = 'https://www.citygross.se/api/v1/esales/pdp/' + productCode + '/product'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text

        parse_html(html_content)

    else:
        print("Something went wrong! Status code: " + (str)(response.status_code))

def parse_html(html_content):
    data = json.loads(html_content)
    #print(json_data)
    print("name:" ,data[0]['name'])
    #print(data['prices'])
    print("price:" , data[0]['prices'][0]['currentPrice']['price'] , "kr") 
    print("weight: " + data[0]['descriptiveSize'])
    unit = data[0]['prices'][0]['currentPrice']['comparativePriceUnit']
    comparePrice = data[0]['prices'][0]['currentPrice']['comparativePrice']

    if str(unit) == "LTR":
        comparative = str(comparePrice) + "/l"
    if str(unit) == "PCE":
        comparative = str(comparePrice) + "/st"
    if str(unit) == "KGM":
        comparative = str(comparePrice) + "/kg"
    print("comparative: " + comparative)
    print(" ")


with open(csv_file_path, mode='r', newline='') as file:
    reader = csv.reader(file)

    next(reader)

    for row in reader:
        product_code = row[1]
        scrape(product_code)
