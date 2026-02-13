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