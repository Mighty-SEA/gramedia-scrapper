# Gramedia Scraper

Script Python untuk mengumpulkan data produk buku dari situs Gramedia.com.

## Fitur

- Mengumpulkan link produk dari halaman kategori buku
- Mengekstrak detail produk seperti nama, deskripsi, penerbit, ISBN, dll
- Mengekstrak URL gambar produk
- Menyimpan data dalam format JSON
- Mendukung tombol "Muat Lebih Banyak" untuk mengambil lebih dari 49 produk
- Mode headless dan non-headless
- Kemampuan mengambil produk dalam jumlah besar (ratusan hingga ribuan)
- Ekstraksi paralel untuk memproses hingga 10 produk sekaligus

## Persyaratan

- Python 3.7+
- Chrome browser

## Instalasi

1. Clone repositori ini atau download file-nya
2. Install dependensi yang diperlukan:

```bash
pip install -r requirements.txt
```

## Penggunaan

### Cara Sederhana

Jalankan script dengan perintah:

```bash
python run_scraper.py
```

Secara default, script akan mengumpulkan 10 produk dan menyimpannya ke file `gramedia_products.json`.

### Opsi Command Line

Anda dapat menyesuaikan jumlah produk dan nama file output:

```bash
python run_scraper.py --num-products 50 --output hasil_scraping.json
```

Atau menggunakan format pendek:

```bash
python run_scraper.py -n 50 -o hasil_scraping.json
```

Jika Anda ingin melihat browser saat scraping (mode non-headless):

```bash
python run_scraper.py --no-headless
```

### Parameter yang Tersedia

- `-n, --num-products`: Jumlah produk yang akan di-scrape (default: 10)
- `-o, --output`: Nama file output JSON (default: gramedia_products.json)
- `--no-headless`: Jalankan browser dalam mode visible (tidak headless)
- `-c, --concurrent`: Jumlah ekstraksi produk paralel (default: 10)

## Pemecahan Masalah

Jika scraper tidak berjalan dengan baik, coba langkah-langkah berikut:

1. Jalankan dalam mode non-headless untuk melihat apa yang terjadi:
   ```bash
   python run_scraper.py --no-headless
   ```

2. Jalankan script debug untuk mendapatkan informasi lebih detail:
   ```bash
   python debug_scraper.py
   ```
   Script ini akan membuat folder `debug` yang berisi HTML halaman kategori dan produk untuk analisis.

3. Untuk menguji khusus tombol "Muat Lebih Banyak", gunakan script debug khusus:
   ```bash
   python debug_load_more.py
   ```
   Script ini akan mencoba mengklik tombol dan menyimpan informasi debugging di folder `debug`.

4. Untuk menguji batas maksimal produk yang bisa diambil, gunakan:
   ```bash
   python debug_load_more_limit.py
   ```
   Script ini akan terus mengklik tombol "Muat Lebih Banyak" sampai tombol tidak tersedia lagi.

5. Periksa file `gramedia_page.html` yang dibuat jika scraper tidak dapat menemukan produk.

6. Pastikan koneksi internet Anda stabil.

## Format Data Output

Data akan disimpan dalam format JSON dengan struktur sebagai berikut:

```json
[
  {
    "url": "https://www.gramedia.com/products/contoh-buku",
    "nama_produk": "Judul Buku",
    "deskripsi": "Deskripsi buku...",
    "gambar_url": "https://image.gramedia.net/rs:fit:0:0/plain/https://cdn.gramedia.com/uploads/items/contoh-buku.jpg",
    "detail_produk": {
      "Penerbit": "Nama Penerbit",
      "ISBN": "1234567890123",
      "Bahasa": "Indonesia",
      "Lebar": "15 cm",
      "Tanggal Terbit": "Jan 1, 2025",
      "Halaman": "200",
      "Berat": "0.5 kg"
    }
  },
  // ... produk lainnya
]
```

## Catatan Penting

- Gunakan script ini dengan bijak dan bertanggung jawab
- Berikan jeda waktu yang cukup antara request untuk menghindari pembatasan akses dari server
- Script ini dibuat untuk tujuan pembelajaran dan penggunaan pribadi
- Perhatikan bahwa situs web dapat memiliki batas jumlah produk yang bisa ditampilkan

## Update Terbaru

- **v1.4.0** - Menambahkan fitur ekstraksi paralel
  - Mengimplementasikan ThreadPoolExecutor untuk memproses hingga 10 produk secara bersamaan
  - Menambahkan parameter `--concurrent` untuk mengontrol jumlah ekstraksi paralel
  - Meningkatkan kecepatan ekstraksi data produk secara signifikan
  - Setiap thread menggunakan driver browser terpisah untuk menghindari konflik

- **v1.3.0** - Menambahkan fitur ekstraksi URL gambar produk
  - Mengekstrak URL gambar produk dari halaman detail produk
  - Menambahkan filter untuk memastikan URL gambar yang valid (menghindari URL pelacakan)
  - Menambahkan fallback dengan beberapa metode ekstraksi gambar
  - Mendukung pengambilan screenshot gambar produk jika metode lain gagal

- **v1.2.0** - Peningkatan kemampuan mengambil produk dalam jumlah besar
  - Meningkatkan jumlah maksimum percobaan klik tombol "Muat Lebih Banyak" (dari 10 menjadi 100)
  - Menambahkan deteksi kegagalan berturut-turut untuk menghentikan scraping jika tombol tidak berfungsi
  - Menambahkan penanganan StaleElementReferenceException untuk elemen yang sudah tidak valid
  - Menambahkan script debug baru (`debug_load_more_limit.py`) untuk menguji batas maksimal produk

- **v1.1.0** - Perbaikan dukungan tombol "Muat Lebih Banyak" untuk mengambil lebih dari 49 produk
  - Menambahkan selector yang tepat untuk tombol "Muat Lebih Banyak" (`button[data-testid='categoriesLoadMore']`)
  - Menambahkan mekanisme fallback jika selector utama gagal
  - Menambahkan script debug khusus (`debug_load_more.py`) untuk menguji tombol
  - Meningkatkan logging untuk memudahkan debugging 