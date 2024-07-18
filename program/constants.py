# from dydx3.constants import API_HOST_MAINNET, API_HOST_GOERLI
from decouple import config

# !!!! SELECT MODE !!!!
MODE = "DEVELOPMENT"

# Close all open positions and orders
ABORT_ALL_POSITIONS = True

# Find Cointegrated Pairs
FIND_COINTEGRATED = True

# Manage Exits
MANAGE_EXITS = True

# Place Trades
PLACE_TRADES = True

# Resolution
RESOLUTION = "1HOUR"

# Stats Window
WINDOW = 21

# Thresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5
USD_PER_TRADE = 100
USD_MIN_COLLATERAL = 1880

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True

DYDX_ADDRESS = config("DYDX_ADDRESS")
SECRET_PHRASE = config("SECRET_PHRASE")
MNEMONIC = (SECRET_PHRASE)
TELEGRAM_TOKEN = config("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = config("TELEGRAM_CHAT_ID")
