import asyncio
import random
import time
import requests
from constants import DYDX_ADDRESS, INDEXER_ACCOUNT_ENDPOINT, INDEXER_ENDPOINT_MAINNET, SECRET_PHRASE
from dydx_v4_client import MAX_CLIENT_ID, NodeClient, Order, OrderFlags
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import TESTNET, Network, mainnet_node
from dydx_v4_client.node.market import Market, since_now
from dydx_v4_client.wallet import Wallet

MARKET_ID = "ETH-USD"

async def test():
  indexer_account = IndexerClient(host=INDEXER_ACCOUNT_ENDPOINT, api_timeout=5)
  indexer = IndexerClient(host=INDEXER_ENDPOINT_MAINNET, api_timeout=5)
  node = await NodeClient.connect(TESTNET.node)

  # headers = {
  #   'Accept': 'application/json'
  # }

  # r = requests.get(f'https://dydx-testnet.imperator.co/v4/orders/parentSubaccountNumber', params={
  #   'address': DYDX_ADDRESS,  'parentSubaccountNumber': "0.1"
  # }, headers = headers)

  # baseURL = 'https://dydx-testnet.imperator.co/v4'
  # r = requests.get(f'{baseURL}/addresses/{DYDX_ADDRESS}/parentSubaccountNumber/0', headers = headers)


  # market = Market(
  #   (await indexer.markets.get_perpetual_markets(MARKET_ID))["markets"][MARKET_ID]
  # )

  wallet = await Wallet.from_mnemonic(node, SECRET_PHRASE, DYDX_ADDRESS)

  # order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.LONG_TERM)

  # cancel = await node.cancel_order(
  #   wallet,
  #   order_id,
  #   good_til_block_time=since_now(seconds=120)
  # )

  # response = await node.get_account_balances(DYDX_ADDRESS)
  # response = await node.get_account_balance(DYDX_ADDRESS, "adv4tnt")
  # response = await node.get_account(DYDX_ADDRESS)
  # response = await node.latest_block()

  # response = await indexer_account.account.get_subaccounts(DYDX_ADDRESS)
  # response = await indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
  # response = await indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
  # response = await indexer_account.account.get_subaccount_orders(DYDX_ADDRESS, 0, status = "OPEN")

  orders = await indexer_account.account.get_subaccount_orders(DYDX_ADDRESS, 0, status = "OPEN")
  if len(orders) > 0:
    for order in orders:
      # cancel = await node.cancel_order(wallet, order["id"]) # Not yet working: Pending fix from DYDX on library
      print(f"You have an open {order['side']} order for {order['ticker']}")

  # print(cancel)

asyncio.run(test())
