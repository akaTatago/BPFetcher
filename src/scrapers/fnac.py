import urllib.parse
from .base_scraper import BaseScraper
from src.utils.scraping_helper import get_soup, clean_text, clean_price, normalize

class FnacScraper(BaseScraper):

    def __init__(self):
        super().__init__("Fnac", "https://www.fnac.pt")

    def _validate_match(self, search_title, search_author, found_title, found_author):
        n_title = normalize(search_title)
        f_title = normalize(found_title)

        if n_title == f_title:
            return True
        return super()._validate_match(search_title, search_author, found_title, found_author)
    
    def _extract_product_data(self, prod):
        title_elem = prod.find("p", class_="Article-desc")
        author_elem = prod.find("p", class_="Article-descSub")
        if not title_elem: return None

        title_link = title_elem.find("a")
        found_title = clean_text(title_elem)
        found_author = clean_text(author_elem.find("a")) if author_elem.find("a") else clean_text(author_elem)[:clean_text(author_elem).find('-')-1]

        price_area = prod.find("div", class_="bigPricerFA")
        if price_area:
            price_tag = price_area.find("strong", class_="userPrice")
            
            if not price_tag:
                all_prices = price_area.find_all("span", class_="price")
                
                if len(all_prices) >= 1:
                    price_tag = all_prices[len(all_prices)-1]
                else:
                    price_tag = None
        price = clean_price(price_tag)

        return {
            "store": self.store_name,
            "title_found": found_title,
            "author_found": found_author,
            "price": price,
            "on_sale": bool(prod.find("del", class_="oldPrice")),
            "status": "Available" if price > 0 else "Unavailable",
            "link": title_link['href'] if title_link else ""
        }
    
    def scrape_by_isbn(self, isbn):
        url = f"{self.base_url}/SearchResult/ResultList.aspx?Search={isbn}&sft=1&sa=0"
        soup, _ = get_soup(url)
        if not soup: return None
        first_prod = soup.find("article", class_="Article-itemGroup")
        return self._extract_product_data(first_prod) if first_prod else None
    
    def search_by_text(self, title, author):
        query = urllib.parse.quote(title.lower()).replace('%20', '+')
        url = f"{self.base_url}/SearchResult/ResultList.aspx?Search={query} &sft=1&sa=0"
        soup, _ = get_soup(url)
        if not soup: return []

        results = []
        unmatches = 0
        products = soup.find_all("div", class_="Article-item")
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