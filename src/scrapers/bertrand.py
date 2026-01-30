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

        info=soup.find("div", class_="product-info")

        if not info:
            return None
        
        #TITLE
        title_tag=info.find("a", class_="title-lnk track")
        found_title=title_tag.text

        #AUTHOR
        author_area=info.find("div", class_=re.compile(r"authors portlet-product-author-\d+"))
        found_author=author_area.find("a").text

        #PRICE AND STATUS
        price=info.find("span", class_="active-price").text
        price_clean = float(price.replace("€", "").replace(",", ".").strip())

        unavailable=info.find("div", class_="unavailable")

        if unavailable:
            status="Unavailable"
            on_sale=False
        else:
            status="Available"
            off_sale_price=info.find("span", class_="old-price")
            if off_sale_price:
                on_sale=True
            else:
                on_sale=False

        #LINK
        full_link = "https://www.bertrand.pt"+title_tag["href"]

        return {
            "title_found": found_title,
            "author_found": found_author,
            "price": price_clean,
            "on_sale": on_sale,
            "status":status,
            "link": full_link
        }
        
    except Exception as e:
        print(f"Connection error: {e}")
        return None