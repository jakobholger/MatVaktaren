from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class Product:
    def __init__(self, name, pricePerUnit):
        self.name = name
        self.pricePerUnit = pricePerUnit
    def __str__(self):
        return f"Product(name={self.name}, pricePerUnit={self.pricePerUnit})"

def searchFood(url):
    #setup driver for chrome
    driver = webdriver.Chrome()

    #open website url parameter
    driver.get(url)

    # Find all elements with data-testid="product"
    items = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product"]')
    
    itemsArray = []

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
            #eggPriceArray.append(price[8:][:5].replace(",","."))

            itemsArray.append(Product(title, price[8:][:5].replace(",",".")))
    else:
        print("[-] Unable to find items.")
    
    print(itemsArray)