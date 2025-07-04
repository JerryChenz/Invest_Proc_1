"""stock_monitor.py - Excel Operations for Stock Monitor

Purpose:
Handles Excel-related operations for the stock monitor system using xlwings.
Manages reading from valuation model files, updating market data, and writing to
monitor files (stock_monitor_INT.xlsx and stock_monitor_CN.xlsx) for two portfolios (INT and CN).

Key Features:
1. Reads opportunity data from valuation models based on portfolio codes.
2. Updates market data (prices, forex rates, yields) in models and monitor files.
3. Writes portfolio data to the Opportunities sheet in monitor files.
4. Supports skip mode to bypass market data updates and avoid unnecessary model saves.
5. Ensures robust error handling for Excel operations.

Dependencies:
- xlwings: For Excel automation.
- pandas: For data manipulation.
- smart_value.data.*: For data positions and utilities.
- smart_value.tools.find_docs: For file path management.
- portfolio_management: For portfolio allocation logic.
"""

import xlwings as xw
from smart_value.data.forex_data import ForexData
from smart_value.data.yq_data import get_price_dict
from smart_value.tools.find_docs import get_model_paths, get_monitor_path
from smart_value.data.model_data import thesis_pos
from smart_value.data.monitor_data import (market_yield_pos, portfolio_mgmt_pos, opportunities_headers)
from smart_value.data.fred_data import get_riskfree_rate, get_us_prime_rate
from smart_value.tools.portfolio_management import update_monitor_data


def update_monitor(skip=True):
    """Update the stock monitor for both INT and CN portfolios.

    Args:
        skip (bool): If True, skips market data updates (yields, prices, forex).

    Steps:
    1. Update market yields and retrieve portfolio assumptions (if not skip).
    2. Process models, update data (if not skip), and collect opportunities by portfolio.
    3. Update each monitor file with portfolio data and allocation weights.
    """
    model_paths = get_model_paths()

    # Step 1: Update market yields and retrieve assumptions
    if not skip:
        print("Connecting...")
        try:
            us_riskfree = get_riskfree_rate("us")
            us_prime = get_us_prime_rate()
        except Exception as e:
            print(f"Error retrieving market yields: {e}")
            us_riskfree = None
            us_prime = None
    else:
        us_riskfree = None
        us_prime = None

    assumptions = {}
    for portfolio_code in ['INT', 'CN']:
        monitor_path = get_monitor_path(portfolio_code)
        assumptions[portfolio_code] = {}
        if not skip:
            try:
                with xw.App(visible=False) as app:
                    monitor_wb = app.books.open(monitor_path)
                    market_yield_sheet = monitor_wb.sheets['Market_Yield']
                    if us_riskfree is not None:
                        market_yield_sheet.range(market_yield_pos["us_riskfree"]).value = us_riskfree
                    if us_prime is not None:
                        market_yield_sheet.range(market_yield_pos["us_prime"]).value = us_prime

                    portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']
                    assumptions[portfolio_code] = {
                        "equity_cost": portfolio_mgmt_sheet.range(portfolio_mgmt_pos["equity_cost"]).value,
                        "target_return": portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value,
                        "entry_yield": portfolio_mgmt_sheet.range(portfolio_mgmt_pos["entry_yield"]).value,
                        "holding_period": portfolio_mgmt_sheet.range(portfolio_mgmt_pos["holding_period"]).value,
                        "benchmark_return": portfolio_mgmt_sheet.range(portfolio_mgmt_pos["benchmark_return"]).value,
                    }
                    monitor_wb.save()
                    monitor_wb.close()
            except Exception as e:
                print(f"Error updating monitor file for {portfolio_code}: {e}")

    # Step 2: Process models and collect opportunities
    forex_data = None
    price_dict = None
    if not skip:
        try:
            forex_data = ForexData()
        except Exception as e:
            print(f"Error retrieving forex data: {e}")
        try:
            price_dict = get_price_dict(model_paths)
        except Exception as e:
            print(f"Error retrieving price dictionary: {e}")

    opportunities_dict = {'INT': [], 'CN': []}
    for model_path in model_paths:
        print(f"Processing {model_path}...")
        with xw.App(visible=False) as app:
            workbook = app.books.open(model_path)
            thesis_sheet = workbook.sheets['Thesis']
            need_save = False

            if not skip:
                # Update market price
                symbol = thesis_sheet.range(thesis_pos['symbol']).value
                if price_dict and symbol in price_dict:
                    thesis_sheet.range(thesis_pos['price']).value = price_dict[symbol]
                    need_save = True

                # Update forex rate
                price_currency = thesis_sheet.range(thesis_pos['price_currency']).value
                report_currency = thesis_sheet.range(thesis_pos['report_currency']).value
                if forex_data:
                    try:
                        fx_rate = forex_data.get_rate(report_currency, price_currency)
                        thesis_sheet.range(thesis_pos['fx_rate']).value = fx_rate
                        need_save = True
                    except Exception as e:
                        print(f"Error getting forex rate for {report_currency}/{price_currency}: {e}")

                # Update assumptions
                portfolio_code = thesis_sheet.range(thesis_pos['portfolio_code']).value
                if portfolio_code in assumptions:
                    for key, pos_key in [("target_return", "target_return"),
                                         ("holding_period", "holding_period"),
                                         ("entry_yield", "entry_yield"),
                                         ("equity_cost", "base_equity_cost"),
                                         ("benchmark_return", "benchmark_return")]:
                        if key in assumptions[portfolio_code]:
                            thesis_sheet.range(thesis_pos[pos_key]).value = assumptions[portfolio_code][key]
                            need_save = True
                else:
                    print(f"Invalid portfolio_code {portfolio_code} in {model_path}")
                    continue

            # Extract opportunity data
            portfolio_code = thesis_sheet.range(thesis_pos['portfolio_code']).value
            if portfolio_code in opportunities_dict:
                opportunity = read_opportunity(thesis_sheet)
                if opportunity:
                    opportunities_dict[portfolio_code].append(opportunity)
            else:
                print(f"Invalid portfolio_code {portfolio_code} in {model_path}")

            if need_save:
                workbook.save()
            workbook.close()

    # Step 3: Update each monitor file
    for portfolio_code in ['INT', 'CN']:
        monitor_path = get_monitor_path(portfolio_code)
        print(f"Updating monitor file for {portfolio_code}...")
        with xw.App(visible=False) as app:
            monitor_wb = app.books.open(monitor_path)
            update_monitor_data(monitor_wb, opportunities_dict[portfolio_code])
            monitor_wb.save()
            monitor_wb.close()
    print("Update completed successfully.")


def read_opportunity(thesis_sheet):
    """Read opportunity data from a model's Thesis sheet.

    Args:
        thesis_sheet (xlwings.Sheet): The Thesis sheet from a valuation model.

    Returns:
        MonitorStock: Object containing extracted opportunity data, or None if invalid.
    """
    try:
        return MonitorStock(thesis_sheet)
    except Exception as e:
        print(f"Error reading opportunity: {e}")
        return None


class MonitorStock:
    """Represents a stock opportunity with data extracted from a valuation model.

    Attributes are dynamically created based on thesis_pos mapping.
    Only includes attributes that exist in both thesis_pos and opportunities_headers.
    """

    def __init__(self, thesis_sheet):
        """Initialize attributes by reading from the Thesis sheet.

        Args:
            thesis_sheet (xlwings.Sheet): The 'Thesis' sheet from a valuation model.
        """
        valid_attrs = set(thesis_pos.keys()) & set(opportunities_headers.keys())
        for attr in valid_attrs:
            try:
                value = thesis_sheet.range(thesis_pos[attr]).value
                setattr(self, attr, value)
            except Exception as e:
                print(f"Warning: Could not set attribute {attr}: {str(e)}")
                setattr(self, attr, None)
