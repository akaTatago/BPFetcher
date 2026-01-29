from curl_cffi import requests
from bs4 import BeautifulSoup
import random
import time

def scrape_wook(isbn):
    clean_isbn = str(isbn).replace("-", "").strip()
    search_url = f"https://www.wook.pt/pesquisa?keyword={clean_isbn}"

    try:
        time.sleep(random.uniform(2, 5))
        
        response = requests.get(search_url, impersonate="chrome", timeout=15)
        soup = BeautifulSoup(response.text, "lxml")

        info=soup.find("div", class_="right d-flex flex-column")

        if not info:
            return None
        
        #TITLE
        found_title=info.find("span", class_="title").text

        #AUTHOR
        found_author=info.find("span", class_="authors").find("a").text

        #PRICE
        price_area=info.find("div", class_="wook-container d-flex flex-column gap-20")
        available=price_area.find("div", id="product-price")
        if not available:
            price_clean=0.00
            on_sale=False
        else:
            price=price_area.find("span", class_="price text-black text-align-right").text
            price_clean = float(price.replace("€", "").replace(",", ".").strip())
            off_sale_price=price_area.find("s", class_="text-red text-align-right")
            if off_sale_price:
                on_sale=True
            else:
                on_sale=False

        #LINK
        full_link = response.url

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