from curl_cffi import requests
from bs4 import BeautifulSoup
import random
import time

def scrape_fnac(isbn):
    search_url = f"https://www.fnac.pt/SearchResult/ResultList.aspx?Search={isbn}&sft=1&sa=0"

    try:
        time.sleep(random.uniform(2, 5))
        
        response = requests.get(search_url, impersonate="chrome", timeout=15)
        soup = BeautifulSoup(response.text, "lxml")

        info=soup.find("article", class_="Article-itemGroup")

        if not info:
            return None
        
        #TITLE
        title_area=info.find("p", class_="Article-desc")
        title_tag=title_area.find("a", class_="Article-title")
        found_title=title_tag.text

        sub_title=title_area.text
        if sub_title:
            found_title = found_title + ": " + sub_title

        #AUTHOR
        author_area=info.find("p", class_="Article-descSub")
        found_author=author_area.find("a").text

        #PRICE AND STATUS
        price_area=info.find("div", class_="bigPricerFA")

        price=price_area.find("div", class_="blocPriceBorder--bgGrey").find("span", class_="price").text
        on_sale=False
        status="Available"

        if not price:
            price=price_area.find("strong", class_="userPrice").text

            if not price:
                price="0.00"
                status="Unavailable"
            else:
                off_sale_price=price_area.find("del", class_="oldPrice").text
                if off_sale_price:
                    on_sale = True
        
        price_clean = float(price.replace("€", "").replace(",", ".").strip())

        #LINK
        full_link = title_tag['href']

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