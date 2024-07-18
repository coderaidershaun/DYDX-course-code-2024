from dydx_v4_client import MAX_CLIENT_ID, NodeClient, Order, OrderFlags, Wallet
from dydx_v4_client.node.market import Market
from constants import DYDX_ADDRESS, MNEMONIC
from datetime import datetime, timedelta
from func_utils import format_number
import random
import time
import json

from pprint import pprint

# Get existing open positions
def is_open_positions(client_private, market):

  # Protect API
  time.sleep(0.2)

  # Get positions
  all_positions = client_private.get_positions(
    market=market,
    status="OPEN"
  )

  # Determine if open
  if len(all_positions.data["positions"]) > 0:
    return True
  else:
    return False


# Check order status
def check_order_status(client, order_id):
  order = client.private.get_order_by_id(order_id)
  if order.data:
    if "order" in order.data.keys():
      return order.data["order"]["status"]
  return "FAILED"


# Place market order
async def place_market_order(client_private, client_public, market, side, size, price, reduce_only):

  # Initialize
  wallet = await Wallet.from_mnemonic(client_private, MNEMONIC, DYDX_ADDRESS)
  current_block = await client_private.latest_block_height()
  market = Market((await client_public.markets.get_perpetual_markets(market))["markets"][market])
  order_id = market.order_id(TEST_ADDRESS, 0, random.randint(0, MAX_CLIENT_ID), OrderFlags.SHORT_TERM)
  good_til_block = current_block + 1 + 10

  # Place Market Order
  print("Placing order...")
  place = await client_private.place_order(
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


# Abort all open positions
def abort_all_positions(client_private, client_public):
  
  # Cancel all orders
  client_private.cancel_all_orders()

  # Protect API
  time.sleep(0.5)

  # Get markets for reference of tick size
  markets = client_public.get_markets().data

  # Protect API
  time.sleep(0.5)

  # Get all open positions
  positions = client_private.get_positions(status="OPEN")
  all_positions = positions.data["positions"]

  # Handle open positions
  close_orders = []
  if len(all_positions) > 0:

    # Loop through each position
    for position in all_positions:

      # Determine Market
      market = position["market"]

      # Determine Side
      side = "BUY"
      if position["side"] == "LONG":
        side = "SELL"

      # Get Price
      price = float(position["entryPrice"])
      accept_price = price * 1.7 if side == "BUY" else price * 0.3
      tick_size = markets["markets"][market]["tickSize"]
      accept_price = format_number(accept_price, tick_size)

      # Place order to close
      order = place_market_order(
        client_private,
        market,
        side,
        position["sumOpen"],
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
async def get_open_positions(client_private):
  response = await client_private.account.get_subaccounts(DYDX_ADDRESS)




################################################## OLD CODE ############################################################

# # Get existing open positions
# def is_open_positions(client, market):

#   # Protect API
#   time.sleep(0.2)

#   # Get positions
#   all_positions = client.private.get_positions(
#     market=market,
#     status="OPEN"
#   )

#   # Determine if open
#   if len(all_positions.data["positions"]) > 0:
#     return True
#   else:
#     return False


# # Check order status
# def check_order_status(client, order_id):
#   order = client.private.get_order_by_id(order_id)
#   if order.data:
#     if "order" in order.data.keys():
#       return order.data["order"]["status"]
#   return "FAILED"


# # Place market order
# def place_market_order(client, market, side, size, price, reduce_only):

#   # Get Position Id
#   account_response = client.private.get_account()
#   position_id = account_response.data["account"]["positionId"]

#   # Get expiration time
#   server_time = client.public.get_time()
#   expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=3700)

#   # Place an order
#   placed_order = client.private.create_order(
#     position_id=position_id, # required for creating the order signature
#     market=market,
#     side=side,
#     order_type="MARKET",
#     post_only=False,
#     size=size,
#     price=price,
#     limit_fee='0.015',
#     expiration_epoch_seconds=expiration.timestamp(),
#     time_in_force="FOK", 
#     reduce_only=reduce_only
#   )

#   # print(placed_order.data)

#   # Return result
#   return placed_order.data


# # Abort all open positions
# def abort_all_positions(client):
  
#   # Cancel all orders
#   client.private.cancel_all_orders()

#   # Protect API
#   time.sleep(0.5)

#   # Get markets for reference of tick size
#   markets = client.public.get_markets().data

#   # Protect API
#   time.sleep(0.5)

#   # Get all open positions
#   positions = client.private.get_positions(status="OPEN")
#   all_positions = positions.data["positions"]

#   # Handle open positions
#   close_orders = []
#   if len(all_positions) > 0:

#     # Loop through each position
#     for position in all_positions:

#       # Determine Market
#       market = position["market"]

#       # Determine Side
#       side = "BUY"
#       if position["side"] == "LONG":
#         side = "SELL"

#       # Get Price
#       price = float(position["entryPrice"])
#       accept_price = price * 1.7 if side == "BUY" else price * 0.3
#       tick_size = markets["markets"][market]["tickSize"]
#       accept_price = format_number(accept_price, tick_size)

#       # Place order to close
#       order = place_market_order(
#         client,
#         market,
#         side,
#         position["sumOpen"],
#         accept_price,
#         True
#       )

#       # Append the result
#       close_orders.append(order)

#       # Protect API
#       time.sleep(0.2)

#     # Override json file with empty list
#     bot_agents = []
#     with open("bot_agents.json", "w") as f:
#       json.dump(bot_agents, f)

#     # Return closed orders
#     return close_orders
