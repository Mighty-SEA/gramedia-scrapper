import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import os
import re

class GramediaScraper:
    def __init__(self, headless=True):
        self.base_url = "https://www.gramedia.com"
        self.category_url = "https://www.gramedia.com/categories/buku"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Menyiapkan driver Selenium"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # Menggunakan headless=new untuk Chrome terbaru
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        
        # Tambahkan opsi untuk mengatasi masalah WebGL
        chrome_options.add_argument("--disable-webgl")
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        
        # Gunakan webdriver-manager untuk mengelola ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def collect_product_links(self, max_products=100):
        """Mengumpulkan link produk dari halaman kategori buku"""
        print(f"Mengakses halaman kategori: {self.category_url}")
        self.driver.get(self.category_url)
        product_links = []
        
        # Tunggu hingga halaman dimuat
        print("Menunggu halaman dimuat...")
        time.sleep(5)  # Tunggu sebentar untuk memastikan halaman dimuat
        
        # Coba beberapa selector yang mungkin untuk produk
        selectors = [
            ".product-card a[href*='/products/']",
            "a.product-title",
            ".product-item a[href*='/products/']",
            ".product-list-item a[href*='/products/']",
            "a[href*='/products/']"
        ]
        
        # Coba setiap selector
        product_elements = []
        for selector in selectors:
            try:
                print(f"Mencoba selector: {selector}")
                # Tunggu hingga elemen muncul
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                # Dapatkan elemen dengan selector ini
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Selector {selector} menemukan {len(elements)} elemen")
                    product_elements = elements
                    break
            except TimeoutException:
                print(f"Timeout menunggu elemen dengan selector: {selector}")
                continue
            except Exception as e:
                print(f"Error dengan selector {selector}: {str(e)}")
                continue
        
        if not product_elements:
            print("Tidak dapat menemukan elemen produk dengan semua selector yang dicoba")
            
            # Simpan HTML halaman untuk debugging
            with open("gramedia_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("HTML halaman disimpan ke gramedia_page.html untuk debugging")
            
            return []
        
        # Kumpulkan link dari elemen yang ditemukan
        for element in product_elements:
            try:
                href = element.get_attribute("href")
                if href and "/products/" in href:
                    link = href
                    if link not in product_links:
                        product_links.append(link)
                        print(f"Produk ditemukan: {len(product_links)}/{max_products}")
                    
                    if len(product_links) >= max_products:
                        break
            except Exception as e:
                print(f"Error saat mengambil link: {str(e)}")
                continue
        
        # Jika masih belum cukup produk, coba klik tombol "Muat Lebih Banyak"
        attempts = 0
        max_attempts = 10
        
        while len(product_links) < max_products and attempts < max_attempts:
            attempts += 1
            print(f"Mencoba memuat lebih banyak produk (percobaan {attempts}/{max_attempts})...")
            
            # Coba beberapa kemungkinan selector untuk tombol "Muat Lebih Banyak"
            load_more_selectors = [
                "button.load-more",
                ".load-more-button",
                "button[data-testid='load-more-button']",
                "a.load-more",
                ".pagination-next",
                "button:contains('Muat Lebih')",
                "button:contains('Load More')"
            ]
            
            clicked = False
            for selector in load_more_selectors:
                try:
                    # Scroll ke bagian bawah halaman
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    # Coba temukan tombol
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            print(f"Menemukan tombol 'Muat Lebih Banyak' dengan selector: {selector}")
                            self.driver.execute_script("arguments[0].click();", element)
                            clicked = True
                            time.sleep(3)  # Tunggu konten baru dimuat
                            break
                    
                    if clicked:
                        break
                except Exception as e:
                    print(f"Error dengan selector {selector}: {str(e)}")
                    continue
            
            if not clicked:
                print("Tidak dapat menemukan atau mengklik tombol 'Muat Lebih Banyak'")
                break
            
            # Ambil link produk baru
            new_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        new_elements = elements
                        break
                except Exception:
                    continue
            
            # Tambahkan link baru ke dalam list
            new_links_added = 0
            for element in new_elements:
                try:
                    href = element.get_attribute("href")
                    if href and "/products/" in href:
                        link = href
                        if link not in product_links:
                            product_links.append(link)
                            new_links_added += 1
                            print(f"Produk ditemukan: {len(product_links)}/{max_products}")
                        
                        if len(product_links) >= max_products:
                            break
                except Exception:
                    continue
            
            if new_links_added == 0:
                print("Tidak ada link produk baru yang ditemukan setelah mengklik tombol")
                break
        
        print(f"Total link produk yang dikumpulkan: {len(product_links)}")
        return product_links[:max_products]
    
    def extract_product_details(self, url):
        """Mengekstrak detail produk dari halaman produk"""
        print(f"Mengekstrak data dari: {url}")
        self.driver.get(url)
        
        # Tunggu hingga elemen judul dimuat
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            )
        except TimeoutException:
            print(f"Timeout menunggu halaman produk dimuat: {url}")
            return None
        
        time.sleep(3)  # Berikan waktu tambahan untuk memastikan semua konten dimuat
        
        # Simpan HTML halaman untuk debugging jika diperlukan
        # with open(f"debug_product_{url.split('/')[-1]}.html", "w", encoding="utf-8") as f:
        #     f.write(self.driver.page_source)
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        # Ekstrak data produk
        product_data = {
            "url": url,
            "nama_produk": self._get_text(soup, "h1"),
            "deskripsi": self._get_text(soup, "div.description, div[data-testid='product-description'], div[data-testid='productDetailDescriptionContainer']"),
            "detail_produk": {}
        }
        
        # Ekstrak detail produk menggunakan selector baru berdasarkan contoh HTML yang diberikan
        # Cari container detail buku
        detail_container = soup.select_one("div[data-testid='productDetailSpecificationContainer']")
        if detail_container:
            # Cari semua item detail
            detail_items = detail_container.select("div[data-testid^='productDetailSpecificationItem']")
            for item in detail_items:
                label_elem = item.select_one("div[data-testid='productDetailSpecificationItemLabel']")
                value_elem = item.select_one("div[data-testid='productDetailSpecificationItemValue']")
                
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    product_data["detail_produk"][label] = value
        
        # Jika detail produk masih kosong, coba pendekatan lain
        if not product_data["detail_produk"]:
            # Coba pendekatan lama
            detail_elements = soup.select("div.product-info-item, div.product-detail-item, div[data-testid='product-detail-item']")
            for element in detail_elements:
                label_elem = element.select_one("div.product-info-label, div.product-detail-label, div[data-testid='product-detail-label']")
                value_elem = element.select_one("div.product-info-value, div.product-detail-value, div[data-testid='product-detail-value']")
                
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True)
                    value = value_elem.get_text(strip=True)
                    product_data["detail_produk"][label] = value
        
        # Jika masih tidak menemukan detail, coba pendekatan lain
        if not product_data["detail_produk"]:
            # Cari dalam tabel detail buku
            detail_table = soup.select_one("table.book-detail, table[data-testid='book-detail']")
            if detail_table:
                rows = detail_table.select("tr")
                for row in rows:
                    cols = row.select("td")
                    if len(cols) >= 2:
                        label = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        product_data["detail_produk"][label] = value
        
        # Jika masih tidak menemukan detail, coba pendekatan lain dengan mencari pola dalam teks
        if not product_data["detail_produk"]:
            detail_section = soup.select_one("div.product-details, div.book-details, div[data-testid='product-details']")
            if detail_section:
                detail_text = detail_section.get_text()
                # Cari pola seperti "Penerbit: Gramedia" atau "ISBN: 1234567890"
                common_fields = ["Penerbit", "ISBN", "Bahasa", "Lebar", "Tanggal Terbit", "Halaman", "Panjang", "Berat"]
                for field in common_fields:
                    pattern = re.compile(f"{field}[\\s:]+([^\\n]+)")
                    match = pattern.search(detail_text)
                    if match:
                        product_data["detail_produk"][field] = match.group(1).strip()
        
        return product_data
    
    def _get_text(self, soup, selector, default=""):
        """Helper untuk mengambil teks dari elemen"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else default
    
    def scrape_products(self, max_products=100, output_file="gramedia_products.json"):
        """Proses utama untuk scraping produk"""
        product_links = self.collect_product_links(max_products)
        print(f"Berhasil mengumpulkan {len(product_links)} link produk")
        
        products_data = []
        for i, link in enumerate(product_links, 1):
            print(f"Memproses produk {i}/{len(product_links)}: {link}")
            product_data = self.extract_product_details(link)
            if product_data:
                products_data.append(product_data)
            time.sleep(1)  # Jeda untuk menghindari pembatasan akses
        
        # Simpan data ke file JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
        
        print(f"Scraping selesai. Data disimpan ke {output_file}")
        
    def close(self):
        """Menutup driver browser"""
        if hasattr(self, "driver"):
            self.driver.quit()

if __name__ == "__main__":
    scraper = GramediaScraper(headless=True)
    try:
        # Jumlah produk yang akan di-scrape (bisa diubah)
        num_products = 10
        scraper.scrape_products(max_products=num_products)
    finally:
        scraper.close() 