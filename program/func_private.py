from dydx_v4_client import MAX_CLIENT_ID, Order, OrderFlags
from dydx_v4_client.node.market import Market, since_now
from dydx_v4_client.indexer.rest.constants import OrderType
from constants import DYDX_ADDRESS
from func_utils import format_number
from func_public import get_markets
import random
import time
import json
from datetime import datetime

from pprint import pprint

# Cancel Order
async def cancel_order(client, order_id):
  order = await get_order(client, order_id)
  market = Market((await client.indexer.markets.get_perpetual_markets(order["ticker"]))["markets"][order["ticker"]])
  market_order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
  market_order_id.client_id = int(order["clientId"])
  market_order_id.clob_pair_id = int(order["clobPairId"])
  current_block = await client.node.latest_block_height()
  good_til_block = current_block + 1 + 10
  cancel = await client.node.cancel_order(
    client.wallet,
    market_order_id,
    good_til_block=good_til_block
  )
  print(cancel)
  print(f"Attempted to cancel order for: {order["ticker"]}. Please check dashboard to ensure cancelled.")

# Get Account
async def get_account(client):
  account = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
  return account["subaccount"]


# Get Open Positions
async def get_open_positions(client):
  response = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
  return response["subaccount"]["openPerpetualPositions"]


# Get Existing Order
async def get_order(client, order_id):
  return await client.indexer_account.account.get_order(order_id)


# Get existing open positions
async def is_open_positions(client, market):

  # Protect API
  time.sleep(0.2)

  # Get positions
  response = await client.indexer_account.account.get_subaccount(DYDX_ADDRESS, 0)
  open_positions = response["subaccount"]["openPerpetualPositions"]

  # Determine if open
  if len(open_positions) > 0:
    for token in open_positions.keys():
      if token == market:
        return True
  
  # Return False
  return False


# Check order status
async def check_order_status(client, order_id):
  order = await client.indexer_account.account.get_order(order_id)
  if order["status"]:
    return order["status"]
  return "FAILED"


# Place market order
async def place_market_order(client, market, side, size, price, reduce_only):

  # Initialize
  ticker = market
  current_block = await client.node.latest_block_height()
  market = Market((await client.indexer.markets.get_perpetual_markets(market))["markets"][market])
  market_order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
  good_til_block = current_block + 1 + 10

  # Set Time In Force
  time_in_force = Order.TIME_IN_FORCE_UNSPECIFIED

  # Place Market Order
  order = await client.node.place_order(
    client.wallet,
    market.order(
      market_order_id,
      order_type=OrderType.MARKET,
      side = Order.Side.SIDE_BUY if side == "BUY" else Order.Side.SIDE_SELL,
      size = float(size),
      price = float(price), # Adding price in case you wish to flip order type to LIMIT. Else price can = 0.
      time_in_force = time_in_force,
      reduce_only = reduce_only,
      good_til_block = good_til_block
    ),
  )

  # Get Recent Orders
  # We do this as in the current V4 version at the time of developing this, the order response does not return the order number
  time.sleep(1.5)
  orders = await client.indexer_account.account.get_subaccount_orders(
    DYDX_ADDRESS, 
    0, 
    ticker, 
    return_latest_orders = "true",
  )

  # Get latest order id
  order_id = ""
  for order in orders:
    client_id = int(order["clientId"])
    clob_pair_id = int(order["clobPairId"])
    order["createdAtHeight"] = int(order["createdAtHeight"])
    if client_id == market_order_id.client_id and clob_pair_id == market_order_id.clob_pair_id:
      order_id = order["id"]
      break

  # Ensure latest order
  if order_id == "":
    sorted_orders = sorted(orders, key=lambda x: x["createdAtHeight"], reverse=True)
    pprint("last order:", sorted_orders[0])
    print("Warning: Unable to detect latest order. Please check dashboard")
    exit(1)

  # Print something if error returned
  if "code" in str(order):
    print(order)

  # Return result
  return (order, order_id)

# Get Open Orders
async def cancel_all_orders(client):
  orders = await client.indexer_account.account.get_subaccount_orders(DYDX_ADDRESS, 0, status = "OPEN")
  if len(orders) > 0:
    for order in orders:
      await cancel_order(client, order["id"])
      print("You have open orders. Please check the Dashboard to ensure they are cancelled as testnet order requests appear not to be cancelling")
      exit(1)


# Abort all open positions
async def abort_all_positions(client):
  
  # Cancel all orders
  await cancel_all_orders(client)

  # Protect API
  time.sleep(0.5)

  # Get markets for reference of tick size
  markets = await get_markets(client)

  # Protect API
  time.sleep(0.5)

  # Get all open positions
  positions = await get_open_positions(client)

  # Handle open positions
  close_orders = []
  if len(positions) > 0:

    # Loop through each position
    for item in positions.keys():
      
      # Get Position
      pos = positions[item]

      # Determine Market
      market = pos["market"]

      # Determine Side
      side = "BUY"
      if pos["side"] == "LONG":
        side = "SELL"

      # Get Price
      price = float(pos["entryPrice"])
      accept_price = price * 1.7 if side == "BUY" else price * 0.3 # Helps towards ensuring order will be filled
      tick_size = markets["markets"][market]["tickSize"]
      accept_price = format_number(accept_price, tick_size)

      # Place order to close
      (order, order_id) = await place_market_order(
        client, 
        market,
        side,
        pos["sumOpen"],
        accept_price,
        True
      )

      # Append the result
      close_orders.append(order)

      # Protect API
      time.sleep(0.2)

    # Override json file with empty list
    bot_agents = []
    with open("bot_agents.json", "w") as f:
      json.dump(bot_agents, f)

    # Return closed orders
    return close_orders
