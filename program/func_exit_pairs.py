from constants import CLOSE_AT_ZSCORE_CROSS
from func_utils import format_number
from func_cointegration import calculate_zscore
from func_public import get_candles_recent, get_markets
from func_private import place_market_order, get_open_positions, get_order
import json
import time

from pprint import pprint

# Manage trade exits
async def manage_trade_exits(client):

  """
    Manage exiting open positions
    Based upon criteria set in constants
  """

  # Initialize saving output
  save_output = []

  # Opening JSON file
  try:
    open_positions_file = open("bot_agents.json")
    open_positions_dict = json.load(open_positions_file)
  except:
    return "complete"

  # Guard: Exit if no open positions in file
  if len(open_positions_dict) < 1:
    return "complete"

  # Get all open positions per trading platform
  exchange_pos = await get_open_positions(client)

  # Create live position tickers list
  markets_live = list(exchange_pos.keys())

  # Protect API
  time.sleep(0.5)

  # Check all saved positions match order record
  # Exit trade according to any exit trade rules
  for position in open_positions_dict:

    # Initialize is_close trigger
    is_close = False

    # Extract position matching information from file - market 1
    position_market_m1 = position["market_1"]
    position_size_m1 = position["order_m1_size"]
    position_side_m1 = position["order_m1_side"]

    # Extract position matching information from file - market 2
    position_market_m2 = position["market_2"]
    position_size_m2 = position["order_m2_size"]
    position_side_m2 = position["order_m2_side"]

    # Protect API
    time.sleep(0.5)

    # Get order info m1 per exchange
    order_m1 = await get_order(client, position["order_id_m1"])
    order_market_m1 = order_m1["ticker"]
    order_size_m1 = order_m1["size"]
    order_side_m1 = order_m1["side"]

    # Protect API Rate limits
    time.sleep(0.5)

    # Get order info m2 per exchange
    order_m2 = await get_order(client, position["order_id_m2"])
    order_market_m2 = order_m2["ticker"]
    order_size_m2 = order_m2["size"]
    order_side_m2 = order_m2["side"]

    ## New: Ensure sizes match what was sent to the exchange
    # Override size to match what DYDX exchange has (as it has shown to accept an order and place a different size to what was requested during testing)
    position_size_m1 = order_m1["size"]
    position_size_m2 = order_m2["size"]

    # Perform matching checks
    check_m1 = position_market_m1 == order_market_m1 and position_size_m1 == order_size_m1 and position_side_m1 == order_side_m1
    check_m2 = position_market_m2 == order_market_m2 and position_size_m2 == order_size_m2 and position_side_m2 == order_side_m2
    check_live = position_market_m1 in markets_live and position_market_m2 in markets_live

    # Guard: If not all match exit with error
    if not check_m1 or not check_m2 or not check_live:
      print(f"Warning: Not all open positions match exchange records for {position_market_m1} and {position_market_m2}")
      print(f"This means that the program does not recognise some of the open positions. Please check and close trades for this pair.")
      print(f"Exiting program")
      exit(1)

    # Get prices
    series_1 = await get_candles_recent(client, position_market_m1)
    time.sleep(0.2)
    series_2 = await get_candles_recent(client, position_market_m2)
    time.sleep(0.2)

    # Get markets for reference of tick size
    markets = await get_markets(client)

    # Protect API
    time.sleep(0.2)

    # Trigger close based on Z-Score
    if CLOSE_AT_ZSCORE_CROSS:

      # Initialize z_scores
      hedge_ratio = position["hedge_ratio"]
      z_score_traded = position["z_score"]
      if len(series_1) > 0 and len(series_1) == len(series_2):
        spread = series_1 - (hedge_ratio * series_2)
        z_score_current = calculate_zscore(spread).values.tolist()[-1]

      # Determine trigger
      z_score_level_check = abs(z_score_current) >= abs(z_score_traded)
      z_score_cross_check = (z_score_current < 0 and z_score_traded > 0) or (z_score_current > 0 and z_score_traded < 0)

      # Close trade
      if z_score_level_check and z_score_cross_check:

        # Initiate close trigger
        is_close = True

    ###
    # Add any other close logic you want here
    # Trigger is_close
    ###

    # Close positions if triggered
    if is_close:

      # Determine side - m1
      side_m1 = "SELL"
      if position_side_m1 == "SELL":
        side_m1 = "BUY"

      # Determine side - m2
      side_m2 = "SELL"
      if position_side_m2 == "SELL":
        side_m2 = "BUY"

      # Get and format Price
      price_m1 = float(series_1[-1])
      price_m2 = float(series_2[-1])
      accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
      accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
      tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
      tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
      accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
      accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

      # Close positions
      try:

        # Close position for market 1
        print(">>> Closing market 1 <<<")
        print(f"Closing position for {position_market_m1}")

        (close_order_m1, order_id) = await place_market_order(
          client,
          market=position_market_m1,
          side=side_m1,
          size=position_size_m1,
          price=accept_price_m1,
          reduce_only=True,
        )

        print(close_order_m1["id"])
        print(">>> <<<")

        # Protect API
        time.sleep(1)

        # Close position for market 2
        print(">>> Closing market 2 <<<")
        print(f"Closing position for {position_market_m2}")

        (close_order_m2, order_id) = await place_market_order(
          client,
          market=position_market_m2,
          side=side_m2,
          size=position_size_m2,
          price=accept_price_m2,
          reduce_only=True,
        )

        print(close_order_m2["id"])
        print(">>> <<<")

      except Exception as e:
        print(e)
        print(f"Exit failed for {position_market_m1} with {position_market_m2}")
        save_output.append(position)

    # Keep record if items and save
    else:
      save_output.append(position)

  # Save remaining items
  print(f"{len(save_output)} Items remaining. Saving file...")
  with open("bot_agents.json", "w") as f:
    json.dump(save_output, f)
