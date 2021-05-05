from web3 import Web3
from abis import weth_abi
from pyaml_env import parse_config
from dotenv import load_dotenv
import os

load_dotenv()

config = parse_config("./config.yaml")
network = config["networks"]["active"]
my_address = Web3.toChecksumAddress(os.getenv("MY_ADDRESS"))
AMOUNT = 1000000000000000000  # 1 WETH/ETH


def main():
    """
    Runs the get_weth function to get WETH
    """
    get_weth()


def get_weth():
    """
    Mints WETH by depositing ETH.
    """
    print("Getting WETH!")
    w3 = Web3(Web3.HTTPProvider(config["networks"][network]["rpc_url"]))
    nonce = w3.eth.getTransactionCount(my_address)
    weth_address = Web3.toChecksumAddress(config["networks"][network]["weth_token"])
    weth = w3.eth.contract(address=weth_address, abi=weth_abi)
    function_call = weth.functions.deposit()
    transaction = function_call.buildTransaction(
        {
            "chainId": config["networks"][network]["chain_id"],
            "from": my_address,
            "nonce": nonce,
            "value": AMOUNT,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=os.getenv("PRIVATE_KEY")
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Here is the tx hash: {tx_hash.hex()}")
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Received 1 WETH")
    return tx_hash


if __name__ == "__main__":
    main()
