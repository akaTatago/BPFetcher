from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import random

def get_soup(url):
    try:
        time.sleep(random.uniform(2, 4))
        response = requests.get(url, impersonate="chrome", timeout=15)
        return BeautifulSoup(response.text, "lxml"), response.url
    except Exception as e:
        print(f"Connection error ({url}): {e}")
        return None, None

def clean_text(element):
    if element:
        return element.get_text(separator=" ", strip=True)
    return None

def normalize(text):
    if text:
        return text.replace(':', '').strip().lower()

def clean_price(element_or_text):
    if not element_or_text:
        return 0.0
    
    text = element_or_text if isinstance(element_or_text, str) else element_or_text.text
    
    clean = text.replace("€", "").replace(",", ".").strip()
    try:
        return float(clean)
    except ValueError:
        return 0.0