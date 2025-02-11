import subprocess
import threading
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

result_queue = queue.Queue()

def check_xsrf_token(url):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname if parsed_url.hostname else url

        result = subprocess.run(['curl', '-I', f'http://{host}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0 and "XSRF-TOKEN" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"An error occurred while checking XSRF-TOKEN for {url}: {str(e)}")
        return False

def check_hostinger(url):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname if parsed_url.hostname else url

        result = subprocess.run(['curl', '-I', f'http://{host}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0 and "Hostinger" in result.stdout:
            print(f"Hostinger platform found: {url}")
            return url
        else:
            print(f"Not Hostinger: {url}")
            return None
    except Exception as e:
        print(f"An error occurred for {url}: {str(e)}")
        return None

def process_website(url):
    if check_xsrf_token(url):
        result = check_hostinger(url)
        if result:
            result_queue.put(result) 
    else:
        print(f"Skipping {url}: XSRF-TOKEN not found")

def save_results(result_file):
    with open(result_file, "a") as file:
        while True:
            try:
                result = result_queue.get(timeout=5)  
                if result is None:  
                    break
                file.write(f"{result}\n")  
                file.flush()  
            except queue.Empty:
                if all(future.done() for future in futures):
                    break

def process_websites(input_file, result_file):
    if os.path.exists(input_file):
        with open(input_file, "r") as file:
            websites = [line.strip() for line in file if line.strip()]

        with ThreadPoolExecutor(max_workers=10) as executor:
            global futures
            futures = [executor.submit(process_website, url) for url in websites]

            writer_thread = threading.Thread(target=save_results, args=(result_file,))
            writer_thread.start()

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error: {e}")

            result_queue.put(None)
            writer_thread.join()  
    else:
        print(f"File {input_file} not found!")

input_file = "websites.txt"  
result_file = "result.txt"

process_websites(input_file, result_file)
