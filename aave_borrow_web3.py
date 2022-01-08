from web3 import Web3
from abis import (
    lending_pool_addresses_provider_abi,
    lending_pool_abi,
    erc20_abi,
    price_feed_abi,
)
from pyaml_env import parse_config
import os
import time
from dotenv import load_dotenv
from web3.gas_strategies.time_based import medium_gas_price_strategy

load_dotenv()

config = parse_config("./config.yaml")
network = config["networks"]["active"]
my_address = Web3.toChecksumAddress(os.getenv("MY_ADDRESS"))


def main():
    w3 = Web3(Web3.HTTPProvider(config["networks"][network]["rpc_url"]))
    w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
    amount = w3.toWei(0.1, "ether")
    lending_pool = get_lending_pool(w3)
    nonce_one = w3.eth.getTransactionCount(my_address)
    nonce_two = nonce_one + 1
    nonce_three = nonce_two + 1
    nonce_four = nonce_three + 1
    weth_token_address = Web3.toChecksumAddress(
        config["networks"][network]["weth_token"]
    )
    approve_erc20(w3, weth_token_address, lending_pool.address,
                  amount, nonce=nonce_one)
    tx_hash = deposit_to_aave(w3, amount, lending_pool, nonce=nonce_two)
    print(f"Here is the deposit transaction hex! {tx_hash.hex()}")
    borrowable_eth, total_debt_eth = get_borrowable_data(
        lending_pool, my_address)
    print(f"LETS BORROW IT ALL")
    erc20_eth_price = get_asset_price(w3)
    amount_erc20_to_borrow = (1 / erc20_eth_price) * (borrowable_eth * 0.95)
    print(f"We are going to borrow {amount_erc20_to_borrow} LINK")
    aave_link_token_address = Web3.toChecksumAddress(
        config["networks"][network]["aave_link_token"]
    )
    borrow_tx = borrow_erc20(
        w3,
        lending_pool,
        amount_erc20_to_borrow,
        erc20_address=aave_link_token_address,
        nonce=nonce_three,
    )
    print(f"Here is the borrow transaction hex! {borrow_tx.hex()}")
    borrowable_eth, total_debt_eth = get_borrowable_data(
        lending_pool, my_address)
    print("Time to repay!")
    amount_to_repay = (1 / erc20_eth_price) * (total_debt_eth * 0.95)
    repay_tx = repay_all(
        w3,
        amount_erc20_to_borrow,
        lending_pool,
        erc20_address=aave_link_token_address,
        nonce=nonce_four,
    )
    print(f"Here is the repay transaction hex! {repay_tx.hex()}")


def borrow_erc20(w3, lending_pool, amount, erc20_address=None, nonce=None):
    # 1 is stable interest rate
    # 0 is the referral code
    nonce = nonce if nonce else w3.eth.getTransactionCount(my_address)
    function_call = lending_pool.functions.borrow(
        erc20_address, Web3.toWei(amount, "ether"), 1, 0, my_address
    )
    transaction = function_call.buildTransaction(
        {
            "chainId": config["networks"][network]["chain_id"],
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=os.getenv("PRIVATE_KEY")
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Congratulations! We have just borrowed {amount}")
    return tx_hash


def get_asset_price(w3):
    link_eth_address = Web3.toChecksumAddress(
        config["networks"][network]["link_eth_price_feed"]
    )
    link_eth_price_feed = w3.eth.contract(
        address=link_eth_address, abi=price_feed_abi)
    latest_price = Web3.fromWei(
        link_eth_price_feed.functions.latestRoundData().call()[1], "ether"
    )
    print(f"The LINK/ETH price is {latest_price}")
    return float(latest_price)


def get_borrowable_data(lending_pool, my_address):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        tlv,
        health_factor,
    ) = lending_pool.functions.getUserAccountData(my_address).call()
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_lending_pool(w3):
    lending_pool_addresses_provider_address = Web3.toChecksumAddress(
        config["networks"][network]["lending_pool_addresses_provider"]
    )
    lending_poll_addresses_provider = w3.eth.contract(
        address=lending_pool_addresses_provider_address,
        abi=lending_pool_addresses_provider_abi,
    )
    lending_pool_address = (
        lending_poll_addresses_provider.functions.getLendingPool().call()
    )
    lending_pool = w3.eth.contract(
        address=lending_pool_address, abi=lending_pool_abi)
    return lending_pool


def deposit_to_aave(w3, amount, lending_pool, nonce=None):
    print("Depositing to Aave...")
    time.sleep(5)
    nonce = nonce if nonce else w3.eth.getTransactionCount(my_address)
    weth_address = Web3.toChecksumAddress(
        config["networks"][network]["weth_token"])
    function_call = lending_pool.functions.deposit(
        weth_address, amount, my_address, 0)
    transaction = function_call.buildTransaction(
        {
            "chainId": config["networks"][network]["chain_id"],
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=os.getenv("PRIVATE_KEY")
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Deposited!")
    return tx_hash


def approve_erc20(w3, erc20_address, spender, amount, nonce=None):
    print("Approving ERC20...")
    nonce = nonce if nonce else w3.eth.getTransactionCount(my_address)
    erc20 = w3.eth.contract(address=erc20_address, abi=erc20_abi)
    function_call = erc20.functions.approve(spender, amount)
    nonce = w3.eth.getTransactionCount(my_address)
    transaction = function_call.buildTransaction(
        {
            "chainId": config["networks"][network]["chain_id"],
            "from": my_address,
            "nonce": nonce,
        }
    )
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=os.getenv("PRIVATE_KEY")
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Approved {amount} tokens for contract {spender}")


def repay_all(w3, amount_to_repay, lending_pool, erc20_address=None, nonce=None):
    print("Time to repay...")
    nonce = nonce if nonce else w3.eth.getTransactionCount(my_address)
    approve_erc20(w3, erc20_address, lending_pool.address, w3.toWei(
        amount_to_repay, 'ether'), nonce=nonce)
    function_call = lending_pool.functions.repay(
        erc20_address,
        Web3.toWei(amount_to_repay, "ether"),
        # the ratemode
        1,
        my_address,
    )
    transaction = function_call.buildTransaction(
        {
            "chainId": config["networks"][network]["chain_id"],
            "from": my_address,
            "nonce": nonce + 1,
        }
    )
    print("Repaying...")
    signed_txn = w3.eth.account.sign_transaction(
        transaction, private_key=os.getenv("PRIVATE_KEY")
    )
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Repaid!")
    return tx_hash


if __name__ == "__main__":
    main()
