#!/usr/bin/env python
"""
Script untuk menjalankan scraper dalam mode debug.
Mode ini akan menjalankan browser dalam mode visible dan menyimpan HTML halaman.
"""
from gramedia_scraper import GramediaScraper
import time
import os
from selenium.webdriver.common.by import By

def main():
    print("Menjalankan Gramedia Scraper dalam mode debug...")
    
    # Buat direktori debug jika belum ada
    os.makedirs("debug", exist_ok=True)
    
    # Jalankan scraper dalam mode non-headless
    scraper = GramediaScraper(headless=False)
    
    try:
        # Akses halaman kategori
        print("Mengakses halaman kategori...")
        scraper.driver.get(scraper.category_url)
        time.sleep(5)  # Tunggu halaman dimuat
        
        # Simpan HTML halaman
        with open("debug/category_page.html", "w", encoding="utf-8") as f:
            f.write(scraper.driver.page_source)
        print("HTML halaman kategori disimpan ke debug/category_page.html")
        
        # Coba temukan produk pertama
        print("Mencoba menemukan produk...")
        selectors = [
            ".product-card a[href*='/products/']",
            "a.product-title",
            ".product-item a[href*='/products/']",
            ".product-list-item a[href*='/products/']",
            "a[href*='/products/']"
        ]
        
        for selector in selectors:
            elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Selector {selector} menemukan {len(elements)} elemen")
                
                # Ambil URL produk pertama
                first_product_url = elements[0].get_attribute("href")
                print(f"URL produk pertama: {first_product_url}")
                
                # Akses halaman produk
                print("Mengakses halaman produk...")
                scraper.driver.get(first_product_url)
                time.sleep(5)  # Tunggu halaman dimuat
                
                # Simpan HTML halaman produk
                with open("debug/product_page.html", "w", encoding="utf-8") as f:
                    f.write(scraper.driver.page_source)
                print("HTML halaman produk disimpan ke debug/product_page.html")
                
                break
        else:
            print("Tidak dapat menemukan produk dengan semua selector yang dicoba")
    
    finally:
        # Tunggu sebentar sebelum menutup browser
        print("Tunggu 10 detik sebelum menutup browser...")
        time.sleep(10)
        scraper.close()
    
    print("Debug selesai. Periksa folder 'debug' untuk hasil.")

if __name__ == "__main__":
    main() 