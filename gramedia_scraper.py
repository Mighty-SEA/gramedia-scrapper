import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
import json
import os
import re
import concurrent.futures
import sys

# Fungsi debug print khusus
def debug_print(message):
    """Print debug message dengan flush untuk memastikan output langsung terlihat"""
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] {message}", flush=True)
    sys.stdout.flush()
    # Tambahkan jeda kecil untuk memastikan output terlihat
    time.sleep(0.01)

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
        debug_print(f"Mengakses halaman kategori: {self.category_url}")
        self.driver.get(self.category_url)
        product_links = []
        
        # Tunggu hingga halaman dimuat
        debug_print("Menunggu halaman dimuat...")
        time.sleep(5)  # Tunggu sebentar untuk memastikan halaman dimuat
        
        # Langsung gunakan selector yang terbukti bekerja
        debug_print("Mencari produk dengan selector: a[href*='/products/']")
        try:
            # Tunggu hingga elemen muncul
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/products/']"))
            )
            # Dapatkan elemen dengan selector ini
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
            debug_print(f"Selector a[href*='/products/'] menemukan {len(product_elements)} elemen")
            
            # Debug: Tampilkan beberapa URL yang ditemukan
            debug_count = min(5, len(product_elements))
            debug_print(f"Debug - {debug_count} URL pertama yang ditemukan:")
            for i in range(debug_count):
                try:
                    href = product_elements[i].get_attribute("href")
                    debug_print(f"  {i+1}. {href}")
                except Exception as e:
                    debug_print(f"  {i+1}. Error: {str(e)}")
                    
        except TimeoutException:
            debug_print(f"Timeout menunggu elemen dengan selector: a[href*='/products/']")
            
            # Simpan HTML halaman untuk debugging
            with open("gramedia_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            debug_print("HTML halaman disimpan ke gramedia_page.html untuk debugging")
            
            return []
        except Exception as e:
            debug_print(f"Error saat mencari produk: {str(e)}")
            
            # Simpan HTML halaman untuk debugging
            with open("gramedia_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            debug_print("HTML halaman disimpan ke gramedia_page.html untuk debugging")
            
            return []
        
        # Kumpulkan link dari elemen yang ditemukan
        added_count = 0
        debug_print(f"Mulai mengumpulkan link produk dari {len(product_elements)} elemen...")
        for element in product_elements:
            try:
                href = element.get_attribute("href")
                if href and "/products/" in href:
                    link = href
                    if link not in product_links:
                        product_links.append(link)
                        added_count += 1
                        debug_print(f"Produk #{added_count} ditemukan: {link}")
                    
                    if len(product_links) >= max_products:
                        debug_print(f"Berhasil mengumpulkan {max_products} produk sesuai target.")
                        debug_print(f"Total link produk yang dikumpulkan: {len(product_links)}")
                        break
            except Exception as e:
                debug_print(f"Error saat mengambil link: {str(e)}")
                continue
        
        debug_print(f"Selesai mengumpulkan link. Berhasil menambahkan {added_count} produk.")
        
        if len(product_links) < max_products:
            debug_print(f"Perlu lebih banyak produk. Mencoba tombol 'Muat Lebih Banyak'...")
            # Panggil fungsi untuk memuat lebih banyak produk jika diperlukan
            product_links = self._load_more_products(product_links, max_products)
        
        debug_print(f"Total link produk yang dikumpulkan: {len(product_links)}")
        return product_links[:max_products]
    
    def _extract_categories_from_breadcrumb(self, soup):
        """Mengekstrak kategori produk dari breadcrumb"""
        categories = []
        found_buku = False
        
        # Coba berbagai selector untuk container breadcrumb
        breadcrumb_container_selectors = [
            "div[data-testid='breadcrumb']",
            "nav.breadcrumb",
            "div.breadcrumbs",
            "div[class*='breadcrumb']",
            "ol.breadcrumb",
            "ul.breadcrumb",
            "div[data-id='productDetailBreadcrumbs']", 
            "div[data-testid='productDetailBreadcrumbs']", 
            "nav[aria-label='breadcrumb']",
            ".breadcrumbs",
            ".breadcrumb-container",
            "[itemprop='breadcrumb']"
        ]
        
        breadcrumb_container = None
        for selector in breadcrumb_container_selectors:
            container = soup.select_one(selector)
            if container:
                debug_print(f"Menemukan container breadcrumb dengan selector: {selector}")
                breadcrumb_container = container
                break
                
        if not breadcrumb_container:
            debug_print("Tidak dapat menemukan container breadcrumb dengan selector standar")
            # Mencoba alternatif lain: cari elemen dengan class yang mengandung 'breadcrumb'
            breadcrumb_classes = soup.find_all(class_=lambda c: c and 'breadcrumb' in c.lower())
            if breadcrumb_classes:
                debug_print(f"Menemukan elemen dengan class breadcrumb: {breadcrumb_classes[0].name}")
                breadcrumb_container = breadcrumb_classes[0]
            else:
                debug_print("Tidak dapat menemukan elemen dengan class breadcrumb")
                return categories
            
        # Coba berbagai selector untuk item breadcrumb
        breadcrumb_item_selectors = [
            "li.breadcrumb-item a",
            "li a",
            "a[href*='/categories/']",
            "a",
            "span.breadcrumb-item",
            "span",
            "div.breadcrumb-item",
            "[data-testid='breadcrumb-item']",
            ".breadcrumb-item a",
            "[data-testid^='categoriesBreadcrumbsItem'] a",
            "[data-testid^='productDetailBreadcrumbsCategory'] a"
        ]
        
        breadcrumb_items = []
        for selector in breadcrumb_item_selectors:
            items = breadcrumb_container.select(selector)
            if items:
                debug_print(f"Menemukan {len(items)} item breadcrumb dengan selector: {selector}")
                breadcrumb_items = items
                break
                
        if not breadcrumb_items:
            debug_print("Tidak dapat menemukan item breadcrumb dengan selector standar")
            # Coba alternatif: semua link dalam container
            all_links = breadcrumb_container.find_all('a')
            if all_links:
                debug_print(f"Menemukan {len(all_links)} link dalam container breadcrumb")
                breadcrumb_items = all_links
            else:
                debug_print("Tidak ada link dalam container breadcrumb")
                return categories
            
        # Iterasi melalui item breadcrumb
        debug_print("Item breadcrumb yang ditemukan:")
        for item in breadcrumb_items:
            text = item.get_text(strip=True)
            href = item.get("href", "")
            debug_print(f"  - {text} ({href})")
            
            # Tandai jika menemukan "Buku"
            if text.lower() == "buku":
                found_buku = True
                debug_print(f"    Menemukan 'Buku' di breadcrumb")
                continue  # Lewati "Buku" itu sendiri
            
            # Ambil kategori setelah "Buku"
            if found_buku and text.lower() != "home":
                categories.append(text)
                debug_print(f"    Menambahkan kategori: {text}")
            # Jika tidak menemukan "Buku" namun memiliki "/categories/buku/" dalam href
            elif not found_buku and href and "/categories/buku/" in href:
                categories.append(text)
                debug_print(f"    Menambahkan kategori dari URL: {text}")
        
        # Jika tidak menemukan kategori dengan cara di atas, coba cari dengan cara lain
        if not categories:
            # Coba cari semua link di breadcrumb yang mengandung "/categories/buku/"
            category_links = soup.select("a[href*='/categories/buku/']")
            for link in category_links:
                text = link.get_text(strip=True)
                if text.lower() != "buku" and text.lower() != "home":
                    categories.append(text)
                    debug_print(f"Menambahkan kategori dari link alternatif: {text}")
            
            # Jika masih tidak menemukan, coba cari dengan URL yang berisi 'category'
            if not categories:
                category_links = soup.select("a[href*='category']")
                for link in category_links:
                    text = link.get_text(strip=True)
                    if text.lower() != "buku" and text.lower() != "home" and text != "":
                        categories.append(text)
                        debug_print(f"Menambahkan kategori dari link dengan 'category': {text}")
        
        debug_print(f"Kategori yang ditemukan: {categories}")
        return categories
        
    def extract_product_details(self, url):
        """Mengekstrak detail produk dari halaman produk"""
        debug_print(f"Mengekstrak data dari: {url}")
        self.driver.get(url)
        
        # Tunggu hingga elemen judul dimuat
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            )
        except TimeoutException:
            debug_print(f"Timeout menunggu halaman produk dimuat: {url}")
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
        
        # Ekstrak kategori dari breadcrumb
        categories = self._extract_categories_from_breadcrumb(soup)
        if categories:
            product_data["kategori"] = ",".join(categories)
        
        # Ekstrak URL gambar produk
        product_data["gambar_url"] = self._extract_product_image(soup, url)
        
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
    
    def _extract_product_image(self, soup, url=""):
        """Mengekstrak URL gambar produk dari halaman produk"""
        # Coba beberapa selector yang mungkin untuk gambar produk
        image_selectors = [
            "img.product-main-image",
            "div.product-gallery__main-image img",
            "div.product-image-container img",
            "div.product-detail-image img",
            "div[data-testid='productDetailGallery'] img",
            "div[data-testid='productGallery'] img",
            "div.product-detail__gallery img",
            "div.product-image img",
            "img[alt*='product']",
            "img[alt*='buku']",
            "img.product-image",
            "img.product-detail-image",
            "img[data-testid='productImage']"
        ]
        
        # Coba dapatkan URL gambar dengan selector
        for selector in image_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.has_attr("src"):
                src = img_elem.get("src")
                # Filter URL yang bukan URL gambar (menghindari URL pelacakan)
                if src and (src.startswith("http") or src.startswith("/")) and self._is_image_url(src):
                    # Jika URL relatif, tambahkan domain
                    if src.startswith("/"):
                        src = f"https://www.gramedia.com{src}"
                    return src
            
            # Coba dengan data-src jika src tidak ada
            if img_elem and img_elem.has_attr("data-src"):
                data_src = img_elem.get("data-src")
                if data_src and (data_src.startswith("http") or data_src.startswith("/")) and self._is_image_url(data_src):
                    # Jika URL relatif, tambahkan domain
                    if data_src.startswith("/"):
                        data_src = f"https://www.gramedia.com{data_src}"
                    return data_src
        
        # Jika tidak menemukan dengan selector, cari semua img dan pilih yang paling relevan
        all_images = soup.select("img")
        for img in all_images:
            if img.has_attr("src"):
                src = img.get("src")
                # Cek apakah ini kemungkinan gambar produk
                if src and self._is_image_url(src) and not ("icon" in src or "logo" in src):
                    if src.startswith("/"):
                        src = f"https://www.gramedia.com{src}"
                    return src
            
            # Coba dengan data-src
            if img.has_attr("data-src"):
                data_src = img.get("data-src")
                if data_src and self._is_image_url(data_src) and not ("icon" in data_src or "logo" in data_src):
                    if data_src.startswith("/"):
                        data_src = f"https://www.gramedia.com{data_src}"
                    return data_src
        
        # Coba dengan JavaScript untuk mendapatkan gambar produk
        try:
            # Coba dapatkan URL gambar dengan JavaScript
            js_image_url = self.driver.execute_script("""
                // Coba dapatkan elemen gambar utama
                var imgSelectors = [
                    'img.product-main-image',
                    'div.product-gallery__main-image img',
                    'div.product-image-container img',
                    'div.product-detail-image img',
                    'div[data-testid="productDetailGallery"] img',
                    'div[data-testid="productGallery"] img',
                    'div.product-detail__gallery img',
                    'div.product-image img',
                    'img.product-image',
                    'img.product-detail-image',
                    'img[data-testid="productImage"]'
                ];
                
                for (var i = 0; i < imgSelectors.length; i++) {
                    var img = document.querySelector(imgSelectors[i]);
                    if (img) {
                        var src = img.src || img.dataset.src;
                        if (src && (src.endsWith('.jpg') || src.endsWith('.jpeg') || 
                                   src.endsWith('.png') || src.endsWith('.webp') || 
                                   src.includes('/images/') || src.includes('/img/'))) {
                            return src;
                        }
                    }
                }
                
                // Jika tidak menemukan dengan selector spesifik, cari semua img
                var allImages = document.querySelectorAll('img');
                for (var i = 0; i < allImages.length; i++) {
                    var src = allImages[i].src || allImages[i].dataset.src;
                    if (src && (src.endsWith('.jpg') || src.endsWith('.jpeg') || 
                               src.endsWith('.png') || src.endsWith('.webp') || 
                               src.includes('/images/') || src.includes('/img/')) && 
                        !(src.includes('icon') || src.includes('logo'))) {
                        return src;
                    }
                }
                
                return null;
            """)
            
            if js_image_url and self._is_image_url(js_image_url):
                return js_image_url
        except Exception as e:
            debug_print(f"Error saat mengambil URL gambar dengan JavaScript: {str(e)}")
        
        # Jika masih tidak menemukan, coba dengan cara lain
        try:
            # Ambil screenshot elemen gambar produk jika ada
            product_image_elem = None
            for selector in image_selectors:
                try:
                    product_image_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if product_image_elem:
                        break
                except:
                    continue
            
            if product_image_elem:
                # Buat direktori untuk menyimpan gambar jika belum ada
                os.makedirs("product_images", exist_ok=True)
                
                # Ambil nama file dari URL produk
                product_id = url.split('/')[-1]
                image_path = f"product_images/{product_id}.png"
                
                # Ambil screenshot elemen gambar
                product_image_elem.screenshot(image_path)
                debug_print(f"Gambar produk disimpan ke {image_path}")
                
                # Kembalikan path lokal gambar
                return image_path
        except Exception as e:
            debug_print(f"Error saat mengambil screenshot gambar produk: {str(e)}")
        
        return ""  # Return string kosong jika tidak menemukan gambar
    
    def _is_image_url(self, url):
        """Memeriksa apakah URL adalah URL gambar yang valid"""
        # Cek ekstensi file gambar umum
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        if any(url.lower().endswith(ext) for ext in image_extensions):
            return True
        
        # Cek path yang umum digunakan untuk gambar
        image_paths = ['/images/', '/img/', '/photos/', '/product/', '/products/', '/cover/', '/covers/', 
                      'image.gramedia.net', 'cdn.gramedia.com']
        if any(path in url.lower() for path in image_paths):
            return True
        
        # Hindari URL pelacakan dan skrip
        tracking_patterns = ['track.', 'tracking.', 'analytics.', 'pixel.', 'beacon.', 
                           'adsct', 'omguk.com', 'javascript:', 'data:']
        if any(pattern in url.lower() for pattern in tracking_patterns):
            return False
        
        return False
    
    def _get_text(self, soup, selector, default=""):
        """Helper untuk mengambil teks dari elemen"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else default
    
    def scrape_products(self, max_products=100, output_file="gramedia_products.json", concurrent_extractions=10):
        """Proses utama untuk scraping produk dengan dukungan ekstraksi paralel"""
        product_links = self.collect_product_links(max_products)
        debug_print(f"Berhasil mengumpulkan {len(product_links)} link produk")
        
        products_data = []
        
        # Buat fungsi untuk menjalankan ekstraksi
        def extract_product(link, index):
            debug_print(f"Memproses produk {index+1}/{len(product_links)}: {link}")
            # Buat driver terpisah untuk setiap thread
            try:
                chrome_options = Options()
                chrome_options.add_argument("--headless=new")  # Selalu gunakan headless untuk thread
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-notifications")
                chrome_options.add_argument("--disable-popup-blocking")
                chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
                chrome_options.add_argument("--disable-webgl")
                chrome_options.add_argument("--enable-unsafe-swiftshader")
                
                thread_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                
                # Kunjungi URL
                thread_driver.get(link)
                
                # Tunggu hingga elemen judul dimuat
                try:
                    WebDriverWait(thread_driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                    )
                except TimeoutException:
                    debug_print(f"Timeout menunggu halaman produk dimuat: {link}")
                    thread_driver.quit()
                    return None
                
                time.sleep(3)  # Berikan waktu tambahan untuk memastikan semua konten dimuat
                
                soup = BeautifulSoup(thread_driver.page_source, "html.parser")
                
                # Ekstrak data produk
                product_data = {
                    "url": link,
                    "nama_produk": self._get_text(soup, "h1"),
                    "deskripsi": self._get_text(soup, "div.description, div[data-testid='product-description'], div[data-testid='productDetailDescriptionContainer']"),
                    "detail_produk": {}
                }
                
                # Ekstrak kategori dari breadcrumb - menggunakan pendekatan alternatif untuk thread
                categories = []
                
                # Coba beberapa pendekatan untuk breadcrumb
                # 1. Gunakan JavaScript untuk mengekstrak breadcrumb
                try:
                    js_breadcrumb = thread_driver.execute_script("""
                        // Cari breadcrumb menggunakan berbagai selector
                        var breadcrumbSelectors = [
                            "div[data-testid='breadcrumb']",
                            "nav.breadcrumb",
                            "div.breadcrumbs",
                            "div[class*='breadcrumb']",
                            "ol.breadcrumb",
                            "ul.breadcrumb",
                            "div[data-id='productDetailBreadcrumbs']", 
                            "div[data-testid='productDetailBreadcrumbs']", 
                            "nav[aria-label='breadcrumb']"
                        ];
                        
                        // Cari container breadcrumb
                        var container = null;
                        for (var i = 0; i < breadcrumbSelectors.length; i++) {
                            container = document.querySelector(breadcrumbSelectors[i]);
                            if (container) break;
                        }
                        
                        if (!container) return [];
                        
                        // Cari semua link dalam breadcrumb
                        var links = container.querySelectorAll('a');
                        var categories = [];
                        var foundBuku = false;
                        
                        for (var i = 0; i < links.length; i++) {
                            var text = links[i].textContent.trim();
                            if (text.toLowerCase() === 'buku') {
                                foundBuku = true;
                                continue;
                            }
                            
                            if (foundBuku && text.toLowerCase() !== 'home') {
                                categories.push(text);
                            }
                        }
                        
                        // Jika tidak menemukan kategori dengan cara di atas, coba cara lain
                        if (categories.length === 0) {
                            var categoryLinks = document.querySelectorAll("a[href*='/categories/buku/']");
                            for (var i = 0; i < categoryLinks.length; i++) {
                                var text = categoryLinks[i].textContent.trim();
                                if (text.toLowerCase() !== 'buku' && text.toLowerCase() !== 'home') {
                                    categories.push(text);
                                }
                            }
                        }
                        
                        return categories;
                    """)
                    
                    if js_breadcrumb and len(js_breadcrumb) > 0:
                        categories = js_breadcrumb
                        debug_print(f"Kategori yang ditemukan dengan JavaScript: {categories}")
                except Exception as e:
                    debug_print(f"Error saat mengekstrak breadcrumb dengan JavaScript: {str(e)}")
                
                # 2. Jika JavaScript gagal, coba dengan BeautifulSoup
                if not categories:
                    categories = self._extract_categories_from_breadcrumb(soup)
                
                # 3. Jika masih kosong, coba cari link kategori di halaman
                if not categories:
                    category_links = soup.select("a[href*='/categories/']")
                    for link in category_links:
                        text = link.get_text(strip=True)
                        href = link.get("href", "")
                        if "categories/buku" in href and text.lower() != "buku" and text.lower() != "home":
                            categories.append(text)
                
                if categories:
                    product_data["kategori"] = ",".join(categories)
                
                # Ekstrak URL gambar produk
                product_data["gambar_url"] = self._extract_product_image(soup, link)
                
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
                
                thread_driver.quit()
                return product_data
            except Exception as e:
                debug_print(f"Error saat mengekstrak produk {link}: {str(e)}")
                if 'thread_driver' in locals():
                    thread_driver.quit()
                return None
        
        # Proses link secara paralel dalam batch
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_extractions) as executor:
            futures = []
            for i, link in enumerate(product_links):
                futures.append(executor.submit(extract_product, link, i))
            
            for future in concurrent.futures.as_completed(futures):
                product_data = future.result()
                if product_data:
                    products_data.append(product_data)
        
        # Simpan data ke file JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(products_data, f, ensure_ascii=False, indent=2)
        
        debug_print(f"Scraping selesai. Data disimpan ke {output_file}")
    
    def close(self):
        """Menutup driver browser"""
        if hasattr(self, "driver"):
            self.driver.quit()

    def _load_more_products(self, existing_links, max_products):
        """Memuat lebih banyak produk dengan mengklik tombol 'Muat Lebih Banyak'"""
        product_links = existing_links.copy()
        attempts = 0
        max_attempts = 100  # Meningkatkan jumlah percobaan maksimum
        consecutive_failures = 0
        max_consecutive_failures = 3  # Berhenti setelah 3 kali gagal berturut-turut
        
        while len(product_links) < max_products and attempts < max_attempts and consecutive_failures < max_consecutive_failures:
            attempts += 1
            debug_print(f"Mencoba memuat lebih banyak produk (percobaan {attempts}/{max_attempts})...")
            
            # Scroll ke bagian bawah halaman untuk memastikan tombol terlihat
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Coba temukan tombol dengan data-testid yang sesuai
            try:
                # Selector yang terbukti berhasil dari debugging
                load_more_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='categoriesLoadMore']")
                if load_more_button.is_displayed() and load_more_button.is_enabled():
                    debug_print("Menemukan tombol 'Muat Lebih Banyak' dengan data-testid='categoriesLoadMore'")
                    debug_print(f"Teks tombol: '{load_more_button.text}'")
                    
                    # Klik tombol menggunakan JavaScript
                    self.driver.execute_script("arguments[0].click();", load_more_button)
                    debug_print("Tombol berhasil diklik, menunggu konten baru dimuat...")
                    time.sleep(3)  # Tunggu konten baru dimuat
                    consecutive_failures = 0  # Reset counter kegagalan berturut-turut
                else:
                    debug_print("Tombol ditemukan tetapi tidak terlihat atau tidak aktif")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        debug_print(f"Tombol tidak aktif selama {consecutive_failures} kali berturut-turut. Berhenti mencoba.")
                        break
            except NoSuchElementException:
                debug_print("Tidak dapat menemukan tombol dengan data-testid='categoriesLoadMore'")
                
                # Coba dengan XPath berdasarkan teks
                try:
                    xpath_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Muat Lebih Banyak')]")
                    if xpath_button.is_displayed() and xpath_button.is_enabled():
                        debug_print("Menemukan tombol dengan XPath: //button[contains(text(), 'Muat Lebih Banyak')]")
                        self.driver.execute_script("arguments[0].click();", xpath_button)
                        time.sleep(3)  # Tunggu konten baru dimuat
                        consecutive_failures = 0  # Reset counter kegagalan berturut-turut
                    else:
                        consecutive_failures += 1
                except NoSuchElementException:
                    debug_print("Tidak dapat menemukan tombol dengan teks 'Muat Lebih Banyak'")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        debug_print(f"Gagal menemukan tombol selama {consecutive_failures} kali berturut-turut. Berhenti mencoba.")
                        # Simpan HTML halaman untuk debugging
                        with open(f"debug_load_more_attempt_{attempts}.html", "w", encoding="utf-8") as f:
                            f.write(self.driver.page_source)
                        debug_print(f"HTML halaman disimpan ke debug_load_more_attempt_{attempts}.html untuk debugging")
                        break
                except Exception as e:
                    debug_print(f"Error saat mencoba mengklik tombol: {str(e)}")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        debug_print(f"Error berturut-turut sebanyak {consecutive_failures} kali. Berhenti mencoba.")
                        break
            except Exception as e:
                debug_print(f"Error saat mencoba mengklik tombol: {str(e)}")
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    debug_print(f"Error berturut-turut sebanyak {consecutive_failures} kali. Berhenti mencoba.")
                    break
            
            # Ambil link produk baru
            try:
                new_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/products/']")
                
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
                                debug_print(f"Produk ditemukan: {len(product_links)}/{max_products}")
                            
                            if len(product_links) >= max_products:
                                debug_print(f"Berhasil mengumpulkan {max_products} produk sesuai target.")
                                debug_print(f"Total link produk yang dikumpulkan: {len(product_links)}")
                                break
                    except Exception:
                        continue
                
                if new_links_added == 0:
                    debug_print("Tidak ada link produk baru yang ditemukan setelah mengklik tombol")
                    consecutive_failures += 1
                    if consecutive_failures >= max_consecutive_failures:
                        debug_print(f"Tidak ada produk baru selama {consecutive_failures} kali berturut-turut. Kemungkinan sudah tidak ada produk lagi.")
                        break
                else:
                    debug_print(f"Berhasil menambahkan {new_links_added} produk baru (total: {len(product_links)})")
                    consecutive_failures = 0  # Reset counter kegagalan berturut-turut
            except Exception as e:
                debug_print(f"Error saat mengambil produk baru: {str(e)}")
                consecutive_failures += 1
        
        if attempts >= max_attempts:
            debug_print(f"Mencapai batas maksimum percobaan ({max_attempts}). Berhenti mencoba.")
        elif consecutive_failures >= max_consecutive_failures:
            debug_print(f"Mencapai batas kegagalan berturut-turut ({max_consecutive_failures}). Kemungkinan sudah tidak ada produk lagi.")
        
        return product_links

if __name__ == "__main__":
    scraper = GramediaScraper(headless=True)
    try:
        # Jumlah produk yang akan di-scrape (bisa diubah)
        num_products = 10
        # Jalankan scraping dengan ekstraksi 10 produk secara paralel
        scraper.scrape_products(max_products=num_products, concurrent_extractions=10)
    finally:
        scraper.close() 