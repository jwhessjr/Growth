"""
This moduleperforms all of the requests for external data sources
"""

import json
from urllib.request import urlopen
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import logging


# Get routines

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

DELAY = 1.0 / 5  # 0.2 seconds between calls


def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


# Read statements from Alpha Vantage


def get_jsonparsed_data(url):
    time.sleep(DELAY)
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


# Get Income Statement
def get_inc_stmnt(company: str, apiKey: str) -> dict:
    """Return annualized ebit, tax expense and interest expense
       from the quarterly reports of a ticker.

    The API returns up to 20 recent quarters; we aggregate them into at most five years.
    """
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=INCOME_STATEMENT&symbol={company}&apikey={apiKey}"
    )
    resp = requests.get(url)
    data = resp.json()

    # The API returns the most recent quarter first.
    quarterly_reports = data.get("quarterlyReports", [])

    if not quarterly_reports:
        raise ValueError(f"No quarterly reports found for {company}")

    # We’ll aggregate at most 5 years (20 quarters).
    max_quarters = min(len(quarterly_reports), 40)
    yearly_data = []

    for i in range(0, max_quarters, 4):  # step by four quarters
        quarter_block = quarterly_reports[i : i + 4]
        if len(quarter_block) < 4:
            break  # incomplete year at the end of the list

        ebit = sum(safe_float(q["ebit"]) for q in quarter_block)
        incomeBeforeTax = sum(safe_float(q["incomeBeforeTax"]) for q in quarter_block)
        tax_exp = sum(safe_float(q["incomeTaxExpense"]) for q in quarter_block)
        int_exp = sum(safe_float(q["interestExpense"]) for q in quarter_block)

        yearly_data.append(
            {
                "ebit": ebit,
                "incomeBeforeTax": incomeBeforeTax,
                "income_tax_expense": tax_exp,
                "interest_expense": int_exp,
            }
        )

    # Build the result dictionary with separate lists
    income_statement = {
        "ebit": [y["ebit"] for y in yearly_data],
        "incomeBeforeTax": [y["incomeBeforeTax"] for y in yearly_data],
        "income_tax_expense": [y["income_tax_expense"] for y in yearly_data],
        "interest_expense": [y["interest_expense"] for y in yearly_data],
    }

    return income_statement


# Function to get the balance sheet and extract the required fields


def get_bal_sheet(company, apiKey):
    url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={company}&apikey={apiKey}"

    data = get_jsonparsed_data(url)
    balSheet = data.get("quarterlyReports", [])
    balSht = {}
    cashAndEquivalents = [
        safe_float(balSheet[0]["cashAndShortTermInvestments"]),
        safe_float(balSheet[4]["cashAndShortTermInvestments"]),
        safe_float(balSheet[8]["cashAndShortTermInvestments"]),
        safe_float(balSheet[12]["cashAndShortTermInvestments"]),
        safe_float(balSheet[16]["cashAndShortTermInvestments"]),
    ]
    currentAssets = [
        safe_float(balSheet[0]["totalCurrentAssets"]),
        safe_float(balSheet[4]["totalCurrentAssets"]),
        safe_float(balSheet[8]["totalCurrentAssets"]),
        safe_float(balSheet[12]["totalCurrentAssets"]),
        safe_float(balSheet[16]["totalCurrentAssets"]),
    ]

    stockholdersEquity = [
        safe_float(balSheet[0]["totalShareholderEquity"]),
        safe_float(balSheet[4]["totalShareholderEquity"]),
        safe_float(balSheet[8]["totalShareholderEquity"]),
        safe_float(balSheet[12]["totalShareholderEquity"]),
        safe_float(balSheet[16]["totalShareholderEquity"]),
    ]
    currentLiabilities = [
        safe_float(balSheet[0]["totalCurrentLiabilities"]),
        safe_float(balSheet[4]["totalCurrentLiabilities"]),
        safe_float(balSheet[8]["totalCurrentLiabilities"]),
        safe_float(balSheet[12]["totalCurrentLiabilities"]),
        safe_float(balSheet[16]["totalCurrentLiabilities"]),
    ]
    currentLongDebt = [
        safe_float(balSheet[0]["currentLongTermDebt"]),
        safe_float(balSheet[4]["currentLongTermDebt"]),
        safe_float(balSheet[8]["currentLongTermDebt"]),
        safe_float(balSheet[12]["currentLongTermDebt"]),
        safe_float(balSheet[16]["currentLongTermDebt"]),
    ]
    shortTermDebt = [
        safe_float(balSheet[0]["shortTermDebt"]),
        safe_float(balSheet[4]["shortTermDebt"]),
        safe_float(balSheet[8]["shortTermDebt"]),
        safe_float(balSheet[12]["shortTermDebt"]),
        safe_float(balSheet[16]["shortTermDebt"]),
    ]
    longTermDebt = [
        safe_float(balSheet[0]["longTermDebt"]),
        safe_float(balSheet[4]["longTermDebt"]),
        safe_float(balSheet[8]["longTermDebt"]),
        safe_float(balSheet[12]["longTermDebt"]),
        safe_float(balSheet[16]["longTermDebt"]),
    ]
    balSht["cash_and_equivalents"] = cashAndEquivalents
    balSht["total_current_assets"] = currentAssets
    # balSht["totalAssets"] = totalAssets
    # balSht["accountsPayable"] = accountsPayable
    balSht["current_long_debt"] = currentLongDebt
    balSht["short_term_debt"] = shortTermDebt
    balSht["long_term_debt"] = longTermDebt
    balSht["total_current_liabilities"] = currentLiabilities
    # balSht["totalLiabilities"] = liabilities
    balSht["total_stockholders_equity"] = stockholdersEquity
    return balSht


# get ERP
def get_erp():
    # URL of the page
    url = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/home.htm"  # Replace with the correct full URL if deeper than homepage

    # Fetch the page
    response = requests.get(url)
    response.raise_for_status()  # Raises an error if the request failed

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the paragraph containing the ERP info
    paragraphs = soup.find_all("p")
    for p in paragraphs:
        if "Implied ERP" in p.get_text():
            text = p.get_text()
            break
    else:
        raise ValueError("Couldn't find the paragraph with Implied ERP")

    # Use regex to extract the first percentage value
    match = re.search(r"(\d+\.\d+)%", text)
    if match:
        implied_erp = safe_float(match.group(1)) / 100
        # print(f"Implied ERP: {implied_erp}%")
        logger.info(f"Implied ERP {implied_erp}")
        return implied_erp
    else:
        # print("Couldn't extract Implied ERP value")
        logger.debug("Couldn't extract ERP %s")
