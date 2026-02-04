from abc import ABC, abstractmethod
from src.utils.scraping_helper import normalize

class BaseScraper(ABC):
    def __init__(self, store_name, base_url):
        self.store_name = store_name
        self.base_url = base_url

    @abstractmethod
    def search_by_text(self, title, author):
        pass

    @abstractmethod
    def scrape_by_isbn(self, isbn):
        pass

    def _validate_match(self, search_title, search_author, found_title, found_author):
        n_title, n_author = normalize(search_title), normalize(search_author)
        f_title, f_author = normalize(found_title), normalize(found_author)

        if f_title == None or f_author==None:
            return False
        
        title_match = n_title in f_title or f_title in n_title
        author_match = n_author in f_author or f_author in n_author
        return title_match and author_match