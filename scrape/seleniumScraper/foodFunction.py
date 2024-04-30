from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import sqlite3
from datetime import datetime
from scrape.seleniumScraper.dbFunctions import add_price_for_product, create_product

class Product:
    def __init__(self, name, comparisonPrice):
        self.name = name
        self.comparisonPrice = comparisonPrice
    def __repr__(self):
        return f"<name:{self.name} pricePerUnit:{self.comparisonPrice}>"
    
class Company:
    def __init__(self, name, productClass, classType, titleClass, titleType, priceClass, priceType):
        self.name = name
        self.productClass = productClass
        self.classType = classType
        self.titleClass = titleClass
        self.titleType = titleType
        self.priceClass = priceClass
        self.priceType = priceType

#Hur man lägger till nya företag
    #Hitta 'objektet' som innehåller en produkt.
    #Hitta klassen för produkten samt vilken typ det är ("div") till exempel.
    #Hitta titel elementet och hitta klassen samt typen för detta element
    #Hitta pris elementet samt klassen och typen.
    #För in dessa i en ett nytt objekt instansierat från Company klassen.
    
willys = Company("Willys", "sc-9dc280cb-0 CZBGo", "div", "sc-9dc280cb-6 bJGDJx", "div", "sc-9dc280cb-17 dOZyhE", "div")
ica = Company("Ica", "_box_1ldjz_1 _box--shadow_1ldjz_15 salt-p--0", "div", "link__Link-sc-14ymsi2-0 cgxCVj link__Link-sc-14ymsi2-0 base__Title-sc-1mnb0pd-27 base__FixedHeightTitle-sc-1mnb0pd-43 cgxCVj ctGnCh cCRJZx", "a", "_text_f6lbl_1 _text--m_f6lbl_23 standard-promotion__PromotionIntentText-sc-1vpsrpe-2 fop__PricePerText-sc-sgv9y1-5 kxmtvg eNYENy", "span")
coop = Company("COOP", "Grid-cell u-size1of4", "div", "ProductTeaser-heading", "p", "ProductTeaser-brand", "div")
mathem = Company("Mathem", "k-grid-span-6 md:k-grid-span-4 lg:k-grid-span-2 k-column", "div", "k-text-style k-text-style--title-xxs k-text--hyphens-auto styles_hyphens__IEbdn", "h2", "k-text-style k-text-style--body-s k-text-color--subdued", "p")




def searchStore(url, c, unit, category):

    #setup driver for chrome
    driver = webdriver.Chrome()

    #open website url parameter
    driver.get(url)

    pushed_date = datetime.now().date()

    time.sleep(0.1)

    # Find all elements with data-testid="product"
    items = driver.find_elements(By.XPATH, f'.//{c.classType}[@class="{c.productClass}"]')
    
    itemsArray = []

    if items:
        for item in items:
            # Find the title element within each item
            title_element = item.find_element(By.XPATH, f'.//{c.titleType}[@class="{c.titleClass}"]')
            title = title_element.text
            # Extract the price per unit
            price_element = item.find_element(By.XPATH, f'.//{c.priceType}[@class="{c.priceClass}"]')
            price = price_element.text

            index = price.index("kr")

            pushPrice = price[:index].replace("Jmf-pris ", "").replace(",", ".")
            
            itemsArray.append(Product(title, price[:index].replace("Jmf-pris ", "").replace(",", ".")+"kr/" + unit))
            pushUnit = "kr/" + unit
            create_product(title, c.name, category)
            add_price_for_product(title, pushPrice, pushed_date, pushUnit, c.name)


    else:
        print("[-] Unable to find items.")

    for item in itemsArray:
        print(item)

    sum_items = 0

    for item in itemsArray:
        sum_items += float(price[:index].replace("Jmf-pris ", "").replace(",", "."))

    averageItem = round(sum_items/len(itemsArray), 4)
    print("Average price: " + str(averageItem) + " kr/" + unit)



    driver.close()

    time.sleep(0.1)
