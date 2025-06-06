#!/usr/bin/env python
"""
Script untuk menguji berapa banyak produk maksimal yang bisa diambil dengan tombol "Muat Lebih Banyak".
Script ini akan terus mengklik tombol sampai tombol tidak tersedia lagi.
"""
from gramedia_scraper import GramediaScraper
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def main():
    print("Menjalankan pengujian batas maksimal tombol 'Muat Lebih Banyak'...")
    
    # Buat direktori debug jika belum ada
    os.makedirs("debug", exist_ok=True)
    
    # Jalankan scraper dalam mode non-headless
    scraper = GramediaScraper(headless=False)
    
    try:
        # Akses halaman kategori
        print("Mengakses halaman kategori...")
        scraper.driver.get(scraper.category_url)
        time.sleep(5)  # Tunggu halaman dimuat
        
        # Hitung jumlah produk awal
        product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        initial_product_count = len(product_elements)
        print(f"Jumlah produk awal: {initial_product_count}")
        
        # Simpan semua URL produk yang ditemukan
        product_urls = set()
        for element in product_elements:
            try:
                href = element.get_attribute("href")
                if href and "/products/" in href:
                    product_urls.add(href)
            except:
                continue
        
        print(f"Jumlah URL produk unik awal: {len(product_urls)}")
        
        # Klik tombol "Muat Lebih Banyak" sampai tidak tersedia lagi
        click_count = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while consecutive_failures < max_consecutive_failures:
            # Scroll ke bagian bawah halaman
            scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            try:
                # Cari tombol "Muat Lebih Banyak"
                button = scraper.driver.find_element(By.CSS_SELECTOR, "button[data-testid='categoriesLoadMore']")
                
                if button.is_displayed() and button.is_enabled():
                    print(f"Klik #{click_count + 1}: Menemukan tombol 'Muat Lebih Banyak'")
                    
                    # Ambil screenshot sebelum klik
                    scraper.driver.save_screenshot(f"debug/before_click_{click_count + 1}.png")
                    
                    # Klik tombol
                    scraper.driver.execute_script("arguments[0].click();", button)
                    click_count += 1
                    
                    # Tunggu konten baru dimuat
                    print("Menunggu konten baru dimuat...")
                    time.sleep(3)
                    
                    # Ambil screenshot setelah klik
                    scraper.driver.save_screenshot(f"debug/after_click_{click_count}.png")
                    
                    # Hitung jumlah produk setelah klik
                    product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
                    new_product_count = len(product_elements)
                    
                    # Hitung URL produk baru
                    new_urls = set()
                    for element in product_elements:
                        try:
                            href = element.get_attribute("href")
                            if href and "/products/" in href:
                                new_urls.add(href)
                        except:
                            continue
                    
                    # Hitung produk baru yang ditambahkan
                    added_urls = new_urls - product_urls
                    product_urls = new_urls
                    
                    print(f"Jumlah produk setelah klik #{click_count}: {new_product_count}")
                    print(f"Jumlah URL produk unik: {len(product_urls)}")
                    print(f"Produk baru ditambahkan: {len(added_urls)}")
                    
                    if len(added_urls) == 0:
                        consecutive_failures += 1
                        print(f"Tidak ada produk baru yang ditambahkan ({consecutive_failures}/{max_consecutive_failures})")
                    else:
                        consecutive_failures = 0  # Reset counter jika berhasil menambahkan produk
                else:
                    print("Tombol ditemukan tetapi tidak terlihat atau tidak aktif")
                    consecutive_failures += 1
                    print(f"Tombol tidak aktif ({consecutive_failures}/{max_consecutive_failures})")
            except NoSuchElementException:
                print("Tidak dapat menemukan tombol 'Muat Lebih Banyak'")
                consecutive_failures += 1
                print(f"Tombol tidak ditemukan ({consecutive_failures}/{max_consecutive_failures})")
                
                # Simpan HTML halaman untuk debugging
                with open(f"debug/page_after_{click_count}_clicks.html", "w", encoding="utf-8") as f:
                    f.write(scraper.driver.page_source)
            except StaleElementReferenceException:
                print("Elemen tombol sudah tidak valid (stale). Mencoba lagi...")
                time.sleep(2)
                continue
            except Exception as e:
                print(f"Error saat mengklik tombol: {str(e)}")
                consecutive_failures += 1
                print(f"Error ({consecutive_failures}/{max_consecutive_failures})")
        
        # Simpan HTML halaman final
        with open("debug/final_page.html", "w", encoding="utf-8") as f:
            f.write(scraper.driver.page_source)
        
        print("\n=== Hasil Pengujian ===")
        print(f"Total klik tombol 'Muat Lebih Banyak': {click_count}")
        print(f"Total produk yang berhasil diambil: {len(product_urls)}")
        
        # Simpan semua URL produk ke file
        with open("debug/all_product_urls.txt", "w", encoding="utf-8") as f:
            for url in sorted(product_urls):
                f.write(f"{url}\n")
        print("Semua URL produk disimpan ke debug/all_product_urls.txt")
    
    finally:
        # Tunggu sebentar sebelum menutup browser
        print("Tunggu 10 detik sebelum menutup browser...")
        time.sleep(10)
        scraper.close()
    
    print("Pengujian selesai. Periksa folder 'debug' untuk hasil.")

if __name__ == "__main__":
    main() 