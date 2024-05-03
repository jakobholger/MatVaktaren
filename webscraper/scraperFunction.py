import requests
import json
from dbFunctions import create_product, add_price_for_product
from datetime import datetime, timedelta
import random

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

pushed_date = datetime.now().date() + timedelta(days=4)

def scrape(productCode):
#url = 'https://www.willys.se/_next/data/6812123c/sv.json?q=%C3%A4gg&name=agg-24p-Frigaende-Inomhus-Medium-101187348_ST&productCode=101187348_ST'
    #    url = 'https://www.willys.se/axfood/rest/p/100087978_ST'
    url = 'https://www.willys.se/axfood/rest/p/' + productCode
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Something went wrong! Status code: " + (str)(response.status_code))
        return 0

    parse_html(html_content, productCode)

def parse_html(html_content, productCode):
    json_data = json.loads(html_content)
    #print(type(json_data))

    #if (json_data['potentialPromotions'][0]['applied']) == True:
    #    print(json_data['potentialPromotions'][0]['price'])
    #    print()
    #    print(json_data['potentialPromotions'][0]['lowestHistoricalPrice'])
   # else:
    #    print(json_data['potentialPromotions'][0]['lowestHistoricalPrice'])
    priceCurrency = json_data["price"].split(" ")

    json_data["price"] = priceCurrency[0].replace(",", ".")
    json_data["currency"] = priceCurrency[1]

    print(json_data['name'], "|", json_data['price'], json_data['currency'], "/", json_data['displayVolume'], "|", json_data['comparePrice'], "/", json_data['comparePriceUnit'])

    create_product(json_data['name'], json_data['displayVolume'], productCode, json_data['googleAnalyticsCategory'])
    add_price_for_product(json_data['name'], random.randint(15, 200), json_data['currency'], pushed_date, json_data['comparePrice'] + "/" + json_data['comparePriceUnit'], productCode)