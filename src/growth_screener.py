"""
Growth Stock Screener
"""

from dataclasses import dataclass
from datetime import date
import sqlite3
import hg_dcflib
import logging

# Get the Risk Free Rate and the ERP
# Add them together to create the hurdle rate