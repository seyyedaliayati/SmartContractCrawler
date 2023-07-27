import requests
import re

from bs4 import BeautifulSoup

from db import store_addresses_in_db

def get_urls():
    url = "https://etherscan.io/contractsVerified/{page_number}?ps=100"
    return [url.format(page_number=page_number) for page_number in range(1, 6)]

def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    r = requests.get(url, headers=headers)
    print(f"Status code: {r.status_code}")
    return r.text

def is_valid_address(address):
    # Check if the address is a hexadecimal string of 40 characters (excluding "0x" prefix)
    if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
        return False
    return True

def get_contract_addresses(html):
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [link['href'] for link in soup.find_all('a', href=True) if link['href'].startswith('/address/0x')]
    addresses = set()
    for href in hrefs:
        address = href.split('/')[2].strip()
        if address.endswith('#code'):
            address = address[:-5]
        else:
            continue
        address = address.lower()
        assert is_valid_address(address), f'Address {address} is not valid'
        addresses.add(address)
    return addresses


def crawl_and_save():
    print('Starting...')
    urls = get_urls()
    addresses = []
    for url in urls:
        print(f"Getting contracts from {url}")
        content = get_html(url)
        ads = get_contract_addresses(content)
        addresses.extend(ads)
    print(f"Found {len(addresses)} addresses")
    store_addresses_in_db(addresses)
    return True


if __name__ == '__main__':
    crawl_and_save()
