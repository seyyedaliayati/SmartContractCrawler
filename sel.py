
import json, os, time
from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests
import threading
import concurrent.futures


from dotenv import load_dotenv

load_dotenv()

START_BLOCK = None # TODO
API_KEY = os.environ.get("ETHERSCAN_API_KEY")

# connect to redis, redis acts as a queue cache
import redis

redis_db = redis.Redis(
  host='redis-15097.c276.us-east-1-2.ec2.cloud.redislabs.com',
  port=15097,
  password='NDh74FAubAJ9omJYslhw5qjWtyQ0Me04')

def check_contract_verification(w3, address) -> tuple:
    etherscan_url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={API_KEY}"
    response = requests.get(etherscan_url)
    result = response.json()
    if result["status"] == "1":
        return True, json.loads(result["result"])
    else:
        return False, None

def add_to_redis(contract_address, data):
    # check if contract_address is in redis
    if redis_db.get(contract_address):
        return
    # add to redis
    response = redis_db.set(contract_address, json.dumps(data))
    if not response:
        print(f"Failed to add {contract_address} to redis")
    else:
        print(f"Added {contract_address} to redis")
    return response

def remove_from_redis(contract_address):
    # check if contract_address is in redis
    if not redis_db.get(contract_address):
        return
    # remove from redis
    response = redis_db.delete(contract_address)
    if not response:
        print(f"Failed to remove {contract_address} from redis")
    else:
        print(f"Removed {contract_address} from redis")
    return response

def traverse_redis():
    # traverse redis
    while True:
        for key in redis_db.scan_iter():
            contract_address = key.decode("utf-8")
            metadata = json.loads(redis_db.get(contract_address))
            print(f"Contract address: {contract_address}")
            print(f"Metadata: {metadata}")
            # remove_from_redis(contract_address)
        print("There are no more keys in redis, sleeping for 500 seconds")
        time.sleep(500)

def get_network_name_by_id(network_id):
    name = None
    # TODO: load once!
    with open("chains.json", "r") as f:
        chains = json.load(f)
        for chain in chains:
            if chain["chainId"] == network_id:
                name = chain["name"]
                break
    return name

def process_block(web3, block_number):
    print(f"Processing block {block_number}")
    block = web3.eth.get_block(block_number)

    for tx_hash in block.transactions:
        tx = web3.eth.get_transaction(tx_hash)
        if tx.to is None:
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            contract_address = receipt.get('contractAddress', None)

            if contract_address:
                data = {
                    "network_id": web3.eth.chain_id,
                    "network_name": get_network_name_by_id(web3.eth.chain_id),
                    "block_number": block_number,
                    "block_timestamp": block.timestamp,
                    "tx_hash": tx_hash.hex(),
                }
                add_to_redis(contract_address, data)

def fetch_addresses(web3: Web3):
    """
    redis: 
    block_number, block_hash, block_timestamp, tx_hash, address, is_processed
    """
    network_id = web3.eth.chain_id
    network_name = get_network_name_by_id(network_id)
    blocks = (18589667, 18613607)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Process blocks in parallel using threads
        futures = [executor.submit(process_block, web3, block_number) for block_number in range(*blocks)]

        # Wait for all threads to complete
        concurrent.futures.wait(futures)

def main():
    w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    # run fetch_addresses in a thread
    fetch_addresses(w3)
    exit(0)
    # Replace the starting block and ending block according to your requirements
    start_block = 0
    end_block = w3.eth.block_number

    for block_number in range(18589667,0, -1):
        block = w3.eth.get_block(block_number)

        for tx_hash in block.transactions:
            tx = w3.eth.get_transaction(tx_hash)

            # Check if the transaction is a contract creation
            if tx.to is None:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                address = receipt.get('contractAddress', None)

                if address:
                    print(f"Contract created at address: {address}")

                    # Check if the contract is verified and open source
                    is_verified, abi = check_contract_verification(w3, address)
                    print(f"Contract ABI: {type(abi)}")
                    if is_verified:
                        print("Contract is verified and open source.")
                    else:
                        print("Contract is not verified or not open source.")
                        
                    print("\n")

if __name__ == "__main__":
    main()
