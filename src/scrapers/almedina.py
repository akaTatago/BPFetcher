from .base_scraper import BaseScraper
from src.utils.scraping_helper import get_soup, clean_text, clean_price, normalize_isbn

class AlmedinaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Almedina", "https://www.almedina.net")

    def scrape_by_isbn(self, isbn):
        isbn = normalize_isbn(isbn)
        url = f"{self.base_url}/catalogsearch/result/?q={isbn}"
        soup, response_link = get_soup(url)
        if not soup: return None
        if soup.find("div", class_="message notice"): return None

        prod = soup.find("div", class_="wrap-holder")

        info = prod.find("div", class_="prod-details-top")
        title_elem = info.find("h2", class_="prod-name")
        author_elem = info.find("a", class_=None)

        if not title_elem: return None

        found_title = clean_text(title_elem)
        found_author = clean_text(author_elem)

        price_area = prod.find("div", class_="price-box")
        price_tag = prod.find("span", class_="price")
        price = clean_price(price_tag)

        return {
            "store": self.store_name,
            "title_found": found_title,
            "author_found": found_author,
            "price": price,
            "on_sale": bool(price_area.find("span", class_="special-price")),
            "status": "Unavailable" if "Indisponível" in info.find("span", id="disponibilidade").text else "Available",
            "link": response_link
        }
    
    def search_by_text(self, title, author):
        query = title.lower() + " " + author.lower()
        url = f"{self.base_url}/?books[query]={query}"
        soup, _ = get_soup(url)
        if not soup: return []                                                             ###CORRIGIR

        results = []
        unmatches = 0
        products = soup.find_all("li", class_="ais-InfiniteHits-item")
        for prod in products:
            if unmatches >= 10:
                break

            data = self._extract_product_data(prod)
            if not data:
                unmatches += 1
                continue
            if self._validate_match(title, author, data["title_found"], data["author_found"]):
                results.append(data)
            else:
                unmatches += 1
    
        return results