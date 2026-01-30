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
        found_title=title_area.get_text(separator=" ", strip=True)

        #AUTHOR
        author_area=info.find("p", class_="Article-descSub")
        found_author=author_area.find("a").text

        #PRICE AND STATUS
        price_area = info.find("div", class_="bigPricerFA")
        
        price_clean = 0.00
        on_sale = False
        status = "Unavailable"

        if price_area:
            price_tag = price_area.find("strong", class_="userPrice")
            
            if not price_tag:
                all_prices = price_area.find_all("span", class_="price")
                
                if len(all_prices) >= 1:
                    price_tag = all_prices[len(all_prices)-1]
                else:
                    price_tag = None

            if price_area.find("del", class_="oldPrice"):
                on_sale = True

            if price_tag:
                price_text = price_tag.get_text(strip=True)
                clean_text = price_text.replace("€", "").replace(",", ".").strip()
                try:
                    price_clean = float(clean_text)
                    status = "Available"
                except ValueError:
                    price_clean = 0.00
                    status = "Unavailable"

        #LINK
        full_link = title_area.find("a")['href']

        return {
            "title_found": found_title,
            "author_found": found_author,
            "price": price_clean,
            "on_sale": on_sale,
            "status":status,
            "link": full_link
        }
        
    except Exception as e:
        print(f"Scraping error: {e}")
        return None