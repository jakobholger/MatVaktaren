from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from foodFunction import searchFood

#Hämta data om följande produkter:
#Bröd och spannmål: mjöl, ris, pasta
#Mejeriprodukter: mjölk, ägg, smör
#Frukt och grönt: isbergssallad, tomat, gurka, potatis
#Kött och fisk: nötkött, kyckling, fläskkött, lax
#Konserver: Gulashsoppa, tomatsoppa, tonfisk
#Drycker: kaffe: te, oboy
#Snacks och godis: chips, surgodis, choklad

#Totalt: 23 olika matvaruprodukter från 7 kategorier

#ägg
print(searchFood('https://www.willys.se/sortiment/mejeri-ost-och-agg/agg'))

#mjöl
print(searchFood('https://www.willys.se/sortiment/skafferi/bakning/mjol'))

#långkornigt ris
print(searchFood('https://www.willys.se/sortiment/skafferi/pasta-ris-och-matgryn/ris'))

#pasta
print(searchFood('https://www.willys.se/sok?q=pasta'))

#mellanmjölk
print(searchFood('https://www.willys.se/sok?q=mellanmj%C3%B6lk'))


#Push elements to database