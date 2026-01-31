from src.utils.scraping_helper import get_soup, clean_text, clean_price

def scrape_wook(isbn):
    search_url = f"https://www.wook.pt/pesquisa?keyword={isbn}"

    soup, final_url = get_soup(search_url)

    if not soup:
        return None

    info=soup.find("div", class_="right d-flex flex-column")

    if not info:
        return None
    
    #TITLE
    found_title=clean_text(info.find("span", class_="title"))

    #AUTHOR
    found_author=clean_text(info.find("span", class_="authors").find("a"))

    #PRICE AND STATUS
    price_area=info.find("div", class_="wook-container d-flex flex-column gap-20")
    available=price_area.find("div", id="product-price")
    if not available:
        status="Unavailable"
        price_clean=0.00
        on_sale=False
    else:
        status="Available"
        price=price_area.find("span", class_="price text-black text-align-right").text
        price_clean = clean_price(price)
        
        off_sale_price=price_area.find("s", class_="text-red text-align-right")
        if off_sale_price:
            on_sale=True
        else:
            on_sale=False

    #LINK
    full_link = final_url

    #PAGES
    info_table=soup.find("table")
    pages=0
    if info_table:
        table_rows = info_table.find_all("tr")
        if len(table_rows) >= 8 and "Páginas:"==table_rows[7].find("td").text:
            pages=int(table_rows[7].find("td", class_="font-medium").text)

    return {
        "title_found": found_title,
        "author_found": found_author,
        "pages":pages,
        "price": price_clean,
        "on_sale": on_sale,
        "status":status,
        "link": full_link
    }