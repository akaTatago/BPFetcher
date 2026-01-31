from src.utils.scraping_helper import get_soup, clean_text, clean_price

def scrape_fnac(isbn):
    search_url = f"https://www.fnac.pt/SearchResult/ResultList.aspx?Search={isbn}&sft=1&sa=0"

    soup, final_url = get_soup(search_url)

    if not soup:
        return None

    info=soup.find("article", class_="Article-itemGroup")

    if not info:
        return None
    
    #TITLE
    title_area=info.find("p", class_="Article-desc")
    found_title=clean_text(title_area)

    #AUTHOR
    found_author=clean_text(info.find("p", class_="Article-descSub").find("a"))

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
            price_clean=clean_price(price_tag)
            if price_area != 0.00:
                status = "Available"
            else:
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