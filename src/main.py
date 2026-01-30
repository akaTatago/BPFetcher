import time
import random
from tqdm import tqdm
from src.utils.csv_helper import load_books, save_results
from src.scrapers.wook import scrape_wook

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
        scraped_data = scrape_wook(identifier)
        final_record = book.copy()
        
        if scraped_data:
            final_record["Title"] = scraped_data["title_found"]
            final_record["Author"] = scraped_data["author_found"]
            final_record["Wook Price"] = scraped_data["price"]
            final_record["On Sale"] = "Yes" if scraped_data["on_sale"] else "No"
            final_record["Link"] = scraped_data["link"]
            final_record["Status"] = scraped_data["status"]
        else:
            final_record["Title"] = ""
            final_record["Author"] = ""
            final_record["Wook Price"] = 0.0
            final_record["On Sale"] = "No"
            final_record["Link"] = ""
            final_record["Status"] = "Not found"
            
        results.append(final_record)
        time.sleep(random.uniform(2, 5))

    success = save_results(results, output_file)
    
    if success:
        print(f"Output saved in {output_file}")

if __name__ == "__main__":
    main()