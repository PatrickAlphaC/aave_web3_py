<br/>
<p align="center">
<a href="https://chain.link" target="_blank">
<img src="https://raw.githubusercontent.com/PatrickAlphaC/aave_web3_py/main/img/aave.png" width="225" alt="Python + Aave">
<img src="https://raw.githubusercontent.com/PatrickAlphaC/aave_web3_py/main/img/python.png" width="225" alt="Python + Aave">
</a>
</p>
<br/>

# aave_web3_py

Put down collateral, Borrow, and repay a loan from Aave! Use this to short assets and accrue interest. 

[You can see a brownie version of this here. ](https://github.com/PatrickAlphaC/aave_brownie_py)

In our `aave_borrow_web3.py` script, we do the following:

1. Approve our `ETH` to be swapped for `WETH`
2. Swap an `amount` of `ETH` for `WETH`
3. Using `deposit_to_aave` we deposit the `WETH` as collateral
4. We use that collateral to borrow `LINK` with `borrow_erc20`
5. Then, we pay it back! 
6. We can view the txs on etherscan to see what's going on under the hood. 


# Setup

You'll need python installed. 

```
pip install -r requirements.txt
```

You'll need the following [environment variables](https://www.twilio.com/blog/2017/01/how-to-set-environment-variables.html). You can set them all in your `.env` file:
```
export MY_ADDRESS=<YOUR_WALLET_ADDRESS>
export PRIVATE_KEY=<YOUR_PRIVATE_KEY> # Remember to start it with "0x"
export KOVAN_RPC_URL='URL'

# Optional... But can be very helpful
export MAINNET_RPC_URL='URL'
```

- `MY_ADDRESS`: Your Wallet Address
- `PRIVATE_KEY`: Your Private Key from your Wallet
- `KOVAN_RPC_URL`: Your Kovan connection to the blockchain. You can get a URL from a service like [Infura](https://infura.io/) or ][Alchemy](https://www.alchemy.com/). An example would be `https://kovan.infura.io/v3/fffffffffffffffffffff`
- `MAINNET_RPC_URL`: Same as above, but for mainnet. 

And last, be sure to check the aave_link_token if you're using a [testnet LINK token](https://docs.aave.com/developers/deployed-contracts/deployed-contracts0).  Aave sometimes changes the token they use on testnet to keep liquidity. 
Also, feel free to check the [Aave docs](https://docs.aave.com/developers/the-core-protocol/lendingpool) as well, to learn more about the tools we are using. 

# Quickstart - kovan

1. [Get some kovan ETH](https://faucet.kovan.network/)

2. Get some WETH

```
python get_weth.py
```

3. Run the script!

```
python aave_borrow_web3.py
```


# Quickstart - mainnet-fork


Optional for running locally:
If you want to run locally, you can install `ganache-cli` and `yarn`. Here is where you can [install yarn.](https://classic.yarnpkg.com/en/docs/install/#mac-stable)

```
yarn global add ganache-cli
```

Then, you can run `ganache-cli --fork $MAINNET_RPC_URL` and set the `active` network in the `config.yaml` to `mainnet-fork`. 

You'll need to set your private key to a private key from your forked mainnet. 

1. Get some WETH

```
python get_weth.py
```

2. Run the script!

```
python aave_borrow_web3.py
```
