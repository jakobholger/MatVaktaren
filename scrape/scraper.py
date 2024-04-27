import requests
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}


url = 'https://www.willys.se/sok?q=%C3%A4gg%3Acategory%3A%C3%84gg'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    #print(req.content)
    #print(req.text)
    html_content = response.content
else:
    print("Something went wrong! Status code: " + (str)(response.status_code))

soup = BeautifulSoup(html_content, 'html.parser')
print(soup.prettify())
price = soup.find('p', attrs={'class': 'sc-1cce6383-14 jVdrOk'})
print(price)
