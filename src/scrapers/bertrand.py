from src.utils.scraping_helper import get_soup, clean_text, normalize, clean_price
import re
import urllib.parse

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

def search_bertrand_by_text(title, author):
    search_url = f"https://www.bertrand.pt/pesquisa/{urllib.parse.quote(title.lower().replace(' ', '+'))}"

    soup, final_url = get_soup(search_url)
    if not soup:
        return []
    
    res = []
    products = soup.find_all("div", class_="product-info")

    unmatches = 0
    for prod in products:
        if unmatches>=10:
            break

        title_elem=prod.find("a", class_="title-lnk track")
        author_elems=prod.find("div", class_=re.compile(r"authors portlet-product-author-\d+")).find_all("a")

        if not title_elem or not author_elems:
            unmatches+=1
            continue

        
        found_title = clean_text(title_elem)
        found_author = ""
        for author_tag in author_elems:
            found_author += f" {clean_text(author_tag)}"

        if ((normalize(title) in normalize(found_title) or normalize(found_title) in normalize(title)) and 
        (normalize(author) in normalize(found_author) or normalize(found_author) in normalize(author))):

            price_clean=clean_price(prod.find("span", class_="active-price"))

            unavailable=prod.find("div", class_="unavailable")

            if unavailable:
                status="Unavailable"
                on_sale=False
            else:
                status="Available"
                off_sale_price=prod.find("span", class_="old-price")
                if off_sale_price:
                    on_sale=True
                else:
                    on_sale=False
            
            full_link = "https://www.bertrand.pt"+title_elem["href"]

            res.append({
                "Store": "Bertrand",
                "title_found": found_title,
                "author_found": found_author.strip(),
                "price": price_clean,
                "on_sale": on_sale,
                "status": status,
                "link": full_link
            })
        else:
            unmatches += 1

    return res