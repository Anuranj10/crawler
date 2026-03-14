import requests

def download_page(url):
    """
    Download the HTML content of the given URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Only process successfully downloaded pages
        if response.status_code == 200:
            return response.text
        else:
            print(f"[!] Failed to download {url}. Status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"[!] Timeout downloading {url}")
    except Exception as e:
        print(f"[!] Error downloading {url}: {e}")
        
    return None
