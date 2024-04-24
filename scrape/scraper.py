import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}


url = 'https://www.willys.se/_next/data/6812123c/sv.json?q=%C3%A4gg&name=agg-24p-Frigaende-Inomhus-Medium-101187348_ST&productCode=101187348_ST'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    #print(req.content)
    #print(req.text)
    html_content = response.content
else:
    print("Something went wrong! Status code: " + (str)(response.status_code))



soup = BeautifulSoup(html_content, 'html.parser')

print(soup)
products = soup.select('div.sc-9dc280cb-0 CZBGo')

print(products)
