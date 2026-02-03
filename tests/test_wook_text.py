import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scrapers.wook import scrape_wook
from src.scrapers.wook import search_wook_by_text

test_books = [
    ["Os Irmãos Karamázov", "Fiódor Dostoiévski"],
    ["Ensaio sobre a Cegueira", "José Saramago"],
    ["A Queda", "Albert Camus"],
    ["1984", "George Orwell"],
    ["O Crime de São Valentim (Edição Especial Exclusiva Wook)", "Navessa Allen"],
    ["RWAAAAAR", "EBAAAAA"],
    ["Batman: Hush: Dc Compact Comics Edition", "Jim Lee"],
    ["Batman: The Cult Deluxe Edition", "Bernie Wrightson"]
]

print("SCRAPING TEST")

for title, author in test_books:
    res = search_wook_by_text(title, author)
    
    if res:
        for edition in res:
            print(f"STATUS: {edition['status']}")
            print(f"TITLE: {edition['title_found']}")
            print(f"AUTHOR: {edition['author_found']}")
            print(f"PRICE: {edition['price']}")
            print(f"ON SALE: {edition['on_sale']}")
            print(f"LINK: {edition['link']}")
            print("-"*40)
    else:
        print(f"BOOK {title} DATA NOT FOUND")
        print("-"*40)