import urllib.parse
import time
import random
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from src.utils.scraping_helper import clean_text, clean_price, normalize, normalize_isbn

class FnacScraper(BaseScraper):

    def __init__(self):
        super().__init__("Fnac", "https://www.fnac.pt")
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        self.context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.page = self.context.new_page()

        self.page.route("**/*", lambda route: route.abort() 
                        if route.request.resource_type in ["image", "media", "font"] 
                        else route.continue_())
        
        try:
            self.page.goto(self.base_url, timeout=30000, wait_until="domcontentloaded")
            self._handle_captcha()
            self._reject_cookies()
        except Exception as e:
            print(f"[FNAC INIT ERROR] {e}")

    def close(self):
        try:
            self.browser.close()
            self.p.stop()
        except:
            pass

    def _reject_cookies(self):
        try:
            if self.page.is_visible("#onetrust-accept-btn-handler"):
                self.page.click("#onetrust-accept-btn-handler")
        except:
            pass

    def _handle_captcha(self):
        if "https://ct.captcha-delivery.com/c.js" in self.page.content().lower():
            print("\n" + "!"*50)
            print("[FNAC] CAPTCHA DETECTED!")
            print("Go to the open Chrome window")
            print("Solve the CAPTCHA")
            input("Press ENTER in this terminal when the Fnac search page completes loading...")
            print("!"*50 + "\n")
            return True
        return False

    def _get_soup_internal(self, url):
        try:
            time.sleep(random.uniform(1.5, 3))
            self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            self._handle_captcha()
            
            content = self.page.content()
            if "<body></body>" in content:
                self.page.wait_for_selector("footer", timeout=5000)
                content = self.page.content()

            return BeautifulSoup(content, "lxml")
        except Exception as e:
            print(f"[FNAC ERROR] {url}: {e}")
            return None

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
        price = 0.0
        if price_area:
            price_tag = price_area.find("strong", class_="userPrice")
            
            if not price_tag:
                all_prices = price_area.find_all("span", class_="price")
                if len(all_prices) >= 1:
                    price_tag = all_prices[-1]
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
        isbn = normalize_isbn(isbn)
        url = f"{self.base_url}/SearchResult/ResultList.aspx?Search={isbn}&sft=1&sa=0"
        
        soup = self._get_soup_internal(url)
        
        if not soup: return None
        first_prod = soup.find("article", class_="Article-itemGroup")
        return self._extract_product_data(first_prod) if first_prod else None
    
    def search_by_text(self, title, author):
        query = urllib.parse.quote(title.lower()).replace('%20', '+')
        url = f"{self.base_url}/SearchResult/ResultList.aspx?Search={query}&sft=1&sa=0"

        soup = self._get_soup_internal(url)
        
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