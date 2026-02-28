"""
Growth Stock Screener
"""

from dataclasses import dataclass
from datetime import date
import sqlite3
import hg_gs_lib
import logging

# Get the Risk Free Rate and the ERP
# Add them together to create the hurdle rate

# Get the financials for the last 40 quarters (10 years)
# Revenue, EBIT
# Debt, Equity
# EPS, P/E ratio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the overall logger level

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create a stream handler for the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)  # only show INFO and above on console
stream_handler.setFormatter(formatter)

# Create a FileHandler for the log file
file_handler = logging.FileHandler("data/value.log")
file_handler.setLevel(logging.DEBUG)  # log all messages to the file
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# Set up COBSTANTS
with open("/Users/jhess/Development/Alpha2/data/fred_api.txt") as f:
    FRED_KEY = f.readline()
EQ_PREM = hg_gs_lib.get_erp()
RISK_FREE = hg_gs_lib.get_risk_free(FRED_KEY)
HURDLE_RATE = EQ_PREM + RISK_FREE
