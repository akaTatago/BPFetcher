<div align="center">

# BPFetcher

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![curl-cffi](https://img.shields.io/badge/curl--cffi-latest-informational)
![playwright](https://img.shields.io/badge/playwright-latest-informational)
![pandas](https://img.shields.io/badge/pandas-latest-informational)

A **web scraping** CLI tool for price comparison across Portuguese bookstores.

Scrapes book prices and availability from **Wook**, **Bertrand**, **Fnac**, and **Almedina** using ISBN or text search.

[Getting Started](#getting-started) •
[Features](#features) •
[Usage](#usage) •
[Scrapers](#scrapers)

</div>

## Getting Started

Clone the repository
```bash
git clone https://github.com/akaTatago/BPFetcher.git
cd BPFetcher
```

Install dependencies
```bash
pip install -r requirements.txt
```

Install Playwright browsers (required for Fnac scraping)
```bash
playwright install chromium
```

Run the scraper
```bash
python -m src.main input.csv --output results.csv --stores all
```

<br />

## Features

- **Multiple Search Modes**: Search by ISBN-13 or by Title + Author
- **Multiple Stores Support**: Scrapes Wook, Bertrand, Fnac, and Almedina
- **Concurrent Scraping**: Fast parallel processing for non-browser scrapers
- **Smart Matching**: Validates book matches using normalized titles and authors
- **Price Tracking**: Detects sale prices and availability status
- **CSV Export**: Clean, structured output with all store data

<br />

## Usage

### Basic Usage
```bash
python -m src.main input.csv
```

### Search by ISBN (default)
```bash
python -m src.main books.csv --mode isbn --output results.csv
```

Your CSV should contain an `ISBN13` column:

| ISBN13          | Title              | Author        |
|-----------------|--------------------|---------------|
| 9780316769174   | The Catcher in... | J.D. Salinger |

### Search by Text
```bash
python -m src.main books.csv --mode text --output results.csv
```

Your CSV should contain `Title` and `Author` columns:

| Title                    | Author        |
|--------------------------|---------------|
| The Catcher in the Rye   | J.D. Salinger |

### Select Specific Stores
```bash
python -m src.main input.csv --stores wook fnac
```

Available stores: `wook`, `bertrand`, `fnac`, `almedina`, or `all` (default)

<br />

## Scrapers

### Request-Based Scrapers

**Wook**, **Bertrand**, and **Almedina** use `curl-cffi` for fast HTTP requests with browser impersonation.

- Randomized delays to avoid rate limiting
- Concurrent execution via **ThreadPoolExecutor**
- Efficient parsing with **BeautifulSoup**

### Browser-Based Scraper

**Fnac** uses `Playwright` due to anti-bot protection:

- Headless Chromium browser
- Automatic CAPTCHA detection (manual solve required)
- Cookie consent handling
- Stealth mode with webdriver detection disabled

<br />

## Output Format

### ISBN Mode

Creates one row per book with columns for each store:
```
Title, Author, Wook Status, Wook Price, Wook On Sale, Wook Link, Bertrand Status, ...
```

### Text Mode

Creates multiple rows per book (one per matching result):
```
Title, Author, Store, Title Found, Author Found, Status, Price, On Sale, Link
```

<br />

## Architecture
```
BPFetcher/
├── main.py                 # CLI entry point
├── requirements.txt
├── src/
│   ├── scrapers/
│   │   ├── base_scraper.py    # Abstract base class
│   │   ├── wook.py            # Wook scraper
│   │   ├── bertrand.py        # Bertrand scraper
│   │   ├── fnac.py            # Fnac scraper (Playwright)
│   │   └── almedina.py        # Almedina scraper
│   └── utils/
│       ├── scraping_helper.py # Shared scraping utilities
│       └── csv_helper.py      # CSV loading/saving
└── data/
    └── results.csv         # Default output location
```

<br />