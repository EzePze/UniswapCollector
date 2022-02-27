import websockets
import asyncio
import dotenv
import json
import web3
from web3 import Web3
from hexbytes import HexBytes

uniswap_v3_abi = json.load(open("uniswap_v3_abi.json"))
uniswap_v3_address = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

def deserialize_block_dict(block, level=0):
    block = block.__dict__
    for key, value in block.items():
        if isinstance(value, dict):
            deserialize_block_dict(value, level+1)
        elif isinstance(value, list):
            [deserialize_block_dict(item, level+1) for item in value]
        elif isinstance(value, str):
            print("\t" * level + key + ': ' + value)
        elif isinstance(value, HexBytes):
            print("\t" * level + key + ': ' + value.hex())

def main():
    conf = dotenv.dotenv_values(".env")
    provider = Web3.WebsocketProvider(conf["INFURA_WS_ENDPOINT"])
    web3 = Web3(provider)
    block = web3.eth.getBlock("latest")
    uniswap_contract = web3.eth.contract(address=Web3.toChecksumAddress(uniswap_v3_address), abi=uniswap_v3_abi)
    print("--------- LATEST BLOCK INFO ---------")
    deserialize_block_dict(block)
    print("-------------------------------------\n")
    print("--------- UNISWAP V3 CONTRACT INFO ---------\n")
    print(f"Contract address: {uniswap_contract.address}")
    #print(f"Contract name: {uniswap_contract.functions.name.call()}")
    #print(f"Total supply: {uniswap_contract.functions.totalSupply().call()}")
    print(f"Total ETH balance: {web3.eth.get_balance(uniswap_contract.address)}")
    print("-------------------------------------\n")

async def main_prime():
    conf = dotenv.dotenv_values(".env")
    async with websockets.connect(conf["INFURA_WS_ENDPOINT"]) as ws:
        await ws.send(json.dumps({"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}))
        while True:
            print(await ws.recv())

if __name__ == "__main__":
    main()
