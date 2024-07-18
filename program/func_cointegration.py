import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from scipy.stats import linregress
from constants import MAX_HALF_LIFE, WINDOW

class SmartError(Exception):
  pass

def half_life_mean_reversion(series):
  if len(series) <= 1:
    raise SmartError("Series length must be greater than 1.")
  difference = np.diff(series)
  lagged_series = series[:-1]
  slope, _, _, _, _ = linregress(lagged_series, difference)
  if np.abs(slope) < np.finfo(np.float64).eps:
    raise SmartError("Cannot calculate half life. Slope value is too close to zero.")
  half_life = -np.log(2) / slope
  return half_life


# Calculate ZScore
def calculate_zscore(spread):
  spread_series = pd.Series(spread)
  mean = spread_series.rolling(center=False, window=WINDOW).mean()
  std = spread_series.rolling(center=False, window=WINDOW).std()
  x = spread_series.rolling(center=False, window=1).mean()
  zscore = (x - mean) / std
  return zscore


# Calculate Cointegration
def calculate_cointegration(series_1, series_2):
  series_1 = np.array(series_1).astype(np.float64)
  series_2 = np.array(series_2).astype(np.float64)
  coint_flag = 0
  coint_res = coint(series_1, series_2)
  coint_t = coint_res[0]
  p_value = coint_res[1]
  critical_value = coint_res[2][1]

  # Better way to fit data vs older version
  series_2_with_constant = sm.add_constant(series_2) 
  model = sm.OLS(series_1, series_2_with_constant).fit()
  hedge_ratio = model.params[1]
  intercept = model.params[0]

  spread = series_1 - (series_2 * hedge_ratio) - intercept
  half_life = half_life_mean_reversion(spread)
  t_check = coint_t < critical_value
  coint_flag = 1 if p_value < 0.05 and t_check else 0
  return coint_flag, hedge_ratio, half_life


# Store Cointegration Results
def store_cointegration_results(df_market_prices):

  # Initialize
  markets = df_market_prices.columns.to_list()
  criteria_met_pairs = []

  # Find cointegrated pairs
  # Start with our base pair
  for index, base_market in enumerate(markets[:-1]):
    series_1 = df_market_prices[base_market].values.astype(np.float64).tolist()

    # Get Quote Pair
    for quote_market in markets[index +1:]:
      series_2 = df_market_prices[quote_market].values.astype(np.float64).tolist()

      # Check cointegration
      coint_flag, hedge_ratio, half_life = calculate_cointegration(series_1, series_2)

      # Log pair
      if coint_flag == 1 and half_life <= MAX_HALF_LIFE and half_life > 0:
        criteria_met_pairs.append({
          "base_market": base_market,
          "quote_market": quote_market,
          "hedge_ratio": hedge_ratio,
          "half_life": half_life,
        })

  # Create and save DataFrame
  df_criteria_met = pd.DataFrame(criteria_met_pairs)
  df_criteria_met.to_csv("cointegrated_pairs.csv")
  del df_criteria_met

  # Return result
  print("Cointegrated pairs successfully saved")
  return "saved"






