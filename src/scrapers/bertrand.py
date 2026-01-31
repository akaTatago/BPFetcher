from src.utils.scraping_helper import get_soup, clean_text, clean_price
import re

def scrape_bertrand(isbn):
    search_url = f"https://www.bertrand.pt/pesquisa/{isbn}"

    soup, final_url = get_soup(search_url)

    if not soup:
        return None

    info=soup.find("div", class_="product-info")

    if not info:
        return None
    
    #TITLE
    title_tag=info.find("a", class_="title-lnk track")
    found_title=clean_text(title_tag)

    #AUTHOR
    found_author=clean_text(info.find("div", class_=re.compile(r"authors portlet-product-author-\d+")).find("a"))

    #PRICE AND STATUS
    price_clean=clean_price(info.find("span", class_="active-price"))

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