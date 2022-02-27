import json
from web3 import Web3
import asyncio
import dotenv

# Accesses the Infura ETH websocket node
conf = dotenv.dotenv_values(".env")
provider = Web3.WebsocketProvider(conf["INFURA_WS_ENDPOINT"])
web3 = Web3(provider)

# Uniswap addresses
uniswap_router = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
uniswap_factory = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
uniswap_swaps = '0x7885e359a085372EbCF1ed6829402f149D02c600'
uniswap_eth_usdc_pool = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'

# Uniswap ABIs
uniswap_router_abi = json.load(open("uniswap_router_abi.json"))
uniswap_factory_abi = json.load(open("uniswap_factory_abi.json"))
uniswap_swaps_abi = json.load(open("uniswap_swaps_abi.json"))
uniswap_pool_abi = json.load(open("uniswap_pool_abi.json"))

# Creating Contract objects for all the different smart contracts data will be pulled from
factory_contract = web3.eth.contract(address=uniswap_factory, abi=uniswap_factory_abi)
router_contract = web3.eth.contract(address=uniswap_router, abi=uniswap_router_abi)
swaps_contract = web3.eth.contract(address=uniswap_swaps, abi=uniswap_swaps_abi)
eth_usdc_pool_contract = web3.eth.contract(address=uniswap_eth_usdc_pool, abi=uniswap_pool_abi)

# What to do when an event is triggered, currently just prints raw to console
def handle_event(event):
    print(Web3.toJSON(event))

# Async loop process new events
async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)


# Main function creates event listeners for all the different smart contracts and desired event, and sets up the async loop
def main():

    # From the factory, we want to know when a new pool is created
    factory_event_filter = factory_contract.events.PairCreated.createFilter(fromBlock='latest')
    # From the pools themselves, we want to know when a new swap occurs
    eth_usdc_swap_event_filter = eth_usdc_pool_contract.events.Swap.createFilter(fromBlock='latest')

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(factory_event_filter, 0.1),
                log_loop(eth_usdc_swap_event_filter, 0.1)
            )
        )
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting by user request.\n")