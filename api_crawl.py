import requests
import os
import time

from etherscan import Etherscan
from dotenv import load_dotenv

from db import store_details_in_db, get_addresses_without_details

load_dotenv()

def wait():
    time.sleep(0.4)

def get_api_wrapper() -> Etherscan:
    eth = Etherscan(
        api_key=os.getenv("ETHERSCAN_API_KEY"),
        net="MAIN"
    )
    return eth

def fetch_details(address: str) -> dict:
    print(f"Fetching details for {address}")
    api = get_api_wrapper()
    contract_info = api.get_contract_source_code(address=address)[0]
    wait()
    print(f"Fetching initial transaction for {address}")
    all_txs = []
    try:
        normal_txs = api.get_normal_txs_by_address(address=address, startblock=0, endblock=999999999, sort="asc")
    except:
        normal_txs = None
    if normal_txs:
        all_txs.append(normal_txs[0])
    wait()
    try:
        internal_txs = api.get_internal_txs_by_address(address=address, startblock=0, endblock=999999999, sort="asc")
    except:
        internal_txs = None
    if internal_txs:
        all_txs.append(internal_txs[0])
    wait()
    if all_txs:
        for tx in all_txs:
            if tx['to'] == '':
                init_tx = tx
                break
    else:
        init_tx = None
        print(f"ERROR: Could not find initial transaction for {address}")
    contract_info.update({
        "InitialTransaction": init_tx
    })
    return contract_info

def crawl_and_save():
    addresses = get_addresses_without_details()
    for address in addresses:
        details = fetch_details(address=address.contract_address)
        store_details_in_db(contract_address=address.contract_address, details=details)
    

if __name__ == "__main__":
    crawl_and_save()

