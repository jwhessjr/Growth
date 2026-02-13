"""
This moduleperforms all of the requests for external data sources
"""

import json
from urllib.request import urlopen
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import logging


# Get routines 
