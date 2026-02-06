import time
import random
import argparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn

from src.utils.csv_helper import load_books, save_results

from src.scrapers.wook import WookScraper
from src.scrapers.bertrand import BertrandScraper
from src.scrapers.fnac import FnacScraper
from src.scrapers.almedina import AlmedinaScraper

console = Console()

ALL_STORES = {
    "wook": WookScraper(),
    "bertrand": BertrandScraper(),
    "fnac": FnacScraper(),
    "almedina": AlmedinaScraper()
}

def main():
    parser = argparse.ArgumentParser(description='BPFetcher - Price comparison helper')

    parser.add_argument('--output', type=str, default='data/results.csv', help='CSV output file path')

    parser.add_argument('--stores', nargs='+', default=['all'], 
                        choices=['all', 'wook', 'bertrand', 'fnac', 'almedina'],
                        help='Choose bookstores being scraped (ex: --stores wook fnac)')
    
    parser.add_argument('--mode', type=str, default='isbn', choices=['isbn', 'text'],
                        help='Search mode: "isbn" (default) or "text" (Title + Author)')
    
    parser.add_argument('input_file', type=str, help='CSV input file path')
    
    args = parser.parse_args()

    console.print("\n[bold dodger_blue1]--- BPFetcher CLI ---[/bold dodger_blue1]")


    active_scrapers = []
    if 'all' in args.stores:
        active_scrapers = list(ALL_STORES.values())
    else:
        for s in args.stores:
            if s in ALL_STORES:
                active_scrapers.append(ALL_STORES[s])

    names = [s.store_name for s in active_scrapers]
    console.print(f"Mode: [yellow]{args.mode.upper()}[/yellow]")
    console.print(f"Bookshops scraped: [dodger_blue1]{', '.join(names)}[/dodger_blue1]")

    with console.status("[bold dodger_blue1]Reading CSV file...[/bold dodger_blue1]", spinner="dots"):
        books = load_books(args.input_file)
        time.sleep(0.5)
    
    if not books:
        console.print("[bold red]Empty input file or missing required columns.[/bold red]")
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
            progress.update(task)

            if args.mode == 'text':
                title = book.get("Title", "")
                author = book.get("Author", "")
                
                matches_found = False

                if title and author:
                    for scraper in active_scrapers:
                        try:
                            found_items = scraper.search_by_text(title, author)
                            
                            for item in found_items:
                                row = book.copy()
                                
                                row['Store'] = scraper.store_name
                                row['Title Found'] = item.get('title_found')
                                row['Author Found'] = item.get('author_found')
                                row['Status'] = item.get('status', 'Unavailable')
                                row['Price'] = item.get('price', 0.0)
                                row['On Sale'] = "Yes" if item.get('on_sale') else "No"
                                row['Link'] = item.get('link', '')
                                
                                results.append(row)
                                matches_found = True

                        except Exception as e:
                            console.print(f"Error in {scraper.store_name}: {e}")
                            pass

            else:
                final_record = book.copy()
                final_record.pop('Identifier', None) 
                final_record.setdefault("Pages", 0)

                identifier = book.get("Identifier")

                if identifier:
                    for scraper in active_scrapers:
                        store_name = scraper.store_name
                        data = None
                        try:
                            data = scraper.scrape_by_isbn(identifier)
                        except Exception:
                            data = None

                        if data:
                            final_record["Title Match"] = data.get("title_found", "")
                            
                            if "pages" in data and data["pages"] > 0:
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
            
            # Delay aleatório
            time.sleep(random.uniform(1.5, 3.5))
            progress.advance(task)

    if save_results(results, args.output):
        console.print(f"\n[dodger_blue1]Done![/dodger_blue1] Output saved in: [underline]{args.output}[/underline]")
    else:
        console.print("\n[bold red]Saving output file error.[/bold red]")

if __name__ == "__main__":
    main()