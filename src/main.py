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
        
        if scraped_data:
            final_record={
                "ISBN13":identifier,
                "Title":scraped_data["title_found"],
                "Price":scraped_data["price"],
                "On sale":scraped_data["on_sale"],
                "Link":scraped_data["link"]
            }
        else:
            final_record={
                "ISBN13":identifier,
                "Title":"",
                "Price":"",
                "On sale":"",
                "Link":""
            }
            
        results.append(final_record)

        time.sleep(random.uniform(2, 5))

    success = save_results(results, output_file)
    
    if success:
        print(f"Output saved in {output_file}")

if __name__ == "__main__":
    main()