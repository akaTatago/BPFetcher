import time
import random
from tqdm import tqdm
from src.utils.csv_helper import load_books, save_results
from src.scrapers.wook import scrape_wook
from src.scrapers.bertrand import scrape_bertrand
from src.scrapers.fnac import scrape_fnac

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
        wook_data = scrape_wook(identifier)
        bertrand_data = scrape_bertrand(identifier)
        fnac_data = scrape_fnac(identifier)
        final_record = book.copy()
        
        if wook_data:
            final_record["Title"] = wook_data["title_found"]
            final_record["Author"] = wook_data["author_found"]
            final_record["Wook Status"] = wook_data["status"]
            final_record["Wook Price"] = wook_data["price"]
            final_record["Wook On Sale"] = "Yes" if wook_data["on_sale"] else "No"
            final_record["Wook Link"] = wook_data["link"]
        else:
            final_record["Wook Status"] = "Not found"
            final_record["Wook Price"] = 0.0
            final_record["Wook On Sale"] = "No"
            final_record["Wook Link"] = ""

        if bertrand_data:
            final_record["Title"] = bertrand_data["title_found"]
            final_record["Author"] = bertrand_data["author_found"]
            final_record["Bertrand Status"] = bertrand_data["status"]
            final_record["Bertrand Price"] = bertrand_data["price"]
            final_record["Bertrand On Sale"] = "Yes" if bertrand_data["on_sale"] else "No"
            final_record["Bertrand Link"] = bertrand_data["link"]
        else:
            final_record["Bertrand Status"] = "Not found"
            final_record["Bertrand Price"] = 0.0
            final_record["Bertrand On Sale"] = "No"
            final_record["Bertrand Link"] = ""

        if fnac_data:
            final_record["Title"] = fnac_data["title_found"]
            final_record["Author"] = fnac_data["author_found"]
            final_record["Fnac Status"] = fnac_data["status"]
            final_record["Fnac Price"] = fnac_data["price"]
            final_record["Fnac On Sale"] = "Yes" if fnac_data["on_sale"] else "No"
            final_record["Fnac Link"] = fnac_data["link"]
        else:
            final_record["Fnac Status"] = "Not found"
            final_record["Fnac Price"] = 0.0
            final_record["Fnac On Sale"] = "No"
            final_record["Fnac Link"] = ""
            
        results.append(final_record)
        time.sleep(random.uniform(2, 5))

    success = save_results(results, output_file)
    
    if success:
        print(f"Output saved in {output_file}")

if __name__ == "__main__":
    main()