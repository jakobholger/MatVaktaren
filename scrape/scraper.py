import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}

productCode = '101190071_ST'
#productCode = '100087978_ST'

def main(productCode):
#url = 'https://www.willys.se/_next/data/6812123c/sv.json?q=%C3%A4gg&name=agg-24p-Frigaende-Inomhus-Medium-101187348_ST&productCode=101187348_ST'
    #    url = 'https://www.willys.se/axfood/rest/p/100087978_ST'
    url = 'https://www.willys.se/axfood/rest/p/' + productCode
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text
    else:
        print("Something went wrong! Status code: " + (str)(response.status_code))
        return 0

    parse_html(html_content)

def parse_html(html_content):
    json_data = json.loads(html_content)
    print(type(json_data))

    if (json_data['potentialPromotions'][0]['applied']) == True:
        print(json_data['potentialPromotions'][0]['price'])
        print()
        print(json_data['potentialPromotions'][0]['lowestHistoricalPrice'])
    else:
        print(json_data['potentialPromotions'][0]['lowestHistoricalPrice'])

    print(json_data['name'], "|", json_data['price'], "/", json_data['displayVolume'], "|", json_data['comparePrice'], "/", json_data['comparePriceUnit'])

if __name__ == "__main__":
    main(productCode)
