# UPA Project 3
# Author: Vojtech Fiala <xfiala61@stud.fit.vutbr.cz>
#
# Support group of co-authors: 
# Vojtech Giesl <xgiesl00@stud.fit.vutbr.cz>
# Vojtech Kronika <xkroni01@stud.fit.vutbr.cz>

from sys import stdin, argv
from bs4 import BeautifulSoup as bs
import cloudscraper

# Main class to get the info
class ProductGetter():
    def __init__(self):
        self.__limit = 99999
        self.__outFile = 'data_all.tsv'
        if len(argv) == 3:
            if argv[1] == '--limit':
                try:
                    self.__limit = int(argv[2])
                except:
                    print("Invalid limit value! Exiting...")
                    exit(1)
                self.__outFile = 'data_limited.tsv'
        self.__urls = None
        self.__scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
        try:
            self.__urls = stdin.readlines()
        except:
            print("Error, there was an error reading the file on stdin")
            exit(1)
    
    def __soupify(self, document):
        soup = bs(document, 'html.parser')
        return soup

    def __getPage(self, page):
        page = self.__scraper.get(page)
        return page.text

    def __floatify(self, price):
        if price == "Unknown":
            return price
        
        newprice = ''
        for letter in price:
            if letter.isnumeric():
                newprice += letter
            elif letter == ',':
                newprice += '.'
        return newprice


    def __parsePage(self, page):
        page = self.__soupify(page)    # download the page
        item_section = page.find('section', {'id':'site-product-price-stock-buy-container'})    # section containing all the info
        if item_section == None:    # Product is not selling anymore
            name = page.find('h1', {'data-type':'product'})
            if name == None:
                name = "Unknown"
            else:
                name = name.text
            price = "Unknown"
            return name, price

        name = item_section.find('h1', {'data-type':'product'}).text    # name of the product
        price = ''
        price = item_section.find('span', {'class':'site-currency-attention'}) # price of the product in euros
        if price == None:
            price = item_section.find('div', {'class':'site-currency-attention'})
        if price == None:
            price = item_section.find('div', {'class':'site-currency-attention site-currency-campaign'}) # product is on sale
            if price == None:
                price = item_section.find('span', {'class':'site-currency-attention site-currency-campaign'})
                if price == None:   # unknown price
                    price = "Unknown"
                else:
                    price = price.text
            else:
                price = price.text
        else:
            price = price.text
        return name, self.__floatify(price)

    def getNamePrices(self):
        counter = 0
        with open(self.__outFile, 'w') as outFile:
            for product in self.__urls:
                if counter >= self.__limit:
                    break
                product = product.strip()   # remove newline
                page = self.__getPage(page=product)
                name, price = self.__parsePage(page)  # get name & price and save in file
                product_info = product + '\t' + name + '\t' + price + '\n'
                outFile.write(product_info)
                counter += 1

if __name__ == '__main__':
    x = ProductGetter()
    x.getNamePrices()
    
