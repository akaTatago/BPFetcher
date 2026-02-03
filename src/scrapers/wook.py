from src.utils.scraping_helper import get_soup, clean_text, clean_price
import urllib.parse

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

def search_wook_by_text(title, author):

    search_url = f"https://www.wook.pt/pesquisa?keyword={urllib.parse(title.lower().replace(' ', '+'))}"

    soup, _ = get_soup(search_url)
    if not soup: return []

    results = []
    
    products = soup.find_all("li", class_="product d-flex")


    unmatches=0
    for prod in products:
        if unmatches == 5:
            break

        title_area=prod.find("div", class_="title")
        title_elem = title_area.find("span", class_="font-bold")
        author_elem = prod.find("div", class_="authors").find("a", class_="text-black")
        
        if not title_elem or not author_elem:
            unmatches+=1
            continue

        found_title = clean_text(title_elem)
        found_author = clean_text(author_elem) if author_elem else ""

        if ((title.lower().strip() in found_title.lower() or found_title.lower() in title.lower().strip())  and 
            author.lower().strip() in found_author.lower()):
            
            price_area=prod.find("span", class_="pvp")
            
            final_price = 0.0
            on_sale = False
            
            if price_area:
                final_price = clean_price(price_area.find("span", class_="font-bold"))

                if price_area.find("s", class_="text-red text-align-right"):
                    on_sale=True
                
            
            status = "Available" if final_price > 0 else "Unavailable"
            link = "https://www.wook.pt" + title_area.find("a")['href']

            results.append({
                "Store": "Wook",
                "Found Title": found_title,
                "Found Author": found_author,
                "Price": final_price,
                "On Sale": on_sale,
                "Status": status,
                "Link": link
            })

    return results