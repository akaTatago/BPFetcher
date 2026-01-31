import time
import random
from tqdm import tqdm
from src.utils.csv_helper import load_books, save_results
from src.scrapers.wook import scrape_wook
from src.scrapers.bertrand import scrape_bertrand
from src.scrapers.fnac import scrape_fnac

STORES = [
    ("Wook", scrape_wook),
    ("Bertrand", scrape_bertrand),
    ("Fnac", scrape_fnac)
]

def main():
    print("\n--- BPFetcher ---")
    
    input_file = "data/books_test.csv"
    output_file = "data/results.csv"
    
    books = load_books(input_file)
    
    if not books:
        print("Empty input file")
        return
    
    results = []

    for book in tqdm(books, desc="Processing", unit="book"):
        identifier = book.get("Identifier")
        
        final_record = book.copy()
        final_record.setdefault("Pages", 0)

        for store_name, scraper_func in STORES:
            data = scraper_func(identifier)
            
            if data:
                final_record["Title"] = data.get("title_found", final_record.get("Title"))
                final_record["Author"] = data.get("author_found", final_record.get("Author"))
                
                if "pages" in data:
                    final_record["Pages"] = data["pages"]

                final_record[f"{store_name} Status"] = data.get("status", "Available")
                final_record[f"{store_name} Price"] = data.get("price", 0.0)
                final_record[f"{store_name} On Sale"] = "Yes" if data.get("on_sale") else "No"
                final_record[f"{store_name} Link"] = data.get("link", "")
            else:
                final_record[f"{store_name} Status"] = "Not found"
                final_record[f"{store_name} Price"] = 0.0
                final_record[f"{store_name} On Sale"] = "No"
                final_record[f"{store_name} Link"] = ""
            
        results.append(final_record)
        time.sleep(random.uniform(2, 5))

    success = save_results(results, output_file)
    
    if success:
        print(f"Output saved in {output_file}")

if __name__ == "__main__":
    main()