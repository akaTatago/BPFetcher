from curl_cffi import requests
from bs4 import BeautifulSoup
import random
import time
import re

def scrape_bertrand(isbn):
    search_url = f"https://www.bertrand.pt/pesquisa/{isbn}"

    try:
        time.sleep(random.uniform(2, 5))
        
        response = requests.get(search_url, impersonate="chrome", timeout=15)
        soup = BeautifulSoup(response.text, "lxml")

        info=soup.find("div", class_="product-info  col-xs-6 col-lg-8 ")

        if not info:
            return None
        
        #TITLE
        found_title=info.find("a", class_="title-lnk track").text

        #AUTHOR
        author_area=info.find("div", class_=re.compile(r"authors portlet-product-author-\d+"))
        found_author=author_area.find("a").text

        #PRICE
        price=info.find("span", class_="active-price")
        price_clean = float(price.replace("€", "").replace(",", ".").strip())

        unavailable=info.find("div", class_="unavailable")

        if unavailable:
            on_sale=False
        else:
            off_sale_price=info.find("span", class_="old-price")
            if off_sale_price:
                on_sale=True
            else:
                on_sale=False

        #LINK
        full_link = found_title=info.find("a", class_="title-lnk track")["href"]

        return {
            "title_found": found_title,
            "author_found": found_author,
            "price": price_clean,
            "on_sale": on_sale,
            "link": full_link
        }
        
    except Exception as e:
        print(f"Connection error: {e}")
        return None