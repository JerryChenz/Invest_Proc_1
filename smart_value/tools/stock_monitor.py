import xlwings as xw
import re
from smart_value.data.forex_data import ForexData
from smart_value.data.yq_data import get_price_dict
from smart_value.tools.find_docs import stock_monitor_file_path, get_model_paths
from smart_value.data.model_data import thesis_pos
from smart_value.data.monitor_data import (market_yield_pos, portfolio_mgmt_pos, opportunities_headers,
                                           opportunities_start_row)
from smart_value.data.fred_data import get_riskfree_rate, get_us_prime_rate

"""
Task: Summarize valuation results from multiple Excel models into a monitor file using Python and xlwings.

Coding Approach:
1. Read Model Paths and Initialize Data: Retrieve paths to all Excel valuation models and initialize dictionaries for 
forex rates and stock prices if updates are required.
2. Update the and market yield data if not in quick mode.
3. Process Each Model: For each model, read the necessary data, update market price, and forex rate if not in quick 
mode, and extract relevant information using a helper class.
4. Update Monitor File: Write the extracted data into the monitor file using, ensuring correct column mappings and 
handling formula cells appropriately.

Note: Ensure correct data mapping between cell positions in Excel sheets and attribute names in the helper class to 
avoid discrepancies.
"""


def update_monitor(skip=True):
    """The main function to update the stock monitor

    Args:
        skip (bool): Whether to skip updating market yields, prices, etc. Defaults to True.

    Process:
        1. Retrieve paths to all Excel valuation models
        2. If not in skip mode, update market yield data
        3. Process each model to extract opportunity data
        4. Update the monitor file with the extracted data
    """
    model_paths = get_model_paths()

    # Update market yield (proceed even if it fails)
    if not skip:
        try:
            update_market_data(stock_monitor_file_path, model_paths)
        except Exception as e:
            print(f"Skipping market yield update due to error: {e}")

    # Read opportunities from all models
    opportunities = []
    for model_path in model_paths:
        print(f"Processing {model_path}...")
        opportunity = read_opportunity(model_path)
        if opportunity:
            opportunities.append(opportunity)

    # Update monitor file
    print("Updating monitor file...")
    with xw.App(visible=False) as app:
        monitor_wb = app.books.open(stock_monitor_file_path)
        update_opportunities(monitor_wb, opportunities)
        monitor_wb.save()
        monitor_wb.close()
    print("Update completed successfully.")


def read_opportunity(model_path):
    """Read opportunity data from a model file

    Args:
        model_path (str): Path to the model file

    Returns:
        MonitorStock: Object containing extracted opportunity data, or None if not a stock model
    """
    opportunity = None
    is_stock_model = re.compile(r".*Valuation.*").match(str(model_path))

    if is_stock_model:
        with xw.App(visible=False) as app:
            workbook = app.books.open(model_path)
            thesis_sheet = workbook.sheets['Thesis']
            opportunity = MonitorStock(thesis_sheet)
            workbook.close()
    return opportunity


def update_opportunities(monitor_workbook, opportunities):
    """Write the extracted opportunities data into the monitor workbook.

    Uses the opportunities_headers mapping to determine column positions.
    Clears existing data before writing new opportunities.
    Sets formulas for margin of safety and price alert columns.

    Args:
        monitor_workbook (xlwings.Book): The target monitor workbook.
        opportunities (list): List of MonitorStock objects to write.
    """
    sheet = monitor_workbook.sheets['Opportunities']
    start_row = opportunities_start_row

    # Clear existing data (with buffer for potential additions)
    last_row = start_row + len(opportunities) + 30
    sheet.range(f"B{start_row}:P{last_row}").clear_contents()

    # Write each opportunity's data
    for row_idx, opportunity in enumerate(opportunities, start=start_row):
        # Write all attributes using opportunities_headers mapping
        for attr, col in opportunities_headers.items():
            if hasattr(opportunity, attr):  # Only write if attribute exists
                sheet.range(f"{col}{row_idx}").value = getattr(opportunity, attr)

        # Set formulas for calculated columns
        sheet.range(f"I{row_idx}").formula = f'=IFERROR(1-G{row_idx}/H{row_idx}, "nm")'  # Margin of safety
        sheet.range(f"O{row_idx}").formula = f'=IFERROR(D{row_idx}/G{row_idx}-1, "nm")'  # Price alert

    print(f"Successfully updated {len(opportunities)} opportunities.")


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
        # Get all attributes that exist in both thesis_pos and opportunities_headers
        valid_attrs = set(thesis_pos.keys()) & set(opportunities_headers.keys())

        for attr in valid_attrs:
            try:
                value = thesis_sheet.range(thesis_pos[attr]).value
                setattr(self, attr, value)
            except Exception as e:
                print(f"Warning: Could not set attribute {attr}: {str(e)}")
                setattr(self, attr, None)


def update_market_data(monitor_path, model_paths):
    """Update market data in stock monitor, and update market price, forex rate, and market yield assumptions in the
    models.

    Args:
        monitor_path (str): Path to the stock monitor file
        model_paths (list): List of paths to valuation model files
    """

    print("Updating market yields...")
    try:
        us_riskfree = get_riskfree_rate("us")
        us_prime = get_us_prime_rate()

        with xw.App(visible=False) as app:
            monitor_wb = app.books.open(monitor_path)
            # Update the market yields
            market_yield_sheet = monitor_wb.sheets['Market_Yield']
            market_yield_sheet.range(market_yield_pos["us_riskfree"]).value = us_riskfree
            market_yield_sheet.range(market_yield_pos["us_prime"]).value = us_prime
            # Retrieve the model assumptions
            portfolio_mgmt_sheet = monitor_wb.sheets['Portfolio_Mgmt']
            equity_cost = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["equity_cost"]).value
            target_return = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["target_return"]).value
            holding_period = portfolio_mgmt_sheet.range(portfolio_mgmt_pos["holding_period"]).value
            monitor_wb.save()
            monitor_wb.close()
        print("Market yields updated successfully.")
    except Exception as e:
        print(f"Error updating Market yields: {e}")

    # Retrieve the Forex rates and the market prices
    forex_data = ForexData()
    price_dict = get_price_dict(model_paths)

    # Update each model's market data and model assumptions
    for path in model_paths:
        try:
            model_wb = app.books.open(path)
            thesis_sheet = model_wb.sheets['Thesis']

            # Update market data
            symbol = thesis_sheet.range(thesis_pos['symbol']).value
            if symbol in price_dict:
                thesis_sheet.range(thesis_pos['price']).value = price_dict[symbol]

            # Update forex rate
            price_currency = thesis_sheet.range(thesis_pos['price_currency']).value
            report_currency = thesis_sheet.range(thesis_pos['report_currency']).value
            if forex_data:
                fx_rate = forex_data.get_rate(report_currency, price_currency)
                thesis_sheet.range(thesis_pos['fx_rate']).value = fx_rate

            # Update market yield assumptions
            thesis_sheet.range(thesis_pos["target_return"]).value = target_return
            thesis_sheet.range(thesis_pos["holding_period"]).value = holding_period
            thesis_sheet.range(thesis_pos["base_equity_cost"]).value = equity_cost

            model_wb.save()
            model_wb.close()
            print(f"Updated {path}")
        except Exception as e:
            print(f"Error updating {path}: {e}")
