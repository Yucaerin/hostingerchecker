import requests
import threading
import queue
import os

input_file = "mikir.txt"

output_hostinger = "result_hostinger.txt"
output_litespeed = "result_litespeed.txt"
output_all = "result_all.txt"

domain_queue = queue.Queue()

def prepare_url(domain):
    return [f"http://{domain}", f"https://{domain}"]

def check_headers_and_cookies(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        headers = response.headers
        cookies = headers.get("set-cookie", "")

        xsrf_token = any("xsrf-token" in cookie.lower() for cookie in cookies.split(","))

        hostinger_platform = "hostinger" in headers.get("platform", "").lower()

        litespeed_server = "litespeed" in headers.get("server", "").lower()

        print(f"[CHECKED] {url} - XSRF-TOKEN: {xsrf_token}, Hostinger: {hostinger_platform}, LiteSpeed: {litespeed_server}")

        if xsrf_token and hostinger_platform and litespeed_server:
            save_to_file(output_all, url)
        elif xsrf_token and hostinger_platform and not litespeed_server:
            save_to_file(output_hostinger, url)
        elif xsrf_token and litespeed_server and not hostinger_platform:
            save_to_file(output_litespeed, url)

    except requests.RequestException:
        print(f"[CHECKED] {url} - ERROR (Request Failed)")

def save_to_file(filename, url):
    with open(filename, "a") as file:
        file.write(url + "\n")
    os.fsync(file.fileno()) 
    print(f"[SAVED] {url} -> {filename}")

def worker():
    while not domain_queue.empty():
        domain = domain_queue.get()
        for prepared_url in prepare_url(domain):
            check_headers_and_cookies(prepared_url)
        domain_queue.task_done()

def main():
    with open(input_file, "r") as file:
        for line in file:
            domain = line.strip()
            if domain:  
                domain_queue.put(domain)

    threads = []
    num_threads = 5 
    for _ in range(num_threads):
        thread = threading.Thread(target=worker)
        thread.daemon = True 
        thread.start()
        threads.append(thread)

    domain_queue.join()

    print("\nProses selesai. Hasil telah disimpan.")

if __name__ == "__main__":
    main()
