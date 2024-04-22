from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from foodFunction import searchFood

print(searchFood('https://www.willys.se/sok?q=%C3%A4gg%3Acategory%3A%C3%84gg'))
time.sleep(10)

#Hämta data om följande produkter:
#Bröd och spannmål: mjöl, ris, pasta
#Mejeriprodukter: mjölk, ägg, smör
#Frukt och grönt: isbergssallad, tomat, gurka, potatis
#Kött och fisk: nötkött, kyckling, fläskkött, lax
#Konserver: Gulashsoppa, tomatsoppa, tonfisk
#Drycker: kaffe: te, oboy
#Snacks och godis: chips, surgodis, choklad

#Totalt: 23 olika matvaruprodukter från 7 kategorier

url = 'https://www.willys.se/sok?q=%C3%A4gg%3Acategory%3A%C3%84gg'

driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load, adjust the duration as needed
time.sleep(0.1)

# Find all elements with data-testid="product"
items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product"]')

eggPriceArray = []

if items:
    for item in items:
        # Find the title element within each item
        title_element = item.find_element(By.XPATH, './/div[@class="sc-9dc280cb-6 bJGDJx"]')
        title = title_element.text
        # Extract the price per unit
        price_element = item.find_element(By.XPATH, './/div[@class="sc-9dc280cb-17 dOZyhE"]')
        price = price_element.text
        
        if price[len(price)-2:]=="kg":
            break

        # Print the product name and price
        #print("Product:", title)
        #print("Price per egg:", price[8:])
        eggPriceArray.append(price[8:][:5].replace(",","."))
else:
    print("[-] Unable to find items.")

# Wait for the page to load, adjust the duration as needed
time.sleep(0.1)

print(eggPriceArray)

total_sum = 0.0

for price in eggPriceArray:
    total_sum += float(price)

averagePrice = total_sum / len(eggPriceArray)

print("Average price per egg:", averagePrice, "kr")

url = 'https://www.willys.se/sok?q=mellanmj%C3%B6lk'

driver.get(url)

# Wait for the page to load, adjust the duration as needed
time.sleep(0.1)

# Find all elements with data-testid="product"
items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product"]')

milkPriceArray = []

if items:
    for item in items:
        # Find the title element within each item
        title_element = item.find_element(By.XPATH, './/div[@class="sc-9dc280cb-6 bJGDJx"]')
        title = title_element.text
        # Extract the price per unit
        price_element = item.find_element(By.XPATH, './/div[@class="sc-9dc280cb-17 dOZyhE"]')
        price = price_element.text

        # Print the product name and price
        #print("Product:", title)
        #print("Price per egg:", price[8:])
        milkPriceArray.append(price[8:][:5].replace(",","."))
else:
    print("[-] Unable to find items.")

print(milkPriceArray)

total_sum = 0.0

for price in milkPriceArray:
    total_sum += float(price)

averageMilkPrice = total_sum / len(milkPriceArray)

print("Average price per liter:", averageMilkPrice, "kr")





# Push all found items to the database
driver.close()