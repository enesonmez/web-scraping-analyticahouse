"""
    author : Enes Sönmez
"""
# web scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd

# other processes
from tqdm import tqdm
import sys
import locale

class SpxScraperBS:
    def __init__(self, *args, **kwargs):
        self.__base_url = "https://www.spx.com.tr"

    # The data in the file is converted into url.
    def get_product_urls(self, filename):
        try:
            product_urls = pd.read_excel(filename, sheet_name=None, header=None)
            product_urls = list(product_urls["Sheet4"].iloc[:,0])
            product_urls = list(map(lambda url : self.__base_url + url, product_urls))
            return product_urls
        except Exception:
            sys.exit("Filename is wrong or not expected file!!!")
    
    # A get request is sent to the url and the html source file is received.
    def get_source(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            return BeautifulSoup(r.content, "lxml")
        return False

    """
        The following 4 functions (brand, name, code, price) were not deliberately reduced to one function. Because there is 
        a loss of speed due to parameter assignments. However, in the selenium example, the code is shortened.
    """
    # The product brand is returned.
    def __get_product_brand(self, source):
        try:
            return source.find("a", attrs={"class": "product__brand"}).text
        except Exception:
            return "None"
    
    # The product name is returned. source => html page source (BeautifulSoup object)
    def __get_product_name(self, source):
        try:
            return source.find("h1", attrs={"class": "product__title"}).text
        except Exception:
            return "None"
    
    # The product code is returned.
    def __get_product_code(self, source):
        try:
            return source.find("div", attrs={"class": "product__code"}).text
        except Exception:
            return "None"
    
    # The product price is returned.
    def __get_product_price(self, source):
        try:
            return source.find("div", attrs={"class": "product__price"}).text
        except Exception:
            return "None"
    
    # The product availability percent is returned. (on sale product type / total listed product type)
    def __get_product_availability(self, source):
        try:
            try:
                if (len(source.find("div", attrs={"data-variant-key": "integration_first_size"}).find("a", attrs={"href": "#"}))):
                    total_product_type = len(source.find("div", attrs={"data-variant-key": "integration_first_size"}).find_all("a")) -1
                    onsale_product_type = total_product_type - len(source.find("div", attrs={"data-variant-key": "integration_first_size"}).find_all("a", attrs={"class": "disabled"}))
            except Exception:
                total_product_type = len(source.find("div", attrs={"data-variant-key": "integration_first_size"}).find_all("a"))
                onsale_product_type = total_product_type - len(source.find("div", attrs={"data-variant-key": "integration_first_size"}).find_all("a", attrs={"class": "disabled"}))
            return (onsale_product_type/total_product_type) * 100
        except Exception:
            return "None"

    def scrape_products(self, filename):
        # for convert money to float
        locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
        data = list()
        urls = self.get_product_urls(filename)
        # to see work progress
        bar = tqdm(urls, unit="product")
        for url in bar:
            bar.set_description(url)
            product_source = self.get_source(url)
            brand = self.__get_product_brand(product_source)
            name = self.__get_product_name(product_source).strip() # Spaces at the beginning and end of the string are deleted.
            code = self.__get_product_code(product_source).strip()
            price = locale.atof(self.__get_product_price(product_source).strip().replace("TL", "")) # money to float convert
            availability_percent = self.__get_product_availability(product_source)
            data.append((brand, name, code, price, availability_percent))
        return data
    
    # Data is written to the excel file. data => list()
    def write_excel(self, data, filename="products_info.xlsx"):
        df = pd.DataFrame(data)
        df.columns = ["Product_Brand", "Product_Name", "Product_Code", "Product_Price_TL", "Product_Availability_Percent"]
        df = df.drop_duplicates() # Duplicate data is deleted.
        df.to_excel(filename)

if __name__ == '__main__':
    spx = SpxScraperBS()
    data = spx.scrape_products("../files/Product-Detail-URL.xlsx")
    spx.write_excel(data)