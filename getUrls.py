# UPA Project 3
# Author: Vojtech Fiala <xfiala61@stud.fit.vutbr.cz>
#
# Support group of co-authors: 
# Vojtech Giesl <xgiesl00@stud.fit.vutbr.cz>
# Vojtech Kronika <xkroni01@stud.fit.vutbr.cz>

import os
from bs4 import BeautifulSoup as bs
import cloudscraper

# Main class to download URLs of products
class URLDownloader():
    def __init__(self, product):
        # careful with this, apparently CPUs are hosted on "proshop.dk" and GPUs on .de etc
        self.__base_url = ''
        self.__product = ''
        self.__base_url = 'https://www.proshop.de'
        
        if product == 'CPU':
            self.__product = 'CPU'  # At first i wanted to dowload CPUs, but theres not enough of them, so GPUs will do it
        elif product == 'GPU':
            self.__product = 'Grafikkarte'

        self.__category = self.__base_url + '/' + self.__product
        self.__file = 'urls.txt'
        self.__scraper = cloudscraper.create_scraper(delay=10, browser='chrome')
    
    def __getPage(self, page):
        page = self.__scraper.get(page)
        return page.text

    def __soupify(self, document):
        soup = bs(document, 'html.parser')
        return soup

    def __removeDuplicates(self, duplicates):
        return list(dict.fromkeys(duplicates))

    def __getProducts(self, page):
        base = self.__soupify(self.__getPage(page))    # download the page
        product_links = base.find_all('a', {"class":"show"})    # each 'a' element has a "show" class if it leads to a product
        valid_links = []
        for link in product_links:
            link = link['href']
            valid_links.append(link)
        return self.__removeDuplicates(valid_links) # return list with no duplicates, it might be on sale or something and there more times
        
    def __saveUrls(self, file, urls):
        with open(file, 'a') as url_file:
            for link in urls:
                url_file.write(link + '\n')

    def getLinks(self):
        base_page = self.__soupify(self.__getPage(self.__category))    # get base page opf a category
        other_pages = base_page.find('ul', {'class':'pagination'})  # find navigation bar so that i get all of the products and not jsut oen page
        nav_links = other_pages.findChildren("a")   # find all links in the nav bar
        nav_hrefs = []
        for link in nav_links:
            nav_hrefs.append(link['href'])
        nav_hrefs = self.__removeDuplicates(nav_hrefs)  # remove duplicates (navigation contains links going "previous" and "enxt")

        page_products = [] 
        for link in nav_hrefs:  # find all cpus
            page_products.append(self.__getProducts(self.__base_url + link))

        product_links = []
        for products in page_products:  # make a list with complete urls for each product
            for product in products:
                product_links.append(self.__base_url + product)
                
        self.__saveUrls(file=self.__file, urls=product_links)
        
if __name__ == '__main__':
    if os.path.isfile('urls.txt'):
        os.remove('urls.txt')   # remove file each time so that the links are fresh
    x = URLDownloader(product='CPU')
    x.getLinks()
    y = URLDownloader(product='GPU')
    y.getLinks()
