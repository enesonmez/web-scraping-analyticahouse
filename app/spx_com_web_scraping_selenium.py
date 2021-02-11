"""
    author : Enes Sönmez
"""
# web scraping
from selenium import webdriver
import pandas as pd

# other processes
import sys
import locale

class SpxScraperSelenium():
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
    
     # The product brand is returned. driver => Selenium webdriver object
    def __get_product_brand(self, driver):
        try:
            return driver.find_element_by_class_name("product__brand").text
        except Exception:
            return "None"
    
    # The product name is returned. 
    def __get_product_name(self, driver):
        try:
            return driver.find_element_by_class_name("product__title").text
        except Exception:
            return "None"
    
    # The product code is returned.
    def __get_product_code(self, driver):
        try:
            return driver.find_element_by_class_name("product__code").text
        except Exception:
            return "None"
    
    # The product price is returned.
    def __get_product_price(self, driver):
        try:
            return driver.find_element_by_class_name("product__price").text
        except Exception:
            return "None"
    
     # The product availability percent is returned. (on sale product type / total listed product type)
    def __get_product_availability(self, driver):
        try:
            total_product_type = len(driver.find_element_by_xpath("//div[@data-variant-key='integration_first_size']").find_elements_by_tag_name("a"))
            onsale_product_type = total_product_type - len(driver.find_element_by_xpath("//div[@data-variant-key='integration_first_size']").find_elements_by_class_name("disabled"))
            return (onsale_product_type/total_product_type) * 100
        except Exception:
            return "None"
    
    # A get request is sent to the url and the html source file is received.
    def scraper(self, filename):
        # for convert money to float
        locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
        data = list()
        urls = self.get_product_urls(filename)
        # Selenium settings
        driver_path = "E:\\Program Files\\selenium\\chromedriver" # Write here the path you installed chromedriver on your own pc.
        driver = webdriver.Chrome(driver_path)
        driver.set_window_size(1400,600)
        for i, url in enumerate(urls):
            driver.get(url)
            brand = self.__get_product_brand(driver)
            name = self.__get_product_name(driver)
            code = self.__get_product_code(driver)
            price = locale.atof(self.__get_product_price(driver).replace("TL", "")) # for convert money to float
            availability_percent = self.__get_product_availability(driver)     
            data.append((brand, name, code, price, availability_percent))
        return data
    
    # Data is written to the excel file. data => list()
    def write_excel(self, data, filename="products_report.xlsx"):
        df = pd.DataFrame(data)
        df.columns = ["Product_Brand", "Product_Name", "Product_Code", "Product_Price_TL", "Product_Availability_Percent"]
        df = df.drop_duplicates() # Duplicate data is deleted.
        df.to_excel(filename)

if __name__ == "__main__":
    spx = SpxScraperSelenium()
    data = spx.scraper("../files/Product-Detail-URL.xlsx")
    spx.write_excel(data)