import asyncio
from constants import DYDX_ADDRESS
from dydx_v4_client.indexer.rest.indexer_client import IndexerClient

from dydx_v4_client.network import TESTNET, Network, mainnet_node

client = IndexerClient(TESTNET.rest_indexer)

async def test():
  print(DYDX_ADDRESS)
  response = await client.account.get_subaccounts("dydx14zzueazeh0hj67cghhf9jypslcf9sh2n5k6art")

asyncio.run(test())
