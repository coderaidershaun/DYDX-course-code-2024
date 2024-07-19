from constants import RESOLUTION
from func_utils import get_ISO_times
import pandas as pd
import numpy as np
import time

from pprint import pprint

# Get relevant time periods for ISO from and to
ISO_TIMES = get_ISO_times()

# Get Recent Candles
async def get_candles_recent(client, market):

  # Define output
  close_prices = []

  # Protect API
  time.sleep(0.2)

  # Get Prices from DYDX V4
  response = await client.indexer.markets.get_perpetual_market_candles(
    market = market, 
    resolution = RESOLUTION
  )

  # Candles
  candles = response

  # Structure data
  for candle in candles["candles"]:
    close_prices.append(candle["close"])

  # Construct and return close price series
  close_prices.reverse()
  prices_result = np.array(close_prices).astype(np.float64)
  return prices_result


# Get Historical Candles
async def get_candles_historical(client, market):

  # Define output
  close_prices = []

  # Extract historical price data for each timeframe
  for timeframe in ISO_TIMES.keys():

    # Confirm times needed
    tf_obj = ISO_TIMES[timeframe]
    from_iso = tf_obj["from_iso"] + ".000Z"
    to_iso = tf_obj["to_iso"] + ".000Z"

    # Protect rate limits
    time.sleep(0.2)

    response = await client.indexer.markets.get_perpetual_market_candles(
      market = market, 
      resolution = RESOLUTION, 
      from_iso = from_iso,
      to_iso = to_iso,
      limit = 100
    )

    candles = response

    # Structure data
    for candle in candles["candles"]:
      close_prices.append({"datetime": candle["startedAt"], market: candle["close"] })

  # Construct and return DataFrame
  close_prices.reverse()
  return close_prices


# Get Markets
async def get_markets(client):
  return await client.indexer.markets.get_perpetual_markets()


# Construct market prices
async def construct_market_prices(client):

  # Ensure only Testnet Assets are used

  # Declare variables
  tradeable_markets = []
  markets = await get_markets(client)

  # Find tradeable pairs
  for market in markets["markets"].keys():
    market_info = markets["markets"][market]
    if market_info["status"] == "ACTIVE":
      tradeable_markets.append(market)

  # Set initial DateFrame
  close_prices = await get_candles_historical(client, tradeable_markets[0])
  df = pd.DataFrame(close_prices)
  df.set_index("datetime", inplace=True)

  # Append other prices to DataFrame
  # You can limit the amount to loop though here to save time in development
  for (i, market) in enumerate(tradeable_markets[0:]):
    print(f"Extracting prices for {i + 1} of {len(tradeable_markets)} tokens for {market}")
    close_prices_add = await get_candles_historical(client, market)
    df_add = pd.DataFrame(close_prices_add)
    try:
      df_add.set_index("datetime", inplace=True)
      df = pd.merge(df, df_add, how="outer", on="datetime", copy=False)
      # print(df.head())
    except Exception as e: 
      print(f"Failed to add {market} - {e}")
    del df_add

  # Check any columns with NaNs
  nans = df.columns[df.isna().any()].tolist()
  if len(nans) > 0:
    print("Dropping columns: ")
    print(nans)
    df.drop(columns=nans, inplace=True)

  # Return result
  return df
