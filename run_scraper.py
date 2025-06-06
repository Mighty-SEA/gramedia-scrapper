#!/usr/bin/env python
import argparse
from gramedia_scraper import GramediaScraper

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Gramedia Book Scraper")
    parser.add_argument("-n", "--num-products", type=int, default=10,
                        help="Number of products to scrape (default: 10)")
    parser.add_argument("-o", "--output", type=str, default="gramedia_products.json",
                        help="Output JSON file (default: gramedia_products.json)")
    parser.add_argument("--no-headless", action="store_true",
                        help="Run in non-headless mode (browser visible)")
    args = parser.parse_args()
    
    # Run scraper
    print(f"Memulai scraping {args.num_products} produk dari Gramedia...")
    scraper = GramediaScraper(headless=not args.no_headless)
    try:
        scraper.scrape_products(max_products=args.num_products, output_file=args.output)
    finally:
        scraper.close()
    
    print(f"Proses selesai. Data disimpan ke {args.output}")

if __name__ == "__main__":
    main() 