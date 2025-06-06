#!/usr/bin/env python
import argparse
import sys
from gramedia_scraper import GramediaScraper, debug_print

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Gramedia Book Scraper")
    parser.add_argument("-n", "--num-products", type=int, default=10,
                        help="Number of products to scrape (default: 10)")
    parser.add_argument("-o", "--output", type=str, default="gramedia_products.json",
                        help="Output JSON file (default: gramedia_products.json)")
    parser.add_argument("--no-headless", action="store_true",
                        help="Run in non-headless mode (browser visible)")
    parser.add_argument("-c", "--concurrent", type=int, default=10,
                        help="Number of concurrent product extractions (default: 10)")
    args = parser.parse_args()
    
    # Pastikan output tidak di-buffer
    sys.stdout.reconfigure(line_buffering=True)
    
    # Run scraper
    debug_print(f"Memulai scraping {args.num_products} produk dari Gramedia dengan {args.concurrent} ekstraksi paralel...")
    scraper = GramediaScraper(headless=not args.no_headless)
    try:
        scraper.scrape_products(max_products=args.num_products, output_file=args.output, concurrent_extractions=args.concurrent)
    finally:
        scraper.close()
    
    debug_print(f"Proses selesai. Data disimpan ke {args.output}")

if __name__ == "__main__":
    main() 