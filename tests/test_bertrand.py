import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scrapers.bertrand import BertrandScraper

test_books = [
    "9789897731129",
    "978-972-0-04683-3",
    "9789723829334",
    "978-972-0-03306-2",
    "9789899287204",
    "56446464646464468",
    "9781779527264",
    "9781779528278"
]

print("SCRAPING TEST")

scraper = BertrandScraper()
for book in test_books:
    res = scraper.scrape_by_isbn(book)
    
    if res:
        print(f"STATUS: {res['status']}")
        print(f"TITLE: {res['title_found']}")
        print(f"AUTHOR: {res['author_found']}")
        print(f"PRICE: {res['price']:.2f}")
        print(f"ON SALE: {res['on_sale']}")
        print(f"LINK: {res['link']}")
        print("-"*40)
    else:
        print(f"BOOK {book} DATA NOT FOUND")
        print("-"*40)