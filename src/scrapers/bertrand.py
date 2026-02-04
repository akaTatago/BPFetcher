import re, urllib.parse
from .base_scraper import BaseScraper
from src.utils.scraping_helper import get_soup, clean_text, clean_price

class BertrandScraper(BaseScraper):
    def __init__(self):
        super().__init__("Bertrand", "https://www.bertrand.pt")

    def scrape_by_isbn(self, isbn):
        url = f"{self.base_url}/pesquisa/{isbn}"
        soup, final_url = get_soup(url)
        if not soup: return None
        prod = soup.find("div", class_="product-info")
        if not prod: return None
        
        #TITLE
        title_tag = prod.find("a", class_="title-lnk track")

        #AUTHOR
        author_tag = prod.find("div", class_=re.compile(r"authors portlet-product-author-\d+")).find("a")

        #PRICE
        price = clean_price(prod.find("span", class_="active-price"))

        return {
            "store": self.store_name,
            "title_found": clean_text(title_tag),
            "author_found": clean_text(author_tag),
            "price": price,
            "on_sale": bool(prod.find("span", class_="old-price")),
            "status": bool(prod.find("div", class_="unavailable")),
            "link": self.base_url + title_tag["href"]
        }

    def search_by_text(self, title, author):
        query = urllib.parse.quote(title.lower().replace(' ', '+'))
        url = f"{self.base_url}/pesquisa/{query}"
        soup, _ = get_soup(url)
        if not soup: return []

        results = []
        unmatches = 0
        products = soup.find_all("div", class_="product-info")

        for prod in products:
            if unmatches>=10:
                break

            title_tag = prod.find("a", class_="title-lnk track")
            author_tag=prod.find("div", class_=re.compile(r"authors portlet-product-author-\d+")).find_all("a")

            if not title_tag or not author_tag: 
                unmatches += 1
                continue

            f_title = clean_text(title_tag)
            f_author = ""
            for author_tag in author_tag:
                f_author += f" {clean_text(author_tag)}"

            if self._validate_match(title, author, f_title, f_author):
                price = clean_price(prod.find("span", class_="active-price"))

                results.append({
                    "store": self.store_name,
                    "title_found": f_title,
                    "author_found": f_author.strip(),
                    "price": price,
                    "on_sale": bool(prod.find("span", class_="old-price")),
                    "status": "Unavailable" if prod.find("div", class_="unavailable") else "Available",
                    "link": self.base_url + title_tag["href"]
                })
            else:
                unmatches += 1

        return results