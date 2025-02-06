import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import urllib3

# Menonaktifkan peringatan SSL yang tidak diverifikasi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# File input dan output
input_file = "websites.txt"
output_file = "result.txt"

# Fungsi untuk memeriksa apakah sebuah website menggunakan platform Hostinger
def check_hostinger_platform(url):
    try:
        # Menambahkan skema jika tidak ada
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        # Permintaan HTTP GET dengan timeout dan retry
        response = requests.get(url, timeout=10, verify=False)
        headers = response.headers

        # Cek header "Platform" untuk menentukan Hostinger
        if "Platform" in headers and headers["Platform"].lower() == "hostinger":
            return True
        return False

    except requests.RequestException as e:
        print(f"Gagal mengakses {url}. Error: {e}")
        return False

# Fungsi untuk memproses setiap website
def process_website(url, result_lock, results):
    if check_hostinger_platform(url):
        with result_lock:
            results.append(url)
            print(f"{url} menggunakan platform Hostinger")

# Fungsi utama untuk membaca input, memproses, dan menyimpan hasil
def main():
    # Membaca daftar website dari file
    try:
        with open(input_file, "r") as file:
            websites = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"File {input_file} tidak ditemukan.")
        return

    # Inisialisasi threading
    results = []
    result_lock = threading.Lock()

    # Menggunakan ThreadPoolExecutor untuk mengelola thread dengan lebih efisien
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_website, url, result_lock, results) for url in websites]

        # Menunggu semua thread selesai
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error: {e}")

    # Menyimpan hasil ke file
    with open(output_file, "w") as file:
        for url in results:
            file.write(url + "\n")

    print(f"Hasil disimpan ke {output_file}")

if __name__ == "__main__":
    main()
