import requests
from bs4 import BeautifulSoup

url = 'https://www.willys.se/sok?q=%C3%A4gg%3Acategory%3A%C3%84gg'

# Send a GET request to the Google homepage

headers = {
     "User-agent" :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

 
# Check if the request was successful (status code 200)
if response.status_code == 200:
    print("[+]Success response")

    # Parse the HTML content of the page using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    print(soup.prettify())

    # Find all elements with the data-testid attribute set to "product"
    #product_elements = soup.css.select_one(".sc-9dc280cb-0 CZBGo")  


    #print(product_elements)
        
    #for product in product_elements:
       # title = product_elements.find('div', class_='sc-9dc280cb-6 bJGDJx').text.strip()
        #print(title)

else:
    print("[-]Failed to fetch Google homepage")
