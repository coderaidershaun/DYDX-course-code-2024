from decouple import config
from dydx_v4_client import MAX_CLIENT_ID, NodeClient, Order, OrderFlags, Wallet
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import TESTNET, Network
from dydx_v4_client.node.market import Market
from dydx_v4_client.network import make_mainnet
from func_public import get_candles_recent

# Connect to DYDX
# Indexer = public connection we will use to get live mainnet data
# node = private connection we will use to send orders etc to the testnet
async def connect_dydx():
  client_public = IndexerClient(host="https://indexer.dydx.trade", api_timeout=5)
  client_public_testnet = IndexerClient(TESTNET.rest_indexer)
  client_private_testnet = await NodeClient.connect(TESTNET.node)
  await check_juristiction(client_public, "BTC-USD")
  return (client_public, client_public_testnet, client_private_testnet)

# Check Juristiction
# DYDX no longer allows trading in certain countries and blocks API access too
# This function serves as a check
async def check_juristiction(client_public, market):

  print("Checking Juristiction...")

  try:
    response = await get_candles_recent(client_public, market)
    print(" ")
    print("--------------------------------------------------------------------------------")
    print("SUCCESS: CONNECTION WORKING")
    print("--------------------------------------------------------------------------------")
    print(" ")
  except Exception as e:
    if "403" in str(e):
      print(" ")
      print("--------------------------------------------------------------------------------")
      print("FAILED: LOCATION ACCESS LIKELY PROHIBTIED")
      print("--------------------------------------------------------------------------------")
      print(" ")
      print("DYDX likely prohibits use from your county")
      print("Theoretically for learning purposes, you could use a VPN to get around this")
      print("However we cannot advise you to do this")
      print(" ")
    exit(1)

  if "403 Forbidden" in response:
    print("DYDX likely prohibits use from your county")
    print("Theoretically for learning purposes, you could use a VPN to get around this")
    print("However we cannot advise you to do this")
    exit(1)


################################################## OLD CODE ############################################################


# from dydx3 import Client
# from web3 import Web3
# from constants import (
#   HOST,
#   ETHEREUM_ADDRESS,
#   DYDX_API_KEY,
#   DYDX_API_SECRET,
#   DYDX_API_PASSPHRASE,
#   STARK_PRIVATE_KEY,
#   HTTP_PROVIDER,
# )

# # Connect to DYDX
# def connect_dydx():

#   # Create Client Connection
#   client = Client(
#       host=HOST,
#       api_key_credentials={
#           "key": DYDX_API_KEY,
#           "secret": DYDX_API_SECRET,
#           "passphrase": DYDX_API_PASSPHRASE,
#       },
#       stark_private_key=STARK_PRIVATE_KEY,
#       eth_private_key=config("ETH_PRIVATE_KEY"),
#       default_ethereum_address=ETHEREUM_ADDRESS,
#       web3=Web3(Web3.HTTPProvider(HTTP_PROVIDER))
#   )

#   # Confirm client
#   account = client.private.get_account()
#   account_id = account.data["account"]["id"]
#   quote_balance = account.data["account"]["quoteBalance"]
#   print("Connection Successful")
#   print("Account ID: ", account_id)
#   print("Quote Balance: ", quote_balance)

#   # Return Client
#   return client
