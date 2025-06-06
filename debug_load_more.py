#!/usr/bin/env python
"""
Script untuk menguji tombol "Muat Lebih Banyak" pada situs Gramedia.
"""
from gramedia_scraper import GramediaScraper
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    print("Menjalankan pengujian tombol 'Muat Lebih Banyak'...")
    
    # Buat direktori debug jika belum ada
    os.makedirs("debug", exist_ok=True)
    
    # Jalankan scraper dalam mode non-headless
    scraper = GramediaScraper(headless=False)
    
    try:
        # Akses halaman kategori
        print("Mengakses halaman kategori...")
        scraper.driver.get(scraper.category_url)
        time.sleep(5)  # Tunggu halaman dimuat
        
        # Simpan HTML halaman awal
        with open("debug/category_page_initial.html", "w", encoding="utf-8") as f:
            f.write(scraper.driver.page_source)
        print("HTML halaman kategori awal disimpan ke debug/category_page_initial.html")
        
        # Hitung jumlah produk awal
        product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
        initial_product_count = len(product_elements)
        print(f"Jumlah produk awal: {initial_product_count}")
        
        # Scroll ke bagian bawah halaman
        print("Scrolling ke bagian bawah halaman...")
        scraper.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Cari tombol "Muat Lebih Banyak" dengan berbagai metode
        print("Mencari tombol 'Muat Lebih Banyak'...")
        
        # 1. Berdasarkan data-testid
        try:
            button = scraper.driver.find_element(By.CSS_SELECTOR, "button[data-testid='categoriesLoadMore']")
            print("Tombol ditemukan dengan selector: button[data-testid='categoriesLoadMore']")
            print(f"Teks tombol: '{button.text}'")
            print(f"Terlihat: {button.is_displayed()}, Aktif: {button.is_enabled()}")
            
            # Ambil screenshot tombol
            scraper.driver.save_screenshot("debug/before_click.png")
            
            # Klik tombol
            print("Mengklik tombol...")
            scraper.driver.execute_script("arguments[0].click();", button)
            time.sleep(5)  # Tunggu konten baru dimuat
            
            # Ambil screenshot setelah klik
            scraper.driver.save_screenshot("debug/after_click.png")
            
            # Hitung jumlah produk setelah klik
            product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            new_product_count = len(product_elements)
            print(f"Jumlah produk setelah klik: {new_product_count}")
            print(f"Produk baru ditambahkan: {new_product_count - initial_product_count}")
            
            # Simpan HTML halaman setelah klik
            with open("debug/category_page_after_click.html", "w", encoding="utf-8") as f:
                f.write(scraper.driver.page_source)
            print("HTML halaman setelah klik disimpan ke debug/category_page_after_click.html")
            
        except Exception as e:
            print(f"Tidak dapat menemukan tombol dengan data-testid: {str(e)}")
            
            # 2. Coba dengan teks tombol
            try:
                buttons = scraper.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        button_text = button.text.strip()
                        if "Muat Lebih Banyak" in button_text:
                            print(f"Tombol ditemukan dengan teks: '{button_text}'")
                            print(f"Terlihat: {button.is_displayed()}, Aktif: {button.is_enabled()}")
                            
                            # Ambil screenshot tombol
                            scraper.driver.save_screenshot("debug/before_click_text.png")
                            
                            # Klik tombol
                            print("Mengklik tombol...")
                            scraper.driver.execute_script("arguments[0].click();", button)
                            time.sleep(5)  # Tunggu konten baru dimuat
                            
                            # Ambil screenshot setelah klik
                            scraper.driver.save_screenshot("debug/after_click_text.png")
                            
                            # Hitung jumlah produk setelah klik
                            product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
                            new_product_count = len(product_elements)
                            print(f"Jumlah produk setelah klik: {new_product_count}")
                            print(f"Produk baru ditambahkan: {new_product_count - initial_product_count}")
                            
                            # Simpan HTML halaman setelah klik
                            with open("debug/category_page_after_click_text.html", "w", encoding="utf-8") as f:
                                f.write(scraper.driver.page_source)
                            print("HTML halaman setelah klik disimpan ke debug/category_page_after_click_text.html")
                            break
                    except:
                        continue
                else:
                    print("Tidak dapat menemukan tombol dengan teks 'Muat Lebih Banyak'")
                    
                    # 3. Coba dengan XPath
                    try:
                        button = scraper.driver.find_element(By.XPATH, "//button[contains(text(), 'Muat Lebih Banyak')]")
                        print("Tombol ditemukan dengan XPath: //button[contains(text(), 'Muat Lebih Banyak')]")
                        print(f"Teks tombol: '{button.text}'")
                        print(f"Terlihat: {button.is_displayed()}, Aktif: {button.is_enabled()}")
                        
                        # Ambil screenshot tombol
                        scraper.driver.save_screenshot("debug/before_click_xpath.png")
                        
                        # Klik tombol
                        print("Mengklik tombol...")
                        scraper.driver.execute_script("arguments[0].click();", button)
                        time.sleep(5)  # Tunggu konten baru dimuat
                        
                        # Ambil screenshot setelah klik
                        scraper.driver.save_screenshot("debug/after_click_xpath.png")
                        
                        # Hitung jumlah produk setelah klik
                        product_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
                        new_product_count = len(product_elements)
                        print(f"Jumlah produk setelah klik: {new_product_count}")
                        print(f"Produk baru ditambahkan: {new_product_count - initial_product_count}")
                        
                        # Simpan HTML halaman setelah klik
                        with open("debug/category_page_after_click_xpath.html", "w", encoding="utf-8") as f:
                            f.write(scraper.driver.page_source)
                        print("HTML halaman setelah klik disimpan ke debug/category_page_after_click_xpath.html")
                    except Exception as e:
                        print(f"Tidak dapat menemukan tombol dengan XPath: {str(e)}")
                        
                        # Simpan semua informasi tombol yang ada di halaman
                        print("Mencari semua tombol di halaman...")
                        buttons = scraper.driver.find_elements(By.TAG_NAME, "button")
                        with open("debug/all_buttons.txt", "w", encoding="utf-8") as f:
                            for i, btn in enumerate(buttons):
                                try:
                                    f.write(f"Tombol #{i+1}:\n")
                                    f.write(f"  Teks: '{btn.text}'\n")
                                    f.write(f"  Terlihat: {btn.is_displayed()}\n")
                                    f.write(f"  Aktif: {btn.is_enabled()}\n")
                                    f.write(f"  Class: {btn.get_attribute('class')}\n")
                                    f.write(f"  ID: {btn.get_attribute('id')}\n")
                                    f.write(f"  data-testid: {btn.get_attribute('data-testid')}\n")
                                    f.write("\n")
                                except:
                                    f.write(f"  Error saat mendapatkan informasi tombol #{i+1}\n\n")
                        print("Informasi semua tombol disimpan ke debug/all_buttons.txt")
                        
                        # Simpan HTML halaman untuk debugging
                        with open("debug/category_page_final.html", "w", encoding="utf-8") as f:
                            f.write(scraper.driver.page_source)
                        print("HTML halaman final disimpan ke debug/category_page_final.html")
            except Exception as e:
                print(f"Error saat mencari tombol berdasarkan teks: {str(e)}")
    
    finally:
        # Tunggu sebentar sebelum menutup browser
        print("Tunggu 10 detik sebelum menutup browser...")
        time.sleep(10)
        scraper.close()
    
    print("Pengujian selesai. Periksa folder 'debug' untuk hasil.")

if __name__ == "__main__":
    main() 