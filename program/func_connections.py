from decouple import config
from dydx_v4_client import MAX_CLIENT_ID, NodeClient, Order, OrderFlags, Wallet
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient
from dydx_v4_client.network import TESTNET, Network
from dydx_v4_client.node.market import Market
from dydx_v4_client.network import make_mainnet
from constants import INDEXER_ACCOUNT_ENDPOINT, INDEXER_ENDPOINT_MAINNET, MNEMONIC, DYDX_ADDRESS
from func_public import get_candles_recent

# Connect to DYDX
# Indexer Account = connection we will use to query our testnet trades
# Indexer = connection we will use to get live mainnet data
# node = private connection we will use to send orders etc to the testnet
async def connect_dydx():
  indexer = IndexerClient(host=INDEXER_ENDPOINT_MAINNET, api_timeout=5)
  indexer_account = IndexerClient(host=INDEXER_ACCOUNT_ENDPOINT, api_timeout=5)
  node = await NodeClient.connect(TESTNET.node)
  wallet = await Wallet.from_mnemonic(node, MNEMONIC, DYDX_ADDRESS)
  await check_juristiction(indexer, "BTC-USD")
  return (indexer, indexer_account, node, wallet)

# Check Juristiction
# DYDX no longer allows trading in certain countries and blocks API access too
# This function serves as a check
async def check_juristiction(indexer, market):

  print("Checking Juristiction...")

  try:
    await get_candles_recent(indexer, market)
    print(" ")
    print("--------------------------------------------------------------------------------")
    print("SUCCESS: CONNECTION WORKING")
    print("--------------------------------------------------------------------------------")
    print(" ")
  except Exception as e:
    print(e)
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
