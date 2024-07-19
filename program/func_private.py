from dydx_v4_client import MAX_CLIENT_ID, Order, OrderFlags, Wallet
from dydx_v4_client.node.market import Market
from constants import DYDX_ADDRESS, MNEMONIC
from datetime import datetime, timedelta
from func_utils import format_number
import random
import time
import json

from pprint import pprint

# Get existing open positions
async def is_open_positions(indexer, market):

  # Protect API
  time.sleep(0.2)

  # Get positions
  response = await indexer.account.get_subaccount(DYDX_ADDRESS, 0)
  open_positions = response["subaccount"]["openPerpetualPositions"]

  # Determine if open
  if len(open_positions) > 0:
    for token in open_positions.keys():
      if token == market:
        return True
  
  # Return False
  return False


# Check order status
def check_order_status(node, order_id):
  order = node.private.get_order_by_id(order_id)
  if order.data:
    if "order" in order.data.keys():
      return order.data["order"]["status"]
  return "FAILED"


# Place market order
async def place_market_order(wallet, node, indexer, market, side, size, price, reduce_only):

  # Initialize
  current_block = await node.latest_block_height()
  market = Market((await indexer.markets.get_perpetual_markets(market))["markets"][market])
  order_id = market.order_id(DYDX_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
  good_til_block = current_block + 1 + 10

  # Place Market Order
  print("Placing order...")
  place = await node.place_order(
    wallet,
    market.order(
      order_id,
      side = Order.Side.SIDE_BUY if side == "BUY" else Order.Side.SIDE_SELL,
      size = size,
      price = price,
      time_in_force = Order.TIME_IN_FORCE_UNSPECIFIED,
      reduce_only = reduce_only,
      good_til_block = good_til_block
    ),
  )

  # Return result
  return place


# Get Open Orders
async def cancel_all_orders(wallet, node, indexer_account):
  orders = await indexer_account.account.get_subaccount_orders(DYDX_ADDRESS, 0, status = "OPEN")
  if len(orders) > 0:
    for order in orders:
      # cancel = await node.cancel_order(wallet, order["id"]) # Not yet working: Pending fix from DYDX on library
      print(f"You have an open {order['side']} order for {order['ticker']}. Please cancel via the DYDX trading dashboard before launching bot")
    exit(1)


# Abort all open positions
async def abort_all_positions(wallet, node, indexer_account, indexer):
  
  # Cancel all orders
  await cancel_all_orders(wallet, node, indexer_account)

  # Protect API
  time.sleep(0.5)

  # Get markets for reference of tick size
  markets = indexer.get_markets().data

  # Protect API
  time.sleep(0.5)

  # Get all open positions
  positions = get_open_positions(indexer_account)

  # Handle open positions
  close_orders = []
  if len(positions) > 0:

    # Loop through each position
    for pos in positions:

      # Determine Market
      market = pos["market"]

      # Determine Side
      side = "BUY"
      if pos["side"] == "LONG":
        side = "SELL"

      # Get Price
      price = float(pos["entryPrice"])
      accept_price = price * 1.7 if side == "BUY" else price * 0.3
      tick_size = markets["markets"][market]["tickSize"]
      accept_price = format_number(accept_price, tick_size)

      # Place order to close
      order = place_market_order(
        node,
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


# Get Open Positions
async def get_open_positions(indexer):
  response = await indexer.account.get_subaccount(DYDX_ADDRESS, 0)
  return response["subaccount"]["openPerpetualPositions"]
