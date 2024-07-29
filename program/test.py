import asyncio
from dydx_v4_client import MAX_CLIENT_ID, Order, OrderFlags
from dydx_v4_client.node.market import Market, since_now
from dydx_v4_client.indexer.rest.constants import OrderType
from constants import DYDX_ADDRESS
from func_utils import format_number
from func_public import get_markets
import random
import time
import json


from func_connections import connect_dydx
from func_private import place_market_order

async def main():
  client = await connect_dydx()
  order = await place_market_order(client, "MATIC-USD", "BUY", 10, 0, False)

asyncio.run(main())
