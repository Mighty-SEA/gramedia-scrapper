# Gramedia Scraper

Script Python untuk mengumpulkan data produk buku dari situs Gramedia.com.

## Fitur

- Mengumpulkan link produk dari halaman kategori buku
- Mengekstrak detail produk seperti nama, deskripsi, penerbit, ISBN, dll
- Menyimpan data dalam format JSON

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

3. Periksa file `gramedia_page.html` yang dibuat jika scraper tidak dapat menemukan produk.

4. Pastikan koneksi internet Anda stabil.

## Format Data Output

Data akan disimpan dalam format JSON dengan struktur sebagai berikut:

```json
[
  {
    "url": "https://www.gramedia.com/products/contoh-buku",
    "nama_produk": "Judul Buku",
    "deskripsi": "Deskripsi buku...",
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