import requests
import json
from dbFunctions import create_product, add_price_for_product, check_exists_for_current_date, get_product_id
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

date = datetime.now().date()

def scrape(product_code):
    product_id = get_product_id(product_code)
    #Check if it already exists for today
    if check_exists_for_current_date(product_id, date):
        url = 'https://www.willys.se/axfood/rest/p/' + product_code
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            html_content = response.text

            parse_html(html_content, product_code)

        else:
            print("Something went wrong! Status code: " + (str)(response.status_code))
    else:
        print("Product price already exists for this date.")

def parse_html(html_content, product_code):
    json_data = json.loads(html_content)
    #print(type(json_data))

    priceCurrency = json_data["price"].split(" ")

    json_data["price"] = priceCurrency[0].replace(",", ".")
    json_data["currency"] = priceCurrency[1]

    #print(json_data['name'], "|", json_data['price'], json_data['currency'], "/", json_data['displayVolume'], "|", json_data['comparePrice'], "/", json_data['comparePriceUnit'])

    create_product(json_data['name'], json_data['displayVolume'], json_data['price'], json_data['price'], product_code, json_data['googleAnalyticsCategory'])
    add_price_for_product(json_data['name'], json_data['price'], json_data['currency'], date, json_data['comparePrice'] + "/" + json_data['comparePriceUnit'], product_code)