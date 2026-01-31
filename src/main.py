import time
import random
import argparse

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

from src.utils.csv_helper import load_books, save_results
from src.scrapers.wook import scrape_wook
from src.scrapers.bertrand import scrape_bertrand
from src.scrapers.fnac import scrape_fnac

console = Console()

ALL_STORES = {
    "wook": ("Wook", scrape_wook),
    "bertrand": ("Bertrand", scrape_bertrand),
    "fnac": ("Fnac", scrape_fnac)
}

def main():
    parser = argparse.ArgumentParser(description='BPFetcher - Price comparison helper')

    parser.add_argument('--output', type=str, default='data/results.csv', help='CSV output file path')

    parser.add_argument('--stores', nargs='+', default=['all'], 
                        choices=['all', 'wook', 'bertrand', 'fnac'],
                        help='Choose bookstores being scraped (ex: --stores wook fnac)')
    
    parser.add_argument('input_file', type=str, help='CSV input file path')
    
    args = parser.parse_args()

    console.print("\n[bold dodger_blue1]--- BPFetcher CLI ---[/bold dodger_blue1]")


    active_stores = []
    if 'all' in args.stores:
        active_stores = list(ALL_STORES.values())
    else:
        for s in args.stores:
            if s in ALL_STORES:
                active_stores.append(ALL_STORES[s])

    names = [s[0] for s in active_stores]
    console.print(f"Bookshops scraped: [dodger_blue1]{', '.join(names)}[/dodger_blue1]")

    with console.status("[bold dodger_blue1]Reading CSV file...[/bold dodger_blue1]", spinner="dots"):
        books = load_books(args.input_file)
        time.sleep(0.5)
    
    if not books:
        console.print("Empty input file")
        return
    
    results = []

    with Progress(
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[dodger_blue1]Starting...", total=len(books))

        for book in books:
            identifier = book.get("Identifier")
            
            progress.update(task)

            final_record = book.copy()
            final_record.setdefault("Pages", 0)

            for store_name, scraper_func in active_stores:
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

            progress.advance(task)

    if save_results(results, args.output):
        console.print(f"\n[dodger_blue1]Done![/dodger_blue1] Output saved in: [underline]{args.output}[/underline]")
    else:
        console.print("\n[bold red]Saving output file error.[/bold red]")

if __name__ == "__main__":
    main()